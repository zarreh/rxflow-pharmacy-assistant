"""Comprehensive mock data for pharmacy refill assistant demo"""

# Expanded medication database with RxCUI codes and detailed information
MEDICATIONS_DB = {
    "lisinopril": {
        "rxcui": "29046",
        "generic_name": "lisinopril",
        "brand_names": ["Prinivil", "Zestril"],
        "common_dosages": ["5mg", "10mg", "20mg", "40mg"],
        "requires_pa": False,
        "drug_class": "ACE inhibitor",
        "indication": "Hypertension, heart failure",
        "common_interactions": ["ibuprofen", "potassium supplements", "lithium"],
        "contraindications": ["pregnancy", "angioedema history"],
        "typical_supply_days": [30, 90]
    },
    "eliquis": {
        "rxcui": "1364430",
        "generic_name": "apixaban",
        "brand_names": ["Eliquis"],
        "common_dosages": ["2.5mg", "5mg"],
        "requires_pa": True,
        "drug_class": "anticoagulant",
        "indication": "Atrial fibrillation, DVT/PE prevention",
        "common_interactions": ["aspirin", "warfarin", "rifampin"],
        "contraindications": ["active bleeding", "severe liver disease"],
        "typical_supply_days": [30, 90]
    },
    "metformin": {
        "rxcui": "6809",
        "generic_name": "metformin",
        "brand_names": ["Glucophage", "Fortamet", "Glumetza"],
        "common_dosages": ["500mg", "850mg", "1000mg"],
        "requires_pa": False,
        "drug_class": "antidiabetic (biguanide)",
        "indication": "Type 2 diabetes mellitus",
        "common_interactions": ["alcohol", "contrast dye", "furosemide"],
        "contraindications": ["kidney disease", "metabolic acidosis"],
        "typical_supply_days": [30, 90]
    },
    "atorvastatin": {
        "rxcui": "83367",
        "generic_name": "atorvastatin",
        "brand_names": ["Lipitor"],
        "common_dosages": ["10mg", "20mg", "40mg", "80mg"],
        "requires_pa": False,
        "drug_class": "statin",
        "indication": "Hyperlipidemia, cardiovascular disease prevention",
        "common_interactions": ["grapefruit juice", "gemfibrozil", "cyclosporine"],
        "contraindications": ["active liver disease", "pregnancy"],
        "typical_supply_days": [30, 90]
    },
    "levothyroxine": {
        "rxcui": "10582",
        "generic_name": "levothyroxine",
        "brand_names": ["Synthroid", "Levoxyl", "Unithroid"],
        "common_dosages": ["25mcg", "50mcg", "75mcg", "100mcg", "125mcg"],
        "requires_pa": False,
        "drug_class": "thyroid hormone",
        "indication": "Hypothyroidism",
        "common_interactions": ["calcium", "iron", "coffee"],
        "contraindications": ["untreated thyrotoxicosis"],
        "typical_supply_days": [30, 90]
    },
    "omeprazole": {
        "rxcui": "7646",
        "generic_name": "omeprazole", 
        "brand_names": ["Prilosec"],
        "common_dosages": ["20mg", "40mg"],
        "requires_pa": False,
        "drug_class": "proton pump inhibitor",
        "indication": "GERD, peptic ulcer disease",
        "common_interactions": ["clopidogrel", "warfarin", "digoxin"],
        "contraindications": ["hypersensitivity to PPIs"],
        "typical_supply_days": [30, 90]
    },
    "amlodipine": {
        "rxcui": "17767",
        "generic_name": "amlodipine",
        "brand_names": ["Norvasc"],
        "common_dosages": ["2.5mg", "5mg", "10mg"],
        "requires_pa": False,
        "drug_class": "calcium channel blocker",
        "indication": "Hypertension, angina",
        "common_interactions": ["grapefruit juice", "simvastatin"],
        "contraindications": ["cardiogenic shock", "severe aortic stenosis"],
        "typical_supply_days": [30, 90]
    },
    "insulin": {
        "rxcui": "5856",
        "generic_name": "insulin",
        "brand_names": ["Humalog", "Novolog", "Lantus"],
        "common_dosages": ["100 units/mL"],
        "requires_pa": True,
        "drug_class": "antidiabetic hormone",
        "indication": "Diabetes mellitus",
        "common_interactions": ["ACE inhibitors", "beta blockers"],
        "contraindications": ["hypoglycemia"],
        "typical_supply_days": [30]
    }
}

