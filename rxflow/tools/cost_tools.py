"""Cost comparison and insurance tools for price optimization and coverage checks."""

from langchain.tools import Tool
from typing import Dict, List, Optional
import random
from ..services.mock_data import PHARMACY_INVENTORY, MOCK_PATIENTS
from ..utils.logger import get_logger

logger = get_logger(__name__)

class MockGoodRxTool:
    """Simulates GoodRx API for price comparison across pharmacies"""
    
    def __init__(self):
        self.pharmacy_data = PHARMACY_INVENTORY
        
        # Base price multipliers for different pharmacy chains
        self.price_multipliers = {
            "cvs": 1.2,
            "walmart": 0.4,
            "walgreens": 1.1, 
            "costco": 0.3,
            "rite_aid": 1.15,
            "kroger": 0.5,
            "safeway": 1.0
        }
    
    def get_prices(self, query: str) -> Dict:
        """
        Get medication prices from multiple pharmacies
        Query format: "medication:dosage:quantity" or "medication:dosage" (defaults to 30 day supply)
        """
        try:
            # Parse query
            parts = query.split(':')
            if len(parts) < 2:
                return {
                    "success": False,
                    "error": "Invalid query format. Use 'medication:dosage:quantity' or 'medication:dosage'",
                    "source": "validation"
                }
            
            medication = parts[0].strip().lower()
            dosage = parts[1].strip()
            quantity = int(parts[2]) if len(parts) > 2 else 30
            
            logger.info(f"[AI USAGE] Getting GoodRx prices for {medication} {dosage}, quantity: {quantity}")
            
            # Generate realistic base price based on medication type
            base_prices = {
                "lisinopril": 15.0,
                "metformin": 10.0,
                "atorvastatin": 20.0,
                "eliquis": 450.0,
                "insulin": 300.0,
                "levothyroxine": 12.0,
                "omeprazole": 8.0
            }
            
            base_price = base_prices.get(medication, random.uniform(20, 100))
            
            # Adjust for quantity (assume 30-day supply as base)
            adjusted_base = base_price * (quantity / 30)
            
            # Generate prices for different pharmacies
            pharmacy_prices = {}
            for pharmacy_type, multiplier in self.price_multipliers.items():
                # Add some random variation
                variation = random.uniform(0.9, 1.1)
                price = round(adjusted_base * multiplier * variation, 2)
                
                # Map generic pharmacy types to actual pharmacy names
                pharmacy_name = self._get_pharmacy_name(pharmacy_type)
                pharmacy_prices[pharmacy_name] = {
                    "cash_price": price,
                    "with_goodrx": round(price * 0.8, 2),  # GoodRx typically saves 20%
                    "savings": round(price * 0.2, 2)
                }
            
            # Calculate summary statistics
            cash_prices = [p["cash_price"] for p in pharmacy_prices.values()]
            goodrx_prices = [p["with_goodrx"] for p in pharmacy_prices.values()]
            
            return {
                "success": True,
                "medication": medication,
                "dosage": dosage,
                "quantity": quantity,
                "pharmacy_prices": pharmacy_prices,
                "summary": {
                    "lowest_cash_price": min(cash_prices),
                    "highest_cash_price": max(cash_prices),
                    "lowest_goodrx_price": min(goodrx_prices),
                    "max_cash_savings": max(cash_prices) - min(cash_prices),
                    "max_goodrx_savings": max(cash_prices) - min(goodrx_prices),
                    "average_goodrx_savings": round(sum(p["savings"] for p in pharmacy_prices.values()) / len(pharmacy_prices), 2)
                },
                "source": "mock_goodrx"
            }
            
        except Exception as e:
            logger.error(f"Error getting GoodRx prices: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get price information: {str(e)}",
                "source": "error"
            }
    
    def _get_pharmacy_name(self, pharmacy_type: str) -> str:
        """Map pharmacy types to display names"""
        name_mapping = {
            "cvs": "CVS Pharmacy",
            "walmart": "Walmart Pharmacy", 
            "walgreens": "Walgreens",
            "costco": "Costco Pharmacy",
            "rite_aid": "Rite Aid",
            "kroger": "Kroger Pharmacy",
            "safeway": "Safeway Pharmacy"
        }
        return name_mapping.get(pharmacy_type, pharmacy_type.title())
    
    def compare_brand_vs_generic(self, query: str) -> Dict:
        """
        Compare brand name vs generic medication prices
        Query format: "medication_name" (looks up brand alternatives)
        """
        try:
            medication = query.strip().lower()
            logger.info(f"[AI USAGE] Comparing brand vs generic prices for {medication}")
            
            # Mock brand/generic mappings
            brand_generic_map = {
                "lisinopril": {"brand": "Prinivil", "brand_price": 85.0},
                "atorvastatin": {"brand": "Lipitor", "brand_price": 180.0},
                "metformin": {"brand": "Glucophage", "brand_price": 45.0},
                "omeprazole": {"brand": "Prilosec", "brand_price": 65.0}
            }
            
            if medication not in brand_generic_map:
                return {
                    "success": False,
                    "error": f"No brand comparison available for {medication}",
                    "source": "mock"
                }
            
            brand_info = brand_generic_map[medication]
            
            # Get generic price (use base calculation)
            generic_price = self.get_prices(f"{medication}:10mg:30")
            if not generic_price["success"]:
                return generic_price
            
            generic_lowest = generic_price["summary"]["lowest_cash_price"]
            brand_price = brand_info["brand_price"]
            
            return {
                "success": True,
                "generic_name": medication,
                "brand_name": brand_info["brand"],
                "generic_price": generic_lowest,
                "brand_price": brand_price,
                "savings_with_generic": round(brand_price - generic_lowest, 2),
                "percent_savings": round((brand_price - generic_lowest) / brand_price * 100, 1),
                "recommendation": "generic" if generic_lowest < brand_price * 0.8 else "brand",
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error comparing brand vs generic: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to compare prices: {str(e)}",
                "source": "error"
            }

