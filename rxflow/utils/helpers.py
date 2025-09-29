"""
Helper utilities for RxFlow Pharmacy Assistant
"""

import re
from typing import Dict, Optional, Tuple

from geopy.distance import geodesic


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in miles"""
    return float(geodesic((lat1, lon1), (lat2, lon2)).miles)


def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:.2f}"


def parse_medication_string(medication_input: str) -> Dict[str, Optional[str]]:
    """
    Parse medication string to extract components
    Examples:
    - "lisinopril 10mg" -> {"name": "lisinopril", "strength": "10mg", "form": None}
    - "metformin 500mg tablets" -> {"name": "metformin", "strength": "500mg", "form": "tablets"}
    """
    medication_input = medication_input.lower().strip()

    # Pattern to match medication name, strength, and form
    pattern = r"^(\w+)\s*(\d+(?:\.\d+)?(?:mg|mcg|g|ml|units?)?)?\s*(\w+)?$"
    match = re.match(pattern, medication_input)

    if match:
        name, strength, form = match.groups()
        return {
            "name": name.strip() if name else None,
            "strength": strength.strip() if strength else None,
            "form": form.strip()
            if form and form not in ["mg", "mcg", "g", "ml", "unit", "units"]
            else None,
        }

    # Fallback: just extract the first word as medication name
    words = medication_input.split()
    return {"name": words[0] if words else None, "strength": None, "form": None}


def extract_numeric_value(text: str) -> Optional[float]:
    """Extract numeric value from text string"""
    pattern = r"(\d+(?:\.\d+)?)"
    match = re.search(pattern, text)
    return float(match.group(1)) if match else None


def normalize_drug_name(drug_name: str) -> str:
    """Normalize drug name for consistent matching"""
    return drug_name.lower().strip().replace("-", "").replace(" ", "")