# Comprehensive pharmacy network with detailed information
PHARMACY_INVENTORY = {
    "cvs_main": {
        "name": "CVS Pharmacy - Main Street",
        "address": "123 Main Street, City, ST 12345",
        "phone": "(555) 123-4567",
        "distance_miles": 0.5,
        "wait_time_min": 30,
        "hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM",
        "accepts_insurance": ["BlueCross Shield", "Aetna", "UnitedHealth", "Medicare"],
        "services": ["prescription_refills", "vaccinations", "health_screenings"],
        "in_stock": ["lisinopril", "metformin", "atorvastatin", "omeprazole", "amlodipine", "levothyroxine"],
        "out_of_stock": ["eliquis", "insulin"],
        "prices": {
            "lisinopril_10mg_30": 15.99,
            "lisinopril_10mg_90": 42.99,
            "metformin_500mg_30": 4.99,
            "metformin_500mg_60": 8.99,
            "atorvastatin_20mg_30": 12.99,
            "omeprazole_20mg_30": 18.99,
            "amlodipine_5mg_30": 9.99,
            "levothyroxine_100mcg_30": 14.99
        },
        "drive_through": True,
        "parking_available": True
    },
    "walmart_plaza": {
        "name": "Walmart Pharmacy - Plaza",
        "address": "456 Plaza Drive, City, ST 12345",
        "phone": "(555) 234-5678", 
        "distance_miles": 3.2,
        "wait_time_min": 15,
        "hours": "Mon-Sun: 7AM-11PM",
        "accepts_insurance": ["BlueCross Shield", "Aetna", "UnitedHealth", "Medicare", "Medicaid"],
        "services": ["prescription_refills", "vaccinations", "$4_generics"],
        "in_stock": ["lisinopril", "metformin", "eliquis", "atorvastatin", "levothyroxine", "omeprazole"],
        "out_of_stock": ["insulin"],
        "prices": {
            "lisinopril_10mg_30": 4.00,
            "lisinopril_10mg_90": 10.00,
            "metformin_500mg_30": 4.00,
            "metformin_500mg_60": 4.00,
            "eliquis_5mg_30": 485.00,
            "atorvastatin_20mg_30": 4.00,
            "omeprazole_20mg_30": 4.00,
            "levothyroxine_100mcg_30": 4.00
        },
        "drive_through": True,
        "parking_available": True,
        "special_programs": ["$4_generic_program", "free_antibiotics"]
    },
    "walgreens_downtown": {
        "name": "Walgreens - Downtown",
        "address": "789 Downtown Boulevard, City, ST 12345",
        "phone": "(555) 345-6789",
        "distance_miles": 1.8,
        "wait_time_min": 25,
        "hours": "24/7",
        "accepts_insurance": ["BlueCross Shield", "Aetna", "UnitedHealth", "Cigna"],
        "services": ["prescription_refills", "vaccinations", "24hour_service"],
        "in_stock": ["lisinopril", "metformin", "atorvastatin", "omeprazole", "amlodipine", "insulin"],
        "out_of_stock": ["eliquis"],
        "prices": {
            "lisinopril_10mg_30": 13.99,
            "metformin_500mg_60": 7.99,
            "atorvastatin_20mg_30": 11.99,
            "omeprazole_20mg_30": 16.99,
            "amlodipine_5mg_30": 8.99,
            "insulin_100units_30": 295.00
        },
        "drive_through": True,
        "parking_available": False,
        "special_programs": ["24_hour_service", "delivery_available"]
    },
    "costco_warehouse": {
        "name": "Costco Pharmacy",
        "address": "321 Warehouse Way, City, ST 12345",
        "phone": "(555) 456-7890",
        "distance_miles": 5.1,
        "wait_time_min": 20,
        "hours": "Mon-Fri: 10AM-8:30PM, Sat: 9:30AM-6PM, Sun: 10AM-6PM",
        "accepts_insurance": ["BlueCross Shield", "Aetna", "UnitedHealth", "Medicare"],
        "services": ["prescription_refills", "vaccinations", "member_discounts"],
        "in_stock": ["lisinopril", "metformin", "eliquis", "atorvastatin", "omeprazole", "insulin"],
        "out_of_stock": ["amlodipine"],
        "prices": {
            "lisinopril_10mg_30": 3.20,
            "metformin_500mg_60": 3.40,
            "eliquis_5mg_30": 465.00,
            "atorvastatin_20mg_30": 3.60,
            "omeprazole_20mg_30": 3.80,
            "insulin_100units_30": 275.00
        },
        "drive_through": False,
        "parking_available": True,
        "membership_required": True,
        "special_programs": ["member_only_pricing", "bulk_discounts"]
    },
    "rite_aid_north": {
        "name": "Rite Aid - North Side",
        "address": "654 North Avenue, City, ST 12345",
        "phone": "(555) 567-8901",
        "distance_miles": 2.7,
        "wait_time_min": 22,
        "hours": "Mon-Sat: 8AM-10PM, Sun: 9AM-8PM",
        "accepts_insurance": ["BlueCross Shield", "Aetna", "Medicare"],
        "services": ["prescription_refills", "vaccinations", "wellness_rewards"],
        "in_stock": ["lisinopril", "atorvastatin", "omeprazole", "amlodipine", "levothyroxine"],
        "out_of_stock": ["metformin", "eliquis", "insulin"],
        "prices": {
            "lisinopril_10mg_30": 14.50,
            "atorvastatin_20mg_30": 13.50,
            "omeprazole_20mg_30": 17.50,
            "amlodipine_5mg_30": 10.50,
            "levothyroxine_100mcg_30": 15.50
        },
        "drive_through": True,
        "parking_available": True,
        "special_programs": ["wellness_rewards", "senior_discounts"]
    }
}

