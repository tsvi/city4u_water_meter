# Municipality Verification Script

Automated tool to verify which municipalities support water consumption data using headless browser automation.

## Prerequisites

```bash
# Install Playwright
pdm add -d playwright

# Install Chromium browser
pdm run playwright install chromium
```

## Quick Start

```bash
cd /home/tsvi/projects/read_water
pdm run python3 scripts/update_municipalities.py
```

## What It Does

1. Fetches all municipalities from City4U API
2. Uses Playwright (headless browser) to check each municipality's portal page
3. Waits for Angular/JavaScript to load the dynamic menu
4. Checks for water consumption menu items
5. Extracts municipality logo URLs from portal pages
6. Downloads municipality logos to `custom_components/city4u/logos/`
7. Updates `custom_components/city4u/municipalities.py` with verified results and logo paths
8. Creates `SUPPORTED_MUNICIPALITIES.md` with complete list

## Why Playwright?

City4U portal pages use Angular to dynamically load menu items via JavaScript. The water consumption menu is NOT in the initial HTML - it only appears after JavaScript execution IF the municipality supports water service. Playwright allows us to:

- Execute JavaScript in a real browser
- Wait for Angular to fully render
- Inspect the actual DOM that users see

## Verification Method

The script checks each municipality's portal page for:
1. Water menu section: "מים" (Water)
2. Water consumption link: "צריכת המים שלי" (My water consumption)

Both must be present for verification ✓

## Features

- **Browser Automation**: Uses Playwright to execute JavaScript
- **Logo Download**: Automatically extracts and downloads municipality logos
- **Proxy Auto-Detection**: Uses `http_proxy`/`https_proxy` environment variables
- **Rate Limiting**: Configurable delay between requests (default 0.1s)
- **Progress Display**: Color-coded real-time results
- **Interrupt Handling**: Save partial results with Ctrl+C
- **Direct Update**: Automatically updates Python and Markdown files

## Output Files

- `custom_components/city4u/municipalities.py` - Python module with verified municipalities and logo paths
- `custom_components/city4u/logos/*.jpg` - Downloaded municipality logo files
- `SUPPORTED_MUNICIPALITIES.md` - Markdown documentation of supported municipalities

## Troubleshooting

### Playwright Not Installed

If you see errors about Playwright not being installed:
```bash
pdm add -d playwright
pdm run playwright install chromium
```

### Proxy Issues

The script automatically detects proxy settings from environment variables. If you're behind a corporate proxy and seeing errors, the proxy might be interfering with the checks.

### Slow Performance

Checking all 238 municipalities takes time because each requires:
- Loading a full page
- Waiting for JavaScript to execute
- Inspecting the DOM

You can interrupt (Ctrl+C) at any time and save partial results.