class MockInsuranceFormularyTool:
    """Simulates insurance formulary checks and coverage determination"""
    
    def __init__(self):
        # Mock formulary data for different insurance plans
        self.formulary_data = {
            "BlueCross Shield": {
                "lisinopril": {"tier": 1, "copay": 10, "pa_required": False, "covered": True},
                "metformin": {"tier": 1, "copay": 10, "pa_required": False, "covered": True},
                "atorvastatin": {"tier": 2, "copay": 25, "pa_required": False, "covered": True},
                "eliquis": {"tier": 3, "copay": 75, "pa_required": True, "covered": True},
                "insulin": {"tier": 2, "copay": 35, "pa_required": False, "covered": True},
                "humira": {"tier": 4, "copay": 200, "pa_required": True, "covered": True}
            },
            "Aetna": {
                "lisinopril": {"tier": 1, "copay": 5, "pa_required": False, "covered": True},
                "metformin": {"tier": 1, "copay": 5, "pa_required": False, "covered": True},
                "eliquis": {"tier": 3, "copay": 60, "pa_required": True, "covered": True},
                "atorvastatin": {"tier": 2, "copay": 20, "pa_required": False, "covered": True}
            }
        }
    
    def check_coverage(self, query: str) -> Dict:
        """
        Check insurance coverage for medication
        Query format: "medication:insurance_plan" or just "medication" (uses default patient)
        """
        try:
            # Parse query
            if ':' in query:
                medication, insurance_plan = query.split(':', 1)
            else:
                medication = query
                # Use default patient's insurance
                insurance_plan = MOCK_PATIENTS["12345"]["insurance"]
            
            medication = medication.strip().lower()
            insurance_plan = insurance_plan.strip()
            
            logger.info(f"[AI USAGE] Checking insurance coverage for {medication} with {insurance_plan}")
            
            # Check formulary
            formulary = self.formulary_data.get(insurance_plan, {})
            coverage = formulary.get(medication)
            
            if coverage:
                return {
                    "success": True,
                    "medication": medication,
                    "insurance_plan": insurance_plan,
                    "covered": coverage["covered"],
                    "tier": coverage["tier"],
                    "copay": coverage["copay"],
                    "prior_authorization_required": coverage["pa_required"],
                    "tier_description": self._get_tier_description(coverage["tier"]),
                    "annual_deductible_applies": coverage["tier"] >= 3,
                    "source": "mock_formulary"
                }
            else:
                # Medication not on formulary
                return {
                    "success": True,
                    "medication": medication,
                    "insurance_plan": insurance_plan,
                    "covered": False,
                    "reason": "Non-formulary medication",
                    "alternatives_available": True,
                    "appeal_process_available": True,
                    "estimated_cash_price_range": "$50-$200",
                    "source": "mock_formulary"
                }
                
        except Exception as e:
            logger.error(f"Error checking insurance coverage: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to check coverage: {str(e)}",
                "source": "error"
            }
    
    def get_prior_auth_requirements(self, query: str) -> Dict:
        """
        Get prior authorization requirements and criteria
        Query format: "medication:insurance_plan" or just "medication"
        """
        try:
            # Parse query (similar to check_coverage)
            if ':' in query:
                medication, insurance_plan = query.split(':', 1)
            else:
                medication = query
                insurance_plan = MOCK_PATIENTS["12345"]["insurance"]
            
            medication = medication.strip().lower()
            
            logger.info(f"[AI USAGE] Getting prior auth requirements for {medication}")
            
            # Mock PA criteria data
            pa_criteria = {
                "eliquis": {
                    "required": True,
                    "criteria": [
                        "Documented atrial fibrillation with CHA2DS2-VASc score ≥2",
                        "History of DVT/PE with contraindication to warfarin",
                        "Failed therapy with warfarin due to INR instability"
                    ],
                    "required_documentation": [
                        "Diagnosis codes for atrial fibrillation or VTE",
                        "Lab results showing contraindication to warfarin (if applicable)",
                        "Previous medication trial history"
                    ],
                    "processing_time_days": "3-5 business days",
                    "approval_likelihood": "high_if_criteria_met"
                },
                "humira": {
                    "required": True,
                    "criteria": [
                        "Diagnosis of rheumatoid arthritis, Crohn's disease, or psoriasis",
                        "Failed adequate trial of methotrexate (RA) or sulfasalazine (IBD)",
                        "Disease activity score above moderate threshold"
                    ],
                    "required_documentation": [
                        "Specialist consultation note",
                        "Disease activity scores",
                        "Previous medication trial documentation"
                    ],
                    "processing_time_days": "5-10 business days",
                    "approval_likelihood": "moderate"
                }
            }
            
            if medication in pa_criteria:
                criteria = pa_criteria[medication]
                return {
                    "success": True,
                    "medication": medication,
                    "prior_authorization_required": criteria["required"],
                    "criteria": criteria["criteria"],
                    "required_documentation": criteria["required_documentation"],
                    "processing_time": criteria["processing_time_days"],
                    "approval_likelihood": criteria["approval_likelihood"],
                    "can_start_process": True,
                    "source": "mock_pa_database"
                }
            else:
                return {
                    "success": True,
                    "medication": medication,
                    "prior_authorization_required": False,
                    "reason": "Medication does not require prior authorization",
                    "source": "mock_pa_database"
                }
                
        except Exception as e:
            logger.error(f"Error getting PA requirements: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to get PA requirements: {str(e)}",
                "source": "error"
            }
    
    def _get_tier_description(self, tier: int) -> str:
        """Get description for formulary tiers"""
        descriptions = {
            1: "Generic medications - Lowest copay",
            2: "Preferred brand medications - Low copay", 
            3: "Non-preferred medications - Higher copay",
            4: "Specialty medications - Highest copay"
        }
        return descriptions.get(tier, "Unknown tier")

# Create LangChain tools
goodrx_tool = Tool(
    name="goodrx_price_lookup",
    description="Get medication prices from multiple pharmacies using GoodRx. Use format 'medication:dosage:quantity' or 'medication:dosage' (30-day default). Shows cash prices and GoodRx discounted prices.",
    func=lambda query: MockGoodRxTool().get_prices(query)
)

brand_generic_tool = Tool(
    name="compare_brand_generic_prices",
    description="Compare brand name vs generic medication prices to find savings opportunities. Use medication name as input.",
    func=lambda query: MockGoodRxTool().compare_brand_vs_generic(query)
)

insurance_tool = Tool(
    name="insurance_formulary_check",
    description="Check if medication is covered by insurance plan. Use format 'medication:insurance_plan' or just 'medication' (uses default patient insurance). Returns coverage, tier, copay, and PA requirements.",
    func=lambda query: MockInsuranceFormularyTool().check_coverage(query)
)

prior_auth_tool = Tool(
    name="prior_authorization_lookup",
    description="Get prior authorization requirements and criteria for medications. Use format 'medication:insurance_plan' or just 'medication'. Returns PA criteria and approval process.",
    func=lambda query: MockInsuranceFormularyTool().get_prior_auth_requirements(query)
)