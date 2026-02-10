"""Municipality data for City4U integration.

This list contains municipalities verified to have water consumption support.
Verification checks for water menu in the portal page.

To update this list, run:
    python3 scripts/update_municipalities.py

Last updated: 2026-02-10
Total municipalities: 2
"""

from dataclasses import dataclass
from enum import IntEnum


class City4uID(IntEnum):
    """City4U customer IDs for municipalities with water consumption support."""

    ID_812100 = 812100  # מי מודיעין
    ID_712680 = 712680  # מיתר


@dataclass
class Municipality:
    """Represents a municipality in the City4U system."""

    customer_id: City4uID
    name_he: str
    logo_url: str | None = None


# Verified municipalities with water consumption support
MUNICIPALITIES = [
    Municipality(
        customer_id=City4uID.ID_812100,
        name_he="מי מודיעין",
        logo_url="logos/812100.gif",
    ),
    Municipality(
        customer_id=City4uID.ID_712680,
        name_he="מיתר",
        logo_url="logos/712680.png",
    ),
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
    return f"Unknown ({customer_id})"
