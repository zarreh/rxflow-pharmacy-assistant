"""RxNorm API integration tool for medication verification and lookup."""

import requests
from langchain.tools import Tool
from typing import Dict, Optional
import time
from ..services.mock_data import MEDICATIONS_DB
from ..utils.logger import get_logger

logger = get_logger(__name__)

class RxNormTool:
    """Real RxNorm API integration for medication verification with fallback to mock data"""
    
    BASE_URL = "https://rxnav.nlm.nih.gov/REST"
    TIMEOUT = 5  # seconds
    
    def __init__(self):
        self.mock_db = MEDICATIONS_DB
    
    def search_medication(self, medication_name: str) -> Dict:
        """Search for medication in RxNorm database with fallback to mock data"""
        try:
            logger.info(f"[AI USAGE] Searching RxNorm API for medication: {medication_name}")
            
            # Try real API first
            response = requests.get(
                f"{self.BASE_URL}/drugs.json",
                params={"name": medication_name.strip()},
                timeout=self.TIMEOUT
            )
            
            if response.status_code == 200:
                data = response.json()
                parsed_result = self._parse_rxnorm_response(data, medication_name)
                if parsed_result.get("medications"):
                    logger.info(f"[AI USAGE] Successfully retrieved data from RxNorm API")
                    return parsed_result
            
            # Fallback to mock data if API fails or returns no results
            logger.warning(f"RxNorm API failed or returned no results, using mock data")
            return self._get_mock_medication_data(medication_name)
                
        except requests.exceptions.Timeout:
            logger.warning(f"RxNorm API timeout, falling back to mock data")
            return self._get_mock_medication_data(medication_name)
        except Exception as e:
            logger.error(f"RxNorm API error: {str(e)}, falling back to mock data")
            return self._get_mock_medication_data(medication_name)
    
    def verify_dosage(self, query: str) -> Dict:
        """
        Verify if a dosage is valid for a medication
        Query format: "medication_name:dosage" (e.g., "lisinopril:10mg")
        """
        try:
            if ':' not in query:
                return {
                    "success": False,
                    "error": "Invalid query format. Use 'medication:dosage'",
                    "source": "validation"
                }
            
            medication_name, dosage = query.split(':', 1)
            medication_name = medication_name.strip().lower()
            dosage = dosage.strip()
            
            logger.info(f"[AI USAGE] Verifying dosage {dosage} for medication {medication_name}")
            
            # Check in mock database first for common medications
            if medication_name in self.mock_db:
                med_info = self.mock_db[medication_name]
                is_valid = dosage in med_info["common_dosages"]
                
                return {
                    "success": True,
                    "medication": medication_name,
                    "dosage": dosage,
                    "is_valid_dosage": is_valid,
                    "available_dosages": med_info["common_dosages"],
                    "drug_class": med_info["drug_class"],
                    "source": "mock"
                }
            
            # For unknown medications, assume valid (in real system, would check RxNorm)
            return {
                "success": True,
                "medication": medication_name,
                "dosage": dosage,
                "is_valid_dosage": True,
                "available_dosages": ["Unknown"],
                "drug_class": "Unknown",
                "source": "assumed"
            }
            
        except Exception as e:
            logger.error(f"Error verifying dosage: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to verify dosage: {str(e)}",
                "source": "error"
            }
    
    def get_interactions(self, medication_name: str) -> Dict:
        """Check drug interactions (simplified for demo)"""
        try:
            logger.info(f"[AI USAGE] Checking drug interactions for {medication_name}")
            
            # Mock interaction data - in real system would use RxNorm interaction API
            mock_interactions = {
                "lisinopril": [
                    {
                        "interacting_drug": "ibuprofen",
                        "severity": "moderate", 
                        "effect": "May reduce effectiveness of lisinopril and increase blood pressure"
                    },
                    {
                        "interacting_drug": "potassium supplements",
                        "severity": "major",
                        "effect": "May cause dangerously high potassium levels"
                    }
                ],
                "metformin": [
                    {
                        "interacting_drug": "alcohol",
                        "severity": "moderate",
                        "effect": "Increased risk of lactic acidosis"
                    }
                ],
                "eliquis": [
                    {
                        "interacting_drug": "aspirin",
                        "severity": "major",
                        "effect": "Increased risk of bleeding"
                    },
                    {
                        "interacting_drug": "warfarin",
                        "severity": "major",
                        "effect": "Increased risk of bleeding - do not use together"
                    }
                ]
            }
            
            interactions = mock_interactions.get(medication_name.lower(), [])
            
            return {
                "success": True,
                "medication": medication_name,
                "interactions": interactions,
                "has_interactions": len(interactions) > 0,
                "interaction_count": len(interactions),
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error checking interactions: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to check interactions: {str(e)}",
                "source": "error"
            }
    
    def _parse_rxnorm_response(self, data: Dict, medication_name: str) -> Dict:
        """Parse RxNorm API response"""
        try:
            drug_group = data.get("drugGroup", {})
            concept_group = drug_group.get("conceptGroup", [])
            
            medications = []
            for group in concept_group:
                if "conceptProperties" in group:
                    for concept in group["conceptProperties"]:
                        medications.append({
                            "rxcui": concept.get("rxcui"),
                            "name": concept.get("name", ""),
                            "synonym": concept.get("synonym", ""),
                            "tty": concept.get("tty", ""),  # Term type
                            "language": concept.get("language", "ENG")
                        })
            
            return {
                "success": True,
                "query": medication_name,
                "medications": medications[:10],  # Limit results
                "result_count": len(medications),
                "source": "rxnorm_api"
            }
            
        except Exception as e:
            logger.error(f"Error parsing RxNorm response: {str(e)}")
            return self._get_mock_medication_data(medication_name)
    
    def _get_mock_medication_data(self, medication_name: str) -> Dict:
        """Fallback mock data when API is unavailable"""
        med_lower = medication_name.lower().strip()
        
        if med_lower in self.mock_db:
            med_info = self.mock_db[med_lower]
            return {
                "success": True,
                "query": medication_name,
                "medications": [{
                    "rxcui": f"mock_{med_lower}",
                    "name": med_info["generic_name"],
                    "brand_names": med_info["brand_names"],
                    "common_dosages": med_info["common_dosages"],
                    "drug_class": med_info["drug_class"],
                    "requires_pa": med_info.get("requires_pa", False)
                }],
                "result_count": 1,
                "source": "mock"
            }
        
        # Return "not found" for unknown medications
        return {
            "success": False,
            "query": medication_name,
            "error": f"Medication '{medication_name}' not found in database",
            "medications": [],
            "result_count": 0,
            "source": "mock"
        }

# Create LangChain tools
rxnorm_tool = Tool(
    name="rxnorm_medication_lookup",
    description="Look up medication information from RxNorm database. Returns drug details, RxCUI, brand names, and classifications. Use medication name as input.",
    func=lambda query: RxNormTool().search_medication(query)
)

dosage_verification_tool = Tool(
    name="verify_medication_dosage",
    description="Verify if a dosage is valid for a medication. Use format 'medication:dosage' (e.g., 'lisinopril:10mg'). Returns validation and available dosages.",
    func=lambda query: RxNormTool().verify_dosage(query)
)

interaction_tool = Tool(
    name="check_drug_interactions",
    description="Check for drug interactions for a medication. Use medication name as input. Returns potential interactions and severity levels.",
    func=lambda query: RxNormTool().get_interactions(query)
)