# Mock patient data
MOCK_PATIENTS = {
    "12345": {  # Mock patient ID for demo
        "name": "John Doe",
        "dob": "1975-06-15",
        "insurance": "BlueCross Shield",
        "medications": [
            {
                "name": "lisinopril",
                "dosage": "10mg",
                "strength": "10mg tablets",
                "start_date": "2023-01-15",
                "refills_remaining": 2,
                "last_filled": "2024-01-05",
                "adherence_rate": 0.92,
                "quantity": 30,
                "directions": "Take 1 tablet daily"
            },
            {
                "name": "metformin",
                "dosage": "500mg",
                "strength": "500mg tablets",
                "start_date": "2022-06-20", 
                "refills_remaining": 0,
                "last_filled": "2023-12-10",
                "adherence_rate": 0.88,
                "quantity": 60,
                "directions": "Take 1 tablet twice daily with meals"
            },
            {
                "name": "atorvastatin",
                "dosage": "20mg",
                "strength": "20mg tablets", 
                "start_date": "2023-03-01",
                "refills_remaining": 3,
                "last_filled": "2024-01-15",
                "adherence_rate": 0.95,
                "quantity": 30,
                "directions": "Take 1 tablet daily at bedtime"
            }
        ],
        "allergies": ["penicillin", "sulfa drugs"],
        "conditions": ["hypertension", "type 2 diabetes", "hyperlipidemia"]
    },
    "67890": {  # Additional test patient
        "name": "Jane Smith",
        "dob": "1982-03-22",
        "insurance": "Aetna",
        "medications": [
            {
                "name": "eliquis",
                "dosage": "5mg",
                "strength": "5mg tablets",
                "start_date": "2023-08-10",
                "refills_remaining": 1,
                "last_filled": "2024-01-01",
                "adherence_rate": 0.89,
                "quantity": 60,
                "directions": "Take 1 tablet twice daily"
            }
        ],
        "allergies": ["aspirin"],
        "conditions": ["atrial fibrillation"]
    }
}

