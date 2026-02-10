#!/usr/bin/env python3
"""
Update municipalities.py with verified water consumption municipalities.

This script uses Playwright to automate browser verification since City4U portal
pages use Angular/JavaScript to dynamically load menu items.

Prerequisites:
    pdm add -d playwright
    pdm run playwright install chromium

This script:
1. Fetches all municipalities from City4U API
2. Uses headless browser to check each for water consumption menu
3. Updates municipalities.py with verified list

Usage:
    python3 scripts/update_municipalities.py

Environment variables:
    http_proxy, https_proxy - Proxy configuration (automatically detected)
"""

import asyncio
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import aiohttp
from playwright.async_api import Browser, Page, async_playwright

type MunicipalityData = dict[str, str | int]


class MunicipalityVerifier:
    """Verify which municipalities support water consumption."""

    def __init__(self) -> None:
        self.verified_municipalities: list[MunicipalityData] = []
        self.total_checked: int = 0
        self.browser: Browser | None = None

        # Detect proxy settings
        self.http_proxy = os.environ.get("http_proxy") or os.environ.get("HTTP_PROXY")
        self.https_proxy = os.environ.get("https_proxy") or os.environ.get(
            "HTTPS_PROXY"
        )

        if self.http_proxy or self.https_proxy:
            print("📡 Using proxy configuration:")
            if self.http_proxy:
                print(f"   http_proxy: {self.http_proxy}")
            if self.https_proxy:
                print(f"   https_proxy: {self.https_proxy}")
            print()

    async def fetch_all_municipalities(self) -> list[MunicipalityData]:
        """Fetch all municipalities from City4U API."""
        url = "https://city4u.co.il/WebApi_portal/v1/Customers/Customer/allcustomers"

        print("Fetching all municipalities from City4U API...")

        # Use aiohttp for API calls
        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            try:
                async with session.get(
                    url, proxy=self.https_proxy, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        municipalities: list[MunicipalityData] = await response.json()
                        print(f"✓ Loaded {len(municipalities)} municipalities\n")
                        return municipalities
                    print(f"✗ HTTP {response.status}")
                    return []
            except aiohttp.ClientError as exc:
                print(f"✗ Error fetching municipalities: {exc}")
                return []

    async def check_municipality_has_water(
        self, page: Page, customer_id: int
    ) -> tuple[bool, str, str | None]:
        """
        Check if a municipality has water consumption support using browser automation.

        Returns:
            tuple: (has_water, error_message, logo_url)
        """
        url = f"https://city4u.co.il/PortalServicesSite/_portal/{customer_id}"

        try:
            # Navigate to the portal page
            response = await page.goto(url, wait_until="networkidle", timeout=30000)

            if response is None or response.status != 200:
                status = response.status if response else "No response"
                return False, f"HTTP {status}", None

            # Wait for Angular to fully load
            await page.wait_for_timeout(2000)

            # Check for water menu items by looking in the HTML content
            # This is more reliable than query_selector for dynamically loaded content
            content = await page.content()

            has_water_section = "מים" in content
            has_water_consumption = "צריכת המים שלי" in content

            has_water = has_water_section and has_water_consumption

            # Extract municipality logo from the page
            # Only match logos under PortalServicesSite (others are auto-generated)
            logo_url = None
            logo_pattern = (
                r'<img[^>]*src="(/PortalServicesSite/'
                r'images/_logos/logo_\d+\.[a-z]+)(?:\?[^"]*)?\"'
            )
            logo_match = re.search(logo_pattern, content, re.DOTALL)
            if logo_match:
                logo_url = logo_match.group(1).lstrip("/")  # Remove leading slash

            if has_water:
                return True, "", logo_url
            if has_water_section:
                return False, "No consumption", logo_url
            return False, "No water menu", logo_url

        except asyncio.TimeoutError:
            return False, "Timeout", None
        except (RuntimeError, ValueError) as exc:
            error_msg = str(exc)[:30]
            return False, f"Error: {error_msg}", None

    async def download_logo(
        self, session: aiohttp.ClientSession, logo_path: str, customer_id: int
    ) -> str | None:
        """
        Download municipality logo and save it locally.
        Skips auto-generated logos (only downloads from PortalServicesSite).

        Args:
            session: aiohttp session
            logo_path: Relative path like "PortalServicesSite/images/_logos/logo_115.jpg"
            customer_id: Municipality customer ID

        Returns:
            Relative path to saved logo file, or None if download failed
        """
        if not logo_path:
            return None

        try:
            # Build full URL - logo_path already contains PortalServicesSite/
            url = f"https://city4u.co.il/{logo_path}"

            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 404:
                    # Logo doesn't exist, skip it
                    return None
                if response.status != 200:
                    return None

                data = await response.read()
                # Validate it's actually an image, not an HTML error page
                if not (
                    data[:4] == b"\x89PNG"
                    or data[:3] == b"GIF"
                    or data[:2] == b"\xff\xd8"
                ):
                    return None

                # Detect actual file type from content
                if data[:4] == b"\x89PNG":
                    ext = "png"
                elif data[:3] == b"GIF":
                    ext = "gif"
                elif data[:2] == b"\xff\xd8":
                    ext = "jpg"
                else:
                    ext = "jpg"

                # Save to custom_components/city4u/logos/
                logos_dir = (
                    Path(__file__).parent.parent
                    / "custom_components"
                    / "city4u"
                    / "logos"
                )
                logos_dir.mkdir(parents=True, exist_ok=True)

                logo_file = f"{customer_id}.{ext}"
                logo_path_local = logos_dir / logo_file

                logo_path_local.write_bytes(data)
                print(f"    Downloaded logo: {logo_file} ({len(data):,} bytes)")

                # Return relative path from custom_components/city4u/
                return f"logos/{logo_file}"

        except (aiohttp.ClientError, OSError):
            # Silently skip logo download errors
            return None

    async def verify_all_municipalities(  # pylint: disable=too-many-locals
        self, delay: float = 0.1
    ) -> list[MunicipalityData]:
        """
        Verify all municipalities for water consumption support.

        Args:
            delay: Delay in seconds between requests (default 0.1)

        Returns:
            List of municipalities with water support
        """
        municipalities = await self.fetch_all_municipalities()
        if not municipalities:
            return []

        total = len(municipalities)

        print(f"Checking {total} municipalities for water consumption support...")
        print(f"Delay between requests: {delay} seconds")
        print("Using headless browser automation (Playwright)\n")
        print(f"{'ID':<10} {'Name (Hebrew)':<40} {'Status':<15}")
        print("=" * 70)

        # Create a new page for checking
        assert self.browser is not None, "Browser not initialized"
        page = await self.browser.new_page()

        # Create session for logo downloads
        connector = aiohttp.TCPConnector(ssl=False)

        try:
            async with aiohttp.ClientSession(
                connector=connector, trust_env=True
            ) as session:
                for idx, muni in enumerate(municipalities, 1):
                    customer_id = muni.get("CUSTOMER_ID")
                    name_he = muni.get("CUSTOMER_NAME_HE", "")

                    # Convert to int if it's a float (API sometimes returns floats)
                    if isinstance(customer_id, float):
                        customer_id = int(customer_id)

                    if not isinstance(customer_id, int):
                        print(f"⚠️  Skipping invalid customer_id: {customer_id}")
                        continue

                    (
                        has_water,
                        error,
                        logo_url,
                    ) = await self.check_municipality_has_water(page, customer_id)

                    if has_water:
                        status = "✓ YES"

                        # Download logo if available
                        logo_path = None
                        if logo_url:
                            logo_path = await self.download_logo(
                                session, logo_url, customer_id
                            )

                        self.verified_municipalities.append(
                            {
                                "customer_id": customer_id,
                                "name_he": name_he,
                                "logo_url": logo_path,
                            }
                        )
                        # Highlight water-supported municipalities
                        print(
                            f"\033[92m{customer_id:<10} "
                            f"{name_he:<40} {status:<15}\033[0m"
                        )
                    else:
                        status = "✗ NO" if not error else f"✗ {error[:10]}"
                        print(f"{customer_id:<10} {name_he:<40} {status:<15}")

                    self.total_checked += 1

                    # Progress indicator
                    if idx % 20 == 0:
                        water_count = len(self.verified_municipalities)
                        print(
                            f"\n--- Progress: {idx}/{total} "
                            f"({water_count} with water) ---\n"
                        )

                    # Delay between requests
                    if idx < total:
                        await asyncio.sleep(delay)

        finally:
            await page.close()

        print("\n" + "=" * 70)
        print("\nVerification complete!")
        print(f"Total municipalities: {total}")
        print(f"With water consumption: {len(self.verified_municipalities)}")

        return self.verified_municipalities

    async def run(self, delay: float = 0.1) -> list[MunicipalityData]:
        """Run the verification process."""
        async with async_playwright() as p:
            # Launch browser with proxy if configured
            launch_options = {"headless": True}
            if self.http_proxy or self.https_proxy:
                proxy_url = self.https_proxy or self.http_proxy
                launch_options["proxy"] = {"server": proxy_url}

            self.browser = await p.chromium.launch(**launch_options)

            try:
                verified = await self.verify_all_municipalities(delay)
                return verified
            finally:
                await self.browser.close()


def generate_municipalities_py(verified_municipalities: list[MunicipalityData]) -> str:
    """Generate the content for municipalities.py"""

    # Sort by Hebrew name
    water_munis_sorted = sorted(verified_municipalities, key=lambda x: x["name_he"])

    # Generate enum values
    enum_lines = []
    for muni in water_munis_sorted:
        cid = muni["customer_id"]
        name_he = muni["name_he"]
        enum_lines.append(f"    ID_{cid} = {cid}  # {name_he}")

    # Generate Municipality instances
    muni_lines = []
    for muni in water_munis_sorted:
        muni_lines.append("    Municipality(")
        muni_lines.append(f"        customer_id=City4uID.ID_{muni['customer_id']},")

        muni_lines.append(f'        name_he="{muni["name_he"]}",')
        # Add logo_url if available
        logo_url = muni.get("logo_url")
        if logo_url:
            muni_lines.append(f'        logo_url="{logo_url}",')
        muni_lines.append("    ),")

    enum_section = "\n".join(enum_lines)
    muni_section = "\n".join(muni_lines)
    verification_date = datetime.now().strftime("%Y-%m-%d")

    # pylint: disable=duplicate-code
    content_template = '''"""Municipality data for City4U integration.

This list contains municipalities verified to have water consumption support.
Verification checks for water menu in the portal page.

To update this list, run:
    python3 scripts/update_municipalities.py

Last updated: {verification_date}
Total municipalities: {total_count}
"""

from dataclasses import dataclass
from enum import IntEnum


class City4uID(IntEnum):
    """City4U customer IDs for municipalities with water consumption support."""

{enum_section}


@dataclass
class Municipality:
    """Represents a municipality in the City4U system."""

    customer_id: City4uID
    name_he: str
    logo_url: str | None = None


# Verified municipalities with water consumption support
MUNICIPALITIES = [
{muni_section}
]


# Sorted lists for UI display
MUNICIPALITIES_SORTED_HE = sorted(MUNICIPALITIES, key=lambda m: m.name_he)


def get_municipality_by_id(customer_id: int) -> Municipality | None:
    """Get municipality by customer ID."""
    for muni in MUNICIPALITIES:
        if muni.customer_id == customer_id:
            return muni
    return None


def get_municipality_name(customer_id: int) -> str:
    """Get municipality name by customer ID."""
    muni = get_municipality_by_id(customer_id)
    if muni:
        return muni.name_he
    return f"Unknown ({{customer_id}})"
'''

    content = content_template.format(
        verification_date=verification_date,
        total_count=len(verified_municipalities),
        enum_section=enum_section,
        muni_section=muni_section,
    )

    return content


def generate_supported_municipalities_md(
    verified_municipalities: list[MunicipalityData],
) -> str:
    """Generate markdown file listing supported municipalities."""
    verification_date = datetime.now().strftime("%Y-%m-%d")
    sorted_munis = sorted(verified_municipalities, key=lambda x: x["name_he"])

    content = f"""# Supported Municipalities

This integration supports **{len(verified_municipalities)} municipalities** \
with verified water consumption data.

Last updated: {verification_date}

## Municipality List

| Customer ID | Hebrew Name |
|------------|-------------|
"""

    for muni in sorted_munis:
        content += f"| {muni['customer_id']} | {muni['name_he']} |\n"

    content += """

## Verification Method

Municipalities are verified to have water consumption support by checking:
1. Portal page at
   `https://city4u.co.il/PortalServicesSite/_portal/{{CUSTOMER_ID}}`
2. Presence of water menu (מים) under personal area (איזור אישי)
3. Presence of "צריכת המים שלי" (My water consumption) menu item

## Updating This List

This file is automatically generated by:
```bash
python3 scripts/update_municipalities.py
```
"""

    return content


def update_municipalities_file(
    verified_municipalities: list[dict[str, str | int]],
) -> None:
    """Update municipalities.py and SUPPORTED_MUNICIPALITIES.md with verified data."""
    # Update municipalities.py
    py_content = generate_municipalities_py(verified_municipalities)
    py_path = Path("custom_components/city4u/municipalities.py")
    py_path.write_text(py_content, encoding="utf-8")
    print(f"\n✓ Updated {py_path}")

    # Update SUPPORTED_MUNICIPALITIES.md
    md_content = generate_supported_municipalities_md(verified_municipalities)
    md_path = Path("SUPPORTED_MUNICIPALITIES.md")
    md_path.write_text(md_content, encoding="utf-8")
    print(f"✓ Updated {md_path}")

    print(f"\nVerified municipalities ({len(verified_municipalities)}):")
    for muni in sorted(verified_municipalities, key=lambda x: x["name_he"]):
        print(f"  {muni['customer_id']:<10} {muni['name_he']}")


async def main() -> None:
    """Main execution function."""
    print("=" * 70)
    print("City4U Municipality Verification and Update Tool")
    print("=" * 70)
    print()

    verifier = MunicipalityVerifier()

    try:
        verified = await verifier.run(delay=0.1)

        if verified:
            update_municipalities_file(verified)
            num_verified = len(verified)
            print(
                f"\n✅ Success! Updated municipalities files "
                f"with {num_verified} verified municipalities"
            )
        else:
            print("\n❌ No municipalities with water consumption found.")
            print("This might indicate a connection issue or API change.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        if verifier.verified_municipalities:
            num_partial = len(verifier.verified_municipalities)
            print(f"\nPartially verified {num_partial} municipalities so far.")
            response = input("Update municipalities.py with partial results? [y/N]: ")
            if response.lower() == "y":
                update_municipalities_file(verifier.verified_municipalities)
                print("✓ Partial results saved")
        sys.exit(130)
    except (RuntimeError, OSError) as exc:
        print(f"\n❌ Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
