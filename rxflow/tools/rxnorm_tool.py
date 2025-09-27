"""RxNorm API integration tool for medication verification and lookup."""

import requests
from langchain.tools import Tool
from typing import Dict, Optional, List
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
        """Check drug interactions using enhanced interaction database"""
        try:
            from ..services.mock_data import DRUG_INTERACTIONS
            
            logger.info(f"[AI USAGE] Checking drug interactions for {medication_name}")
            
            medication_lower = medication_name.lower().strip()
            interactions = DRUG_INTERACTIONS.get(medication_lower, [])
            
            # Categorize interactions by severity
            major_interactions = [i for i in interactions if i["severity"] == "major"]
            moderate_interactions = [i for i in interactions if i["severity"] == "moderate"]
            contraindicated = [i for i in interactions if i["severity"] == "contraindicated"]
            
            return {
                "success": True,
                "medication": medication_name,
                "interactions": interactions,
                "interaction_summary": {
                    "total_count": len(interactions),
                    "major_count": len(major_interactions),
                    "moderate_count": len(moderate_interactions),
                    "contraindicated_count": len(contraindicated)
                },
                "severity_breakdown": {
                    "major": major_interactions,
                    "moderate": moderate_interactions, 
                    "contraindicated": contraindicated
                },
                "has_interactions": len(interactions) > 0,
                "highest_severity": self._get_highest_severity(interactions),
                "clinical_significance": self._assess_clinical_significance(interactions),
                "source": "enhanced_mock"
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
        """Enhanced fallback mock data when API is unavailable"""
        med_lower = medication_name.lower().strip()
        
        if med_lower in self.mock_db:
            med_info = self.mock_db[med_lower]
            return {
                "success": True,
                "query": medication_name,
                "medications": [{
                    "rxcui": med_info.get("rxcui", f"mock_{med_lower}"),
                    "name": med_info["generic_name"],
                    "brand_names": med_info["brand_names"],
                    "common_dosages": med_info["common_dosages"],
                    "drug_class": med_info["drug_class"],
                    "indication": med_info.get("indication", ""),
                    "requires_pa": med_info.get("requires_pa", False),
                    "typical_supply_days": med_info.get("typical_supply_days", [30, 90]),
                    "contraindications": med_info.get("contraindications", []),
                    "common_interactions": med_info.get("common_interactions", [])
                }],
                "result_count": 1,
                "source": "mock_enhanced"
            }
        
        # Return "not found" for unknown medications
        return {
            "success": False,
            "query": medication_name,
            "error": f"Medication '{medication_name}' not found in database",
            "medications": [],
            "result_count": 0,
            "source": "mock",
            "suggestions": self._get_medication_suggestions(medication_name)
        }
    
    def _get_medication_suggestions(self, medication_name: str) -> List[str]:
        """Provide medication name suggestions for typos or partial matches"""
        suggestions = []
        med_lower = medication_name.lower()
        
        for med_name in self.mock_db.keys():
            # Simple fuzzy matching - check if query is substring or vice versa
            if (med_lower in med_name or 
                med_name in med_lower or 
                len(set(med_lower) & set(med_name)) >= min(3, len(med_lower))):
                suggestions.append(med_name)
        
        return suggestions[:3]  # Return top 3 suggestions
    
    def _get_highest_severity(self, interactions: List[Dict]) -> str:
        """Determine the highest severity level among interactions"""
        if not interactions:
            return "none"
        
        severity_levels = {"contraindicated": 4, "major": 3, "moderate": 2, "minor": 1}
        highest = max(interactions, key=lambda x: severity_levels.get(x.get("severity", "minor"), 1))
        return highest.get("severity", "none")
    
    def _assess_clinical_significance(self, interactions: List[Dict]) -> str:
        """Assess overall clinical significance of interactions"""
        if not interactions:
            return "No significant interactions found"
        
        contraindicated = any(i.get("severity") == "contraindicated" for i in interactions)
        major_count = sum(1 for i in interactions if i.get("severity") == "major")
        
        if contraindicated:
            return "CRITICAL: Contraindicated drug combination detected"
        elif major_count > 0:
            return f"WARNING: {major_count} major interaction(s) require careful monitoring"
        else:
            return "CAUTION: Monitor for interaction effects"

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