"""Patient History Tool for retrieving patient medication history and adherence data."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from langchain.tools import Tool

from ..services.mock_data import MOCK_PATIENTS
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PatientHistoryTool:
    """Mock patient medication history database"""

    def __init__(self) -> None:
        self.patient_data = MOCK_PATIENTS

    def get_medication_history(self, query: str) -> Dict[str, Any]:
        """
        Retrieve patient medication history
        Query format: "patient_id:medication_name" or just "medication_name" (uses default patient)
        """
        try:
            # Parse query - handle both "patient_id:medication" and just "medication"
            if ":" in query:
                patient_id, medication_name = query.split(":", 1)
            else:
                patient_id = "12345"  # Default patient for demo
                medication_name = query.strip()

            logger.info(
                f"[AI USAGE] Looking up medication history for patient {patient_id}, medication: {medication_name}"
            )

            patient = self.patient_data.get(patient_id, {})
            medications = patient.get("medications", [])

            # Handle different query types
            show_all_medications = (
                not medication_name
                or medication_name.lower()
                in ["all", "", "unknown", "none", "any", "yes", "no", "ok", "sure"]
                or len(medication_name.strip()) < 3
                or medication_name.strip().isdigit()  # Very short queries likely want all medications  # If query is just a patient ID, show all medications
            )

            if not show_all_medications:
                # Enhanced medication search - handle both medication names and conditions
                medication_search = medication_name.lower()
                if "(" in medication_search:
                    medication_search = medication_search.split("(")[0].strip()

                # Map common conditions to medications
                condition_to_med = {
                    "acid reflux": "omeprazole",
                    "heartburn": "omeprazole",
                    "gerd": "omeprazole",
                    "stomach acid": "omeprazole",
                    "blood pressure": "lisinopril",
                    "hypertension": "lisinopril",
                    "diabetes": "metformin",
                    "blood sugar": "metformin",
                    "muscle spasm": "methocarbamol",
                    "muscle pain": "methocarbamol",
                    "pain": "meloxicam",
                    "inflammation": "meloxicam",
                }

                # Check if query is a condition and map to medication
                for condition, med_name in condition_to_med.items():
                    if condition in medication_search:
                        medication_search = med_name
                        break

                medications = [
                    m
                    for m in medications
                    if (
                        medication_search in m["name"].lower()
                        or m["name"].lower() in medication_search
                    )
                ]

            return {
                "success": True,
                "patient_id": patient_id,
                "medications": medications,
                "allergies": patient.get("allergies", []),
                "conditions": patient.get("conditions", []),
                "source": "mock",
            }

        except Exception as e:
            logger.error(f"Error retrieving medication history: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve medication history: {str(e)}",
                "source": "mock",
            }

    def check_adherence(self, query: str) -> Dict:
        """
        Check medication adherence and refill patterns
        Query format: "patient_id:medication_name" or just "medication_name"
        """
        try:
            # Parse query
            if ":" in query:
                patient_id, medication_name = query.split(":", 1)
            else:
                patient_id = "12345"  # Default patient
                medication_name = query.strip()

            logger.info(
                f"[AI USAGE] Checking adherence for patient {patient_id}, medication: {medication_name}"
            )

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
                    "source": "mock",
                }

            return {
                "success": False,
                "error": f"Medication '{medication_name}' not found in patient history",
                "source": "mock",
            }

        except Exception as e:
            logger.error(f"Error checking adherence: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to check adherence: {str(e)}",
                "source": "mock",
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
                "source": "mock",
            }

        except Exception as e:
            logger.error(f"Error retrieving allergies: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to retrieve allergies: {str(e)}",
                "source": "mock",
            }


def safe_medication_history(query: Union[str, Dict, None]) -> Dict:
    """Safe wrapper for medication history tool that handles various input types"""
    try:
        # Handle different input types and ensure we have a string
        processed_query: str
        if query is None or query == {} or query == "":
            processed_query = "all"  # Default to all medications
        elif isinstance(query, dict):
            # If it's a dict, try to extract useful information
            processed_query = str(query.get("medication", query.get("query", "all")))
        elif not isinstance(query, str):
            processed_query = str(query)
        else:
            processed_query = query

        return PatientHistoryTool().get_medication_history(processed_query)
    except Exception as e:
        logger.error(f"Error in safe_medication_history: {e}")
        return {
            "success": False,
            "error": f"Failed to process medication history request: {str(e)}",
            "source": "error_handler",
        }


def safe_adherence_check(query: Union[str, Dict, None]) -> Dict:
    """Safe wrapper for adherence check that handles various input types"""
    try:
        # Handle different input types and ensure we have a string
        processed_query: str
        if query is None or query == {} or query == "":
            # Default to checking most recent medication for demo patient
            processed_query = "12345:lisinopril"
        elif isinstance(query, dict):
            # If it's a dict, try to extract useful information
            processed_query = str(
                query.get("medication", query.get("query", "lisinopril"))
            )
        elif not isinstance(query, str):
            processed_query = str(query)
        else:
            processed_query = query

        return PatientHistoryTool().check_adherence(processed_query)
    except Exception as e:
        logger.error(f"Error in safe_adherence_check: {e}")
        return {
            "success": False,
            "error": f"Failed to process adherence check: {str(e)}",
            "source": "error_handler",
        }


def safe_allergy_check(patient_id: Union[str, Dict, None]) -> Dict:
    """Safe wrapper for allergy check that handles various input types"""
    try:
        # Handle different input types and ensure we have a string
        processed_patient_id: str
        if patient_id is None or patient_id == {} or patient_id == "":
            processed_patient_id = "12345"  # Default patient
        elif isinstance(patient_id, dict):
            # If it's a dict, try to extract patient_id
            processed_patient_id = str(patient_id.get("patient_id", "12345"))
        elif not isinstance(patient_id, str):
            processed_patient_id = str(patient_id)
        else:
            processed_patient_id = patient_id

        return PatientHistoryTool().get_allergies(processed_patient_id)
    except Exception as e:
        logger.error(f"Error in safe_allergy_check: {e}")
        return {
            "success": False,
            "error": f"Failed to process allergy check: {str(e)}",
            "source": "error_handler",
        }


# Create LangChain tools with safe wrappers
patient_history_tool = Tool(
    name="patient_medication_history",
    description="STEP 1 WORKFLOW: REQUIRED - Look up patient medication history for ANY refill request. Use 'medication_name' (like 'omeprazole' for acid reflux) or 'all' to find ALL patient medications. This tool finds the medication the customer is referring to WITHOUT requiring patient ID. Essential for prescription identification and refill processing.",
    func=safe_medication_history,
)

adherence_tool = Tool(
    name="check_medication_adherence",
    description="STEP 5 WORKFLOW: Check patient medication adherence and refill timing. Use after identifying medication to ensure proper refill timing. Use format 'medication_name' to get adherence data and determine if refill is due.",
    func=safe_adherence_check,
)

allergy_tool = Tool(
    name="patient_allergies",
    description="STEP 1 WORKFLOW: REQUIRED - Check patient allergies before any medication processing. Use 'default' or patient_id to get allergy information for safety verification. Always check allergies before proceeding with refills.",
    func=safe_allergy_check,
)