# Comprehensive insurance formulary data
INSURANCE_FORMULARIES = {
    "BlueCross Shield": {
        "plan_name": "BlueCross Shield Standard",
        "type": "commercial",
        "formulary": {
            "lisinopril": {
                "tier": 1, 
                "copay": 10, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "metformin": {
                "tier": 1, 
                "copay": 10, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "atorvastatin": {
                "tier": 2, 
                "copay": 25, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "eliquis": {
                "tier": 3, 
                "copay": 75, 
                "pa_required": True, 
                "covered": True,
                "quantity_limits": "60 tablets per 30 days",
                "step_therapy": True,
                "pa_criteria": ["Documented atrial fibrillation", "Failed warfarin therapy", "Contraindication to warfarin"]
            },
            "insulin": {
                "tier": 2, 
                "copay": 35, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": "10mL per 30 days",
                "step_therapy": False
            },
            "levothyroxine": {
                "tier": 1, 
                "copay": 10, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "omeprazole": {
                "tier": 2, 
                "copay": 25, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "amlodipine": {
                "tier": 1, 
                "copay": 10, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            }
        },
        "deductible": 500,
        "out_of_pocket_max": 3000
    },
    "Aetna": {
        "plan_name": "Aetna Better Health",
        "type": "commercial", 
        "formulary": {
            "lisinopril": {
                "tier": 1, 
                "copay": 5, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "metformin": {
                "tier": 1, 
                "copay": 5, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "eliquis": {
                "tier": 3, 
                "copay": 60, 
                "pa_required": True, 
                "covered": True,
                "quantity_limits": "60 tablets per 30 days",
                "step_therapy": True,
                "pa_criteria": ["Documented atrial fibrillation or VTE", "Age >= 65 or CHADS2 score >= 2"]
            },
            "atorvastatin": {
                "tier": 2, 
                "copay": 20, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            }
        },
        "deductible": 750,
        "out_of_pocket_max": 4000
    },
    "Medicare": {
        "plan_name": "Medicare Part D Standard",
        "type": "medicare",
        "formulary": {
            "lisinopril": {
                "tier": 1, 
                "copay": 3, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "metformin": {
                "tier": 1, 
                "copay": 3, 
                "pa_required": False, 
                "covered": True,
                "quantity_limits": None,
                "step_therapy": False
            },
            "eliquis": {
                "tier": 4, 
                "copay": 150, 
                "pa_required": True, 
                "covered": True,
                "quantity_limits": "60 tablets per 30 days",
                "step_therapy": True,
                "pa_criteria": ["Medicare coverage criteria", "Failed warfarin or contraindicated"]
            }
        },
        "deductible": 545,
        "coverage_gap": 5030,
        "out_of_pocket_max": 8000
    }
}

# Prior authorization criteria database
PRIOR_AUTH_CRITERIA = {
    "eliquis": {
        "required": True,
        "criteria": [
            "Documented atrial fibrillation with CHA2DS2-VASc score ≥2",
            "History of DVT/PE with contraindication to warfarin", 
            "Failed therapy with warfarin due to INR instability",
            "Documented bleeding event on warfarin"
        ],
        "required_documentation": [
            "Diagnosis codes for atrial fibrillation or VTE",
            "CHA2DS2-VASc score calculation",
            "Lab results showing contraindication to warfarin (if applicable)",
            "Previous medication trial history with dates and outcomes"
        ],
        "processing_time_days": "3-5 business days",
        "approval_rate": 0.85,
        "common_denial_reasons": [
            "Insufficient documentation of indication",
            "No trial of preferred alternative documented",
            "Duplicate therapy with other anticoagulants"
        ]
    },
    "insulin": {
        "required": True,
        "criteria": [
            "Diagnosis of diabetes mellitus (Type 1 or Type 2)",
            "A1C > 7.0% despite oral antidiabetic therapy",
            "Contraindication to or failure of metformin",
            "Specialist endocrinologist recommendation"
        ],
        "required_documentation": [
            "Recent A1C results within 3 months",
            "Documentation of oral medication trials",
            "Endocrinologist consultation note",
            "Blood glucose logs"
        ],
        "processing_time_days": "2-4 business days",
        "approval_rate": 0.92,
        "common_denial_reasons": [
            "A1C not above threshold",
            "Insufficient trial of oral medications"
        ]
    }
}

# GoodRx-style discount pricing data
GOODRX_DISCOUNTS = {
    "discount_programs": {
        "goodrx": {"name": "GoodRx", "average_savings": 0.20, "max_savings": 0.80},
        "singlecare": {"name": "SingleCare", "average_savings": 0.18, "max_savings": 0.75},
        "rxsaver": {"name": "RxSaver", "average_savings": 0.15, "max_savings": 0.70}
    },
    "manufacturer_coupons": {
        "eliquis": {
            "available": True,
            "max_savings": 60,
            "eligibility": "Commercial insurance only",
            "website": "eliquis.com/copay-card"
        },
        "insulin": {
            "available": True, 
            "max_savings": 35,
            "eligibility": "All patients",
            "website": "manufacturer-insulin-savings.com"
        }
    }
}

# Drug interaction database
DRUG_INTERACTIONS = {
    "lisinopril": [
        {
            "interacting_drug": "ibuprofen",
            "severity": "moderate",
            "effect": "NSAIDs may reduce the antihypertensive effect of ACE inhibitors and increase risk of kidney problems",
            "management": "Monitor blood pressure and kidney function. Consider acetaminophen for pain relief."
        },
        {
            "interacting_drug": "potassium supplements",
            "severity": "major", 
            "effect": "May cause dangerously high potassium levels (hyperkalemia)",
            "management": "Monitor potassium levels closely. May need dose adjustment or alternative supplement."
        },
        {
            "interacting_drug": "lithium",
            "severity": "moderate",
            "effect": "ACE inhibitors may increase lithium levels, leading to toxicity",
            "management": "Monitor lithium levels and watch for signs of lithium toxicity"
        }
    ],
    "metformin": [
        {
            "interacting_drug": "alcohol",
            "severity": "moderate",
            "effect": "Increased risk of lactic acidosis, especially with excessive alcohol consumption",
            "management": "Limit alcohol intake and avoid binge drinking"
        },
        {
            "interacting_drug": "contrast dye",
            "severity": "major",
            "effect": "Risk of lactic acidosis due to kidney dysfunction from contrast",
            "management": "Discontinue metformin before contrast procedures, resume after 48 hours if kidney function normal"
        }
    ],
    "eliquis": [
        {
            "interacting_drug": "aspirin",
            "severity": "major",
            "effect": "Significantly increased risk of bleeding",
            "management": "Use combination only if clearly indicated. Monitor for bleeding signs."
        },
        {
            "interacting_drug": "warfarin", 
            "severity": "contraindicated",
            "effect": "Excessive anticoagulation and severe bleeding risk",
            "management": "Do not use together. Transition carefully between anticoagulants."
        },
        {
            "interacting_drug": "rifampin",
            "severity": "major",
            "effect": "Rifampin significantly reduces apixaban levels, decreasing effectiveness",
            "management": "Avoid combination or use alternative anticoagulant"
        }
    ],
    "atorvastatin": [
        {
            "interacting_drug": "grapefruit juice",
            "severity": "moderate",
            "effect": "Grapefruit juice increases statin levels, increasing risk of muscle problems",
            "management": "Avoid grapefruit juice or use alternative statin"
        }
    ]
}

# Mock order tracking system
ORDER_TRACKING = {
    "order_statuses": ["received", "processing", "ready", "picked_up", "cancelled"],
    "typical_processing_times": {
        "new_prescription": 30,
        "refill": 15,
        "transfer": 45,
        "compound": 120
    }
}
