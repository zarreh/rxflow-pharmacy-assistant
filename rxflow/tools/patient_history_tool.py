"""Patient History Tool for retrieving patient medication history and adherence data."""

from langchain.tools import Tool
from typing import Dict, List, Optional
import json
from datetime import datetime, timedelta
from ..services.mock_data import MOCK_PATIENTS
from ..utils.logger import get_logger

logger = get_logger(__name__)

class PatientHistoryTool:
    """Mock patient medication history database"""
    
    def __init__(self):
        self.patient_data = MOCK_PATIENTS
    
    def get_medication_history(self, query: str) -> Dict:
        """
        Retrieve patient medication history
        Query format: "patient_id:medication_name" or just "medication_name" (uses default patient)
        """
        try:
            # Parse query - handle both "patient_id:medication" and just "medication"
            if ':' in query:
                patient_id, medication_name = query.split(':', 1)
            else:
                patient_id = "12345"  # Default patient for demo
                medication_name = query.strip()
            
            logger.info(f"[AI USAGE] Looking up medication history for patient {patient_id}, medication: {medication_name}")
            
            patient = self.patient_data.get(patient_id, {})
            medications = patient.get("medications", [])
            
            if medication_name and medication_name.lower() != "all":
                # Filter by medication name
                medications = [
                    m for m in medications 
                    if medication_name.lower() in m["name"].lower()
                ]
            
            return {
                "success": True,
                "patient_id": patient_id,
                "medications": medications,
                "allergies": patient.get("allergies", []),
                "conditions": patient.get("conditions", []),
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error retrieving medication history: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve medication history: {str(e)}",
                "source": "mock"
            }
    
    def check_adherence(self, query: str) -> Dict:
        """
        Check medication adherence and refill patterns
        Query format: "patient_id:medication_name" or just "medication_name"
        """
        try:
            # Parse query
            if ':' in query:
                patient_id, medication_name = query.split(':', 1)
            else:
                patient_id = "12345"  # Default patient
                medication_name = query.strip()
            
            logger.info(f"[AI USAGE] Checking adherence for patient {patient_id}, medication: {medication_name}")
            
            history = self.get_medication_history(query)
            
            if history["success"] and history["medications"]:
                med = history["medications"][0]  # Take first match
                
                # Calculate days since last refill
                last_filled = datetime.strptime(med["last_filled"], "%Y-%m-%d")
                days_since_refill = (datetime.now() - last_filled).days
                
                # Determine adherence status
                adherence_rate = med["adherence_rate"]
                if adherence_rate >= 0.9:
                    status = "excellent"
                elif adherence_rate >= 0.8:
                    status = "good"
                elif adherence_rate >= 0.7:
                    status = "fair"
                else:
                    status = "poor"
                
                return {
                    "success": True,
                    "medication": med["name"],
                    "dosage": med["dosage"],
                    "adherence_rate": adherence_rate,
                    "adherence_status": status,
                    "last_filled": med["last_filled"],
                    "days_since_refill": days_since_refill,
                    "refills_remaining": med["refills_remaining"],
                    "needs_new_prescription": med["refills_remaining"] == 0,
                    "source": "mock"
                }
            
            return {
                "success": False,
                "error": f"Medication '{medication_name}' not found in patient history",
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error checking adherence: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to check adherence: {str(e)}",
                "source": "mock"
            }
    
    def get_allergies(self, patient_id: str = "12345") -> Dict:
        """Get patient allergies"""
        try:
            logger.info(f"[AI USAGE] Retrieving allergies for patient {patient_id}")
            
            patient = self.patient_data.get(patient_id, {})
            allergies = patient.get("allergies", [])
            
            return {
                "success": True,
                "patient_id": patient_id,
                "allergies": allergies,
                "has_allergies": len(allergies) > 0,
                "source": "mock"
            }
            
        except Exception as e:
            logger.error(f"Error retrieving allergies: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve allergies: {str(e)}",
                "source": "mock"
            }

# Create LangChain tools
patient_history_tool = Tool(
    name="patient_medication_history",
    description="Retrieve patient medication history, adherence data, and allergies. Use format 'medication_name' or 'patient_id:medication_name'. Returns medication details, refill status, and patient safety information.",
    func=lambda query: PatientHistoryTool().get_medication_history(query)
)

adherence_tool = Tool(
    name="check_medication_adherence", 
    description="Check patient medication adherence rates and refill patterns. Use format 'medication_name' or 'patient_id:medication_name'. Returns adherence percentage, status, and refill needs.",
    func=lambda query: PatientHistoryTool().check_adherence(query)
)

allergy_tool = Tool(
    name="patient_allergies",
    description="Get patient allergy information for medication safety checks. Use patient_id (defaults to '12345' for demo).",
    func=lambda patient_id: PatientHistoryTool().get_allergies(patient_id)
)