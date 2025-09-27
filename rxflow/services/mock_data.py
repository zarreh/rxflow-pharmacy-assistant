"""Mock data for demo purposes"""

MEDICATIONS_DB = {
    "lisinopril": {
        "generic_name": "lisinopril",
        "brand_names": ["Prinivil", "Zestril"],
        "common_dosages": ["5mg", "10mg", "20mg", "40mg"],
        "requires_pa": False,
        "drug_class": "ACE inhibitor"
    },
    "eliquis": {
        "generic_name": "apixaban",
        "brand_names": ["Eliquis"],
        "common_dosages": ["2.5mg", "5mg"],
        "requires_pa": True,
        "drug_class": "anticoagulant"
    },
    "metformin": {
        "generic_name": "metformin",
        "brand_names": ["Glucophage", "Fortamet"],
        "common_dosages": ["500mg", "850mg", "1000mg"],
        "requires_pa": False,
        "drug_class": "antidiabetic"
    }
}

PHARMACY_INVENTORY = {
    "cvs_main": {
        "name": "CVS Main Street",
        "address": "123 Main St",
        "distance_miles": 0.5,
        "wait_time_min": 30,
        "in_stock": ["lisinopril", "metformin", "atorvastatin"],
        "prices": {
            "lisinopril_10mg_30": 15.99,
            "metformin_500mg_60": 8.99
        }
    },
    "walmart_plaza": {
        "name": "Walmart Pharmacy",
        "address": "456 Plaza Dr",
        "distance_miles": 3.2,
        "wait_time_min": 15,
        "in_stock": ["lisinopril", "metformin", "eliquis"],
        "prices": {
            "lisinopril_10mg_30": 4.00,
            "metformin_500mg_60": 4.00
        }
    }
}

# Mock API responses
MOCK_API_RESPONSES = {
    "check_prior_auth": {
        "lisinopril": {"required": False, "reason": None},
        "eliquis": {"required": True, "reason": "High-cost medication", "criteria": "Documented AFib or DVT/PE"}
    }
}
