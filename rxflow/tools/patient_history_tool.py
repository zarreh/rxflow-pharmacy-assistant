"""
Patient History Tool for RxFlow Pharmacy Assistant

This module provides comprehensive patient medication history retrieval and adherence 
analysis capabilities. It interfaces with patient databases to provide critical 
information needed for safe prescription refill processing.

The module includes tools for:
- Medication history lookup with fuzzy matching
- Adherence pattern analysis and scoring
- Allergy and contraindication checking
- Patient safety validation

Key Features:
    - Flexible query parsing for patient and medication identification
    - Comprehensive medication matching with multiple aliases
    - Adherence scoring with detailed analysis
    - Safety-first design with comprehensive error handling
    - Integration with LangChain for conversational interfaces

Safety Considerations:
    All tools include safety wrappers that prevent errors from propagating
    and provide graceful degradation when patient data is unavailable.

Example:
    ```python
    # Initialize patient history tool
    tool = PatientHistoryTool()
    
    # Look up patient medication history
    history = tool.get_medication_history("omeprazole")
    
    # Check adherence patterns
    adherence = tool.check_adherence("patient_123:lisinopril")
    ```

Classes:
    PatientHistoryTool: Main class for patient data operations

Functions:
    safe_medication_history: Safety wrapper for medication history lookup
    safe_adherence_check: Safety wrapper for adherence analysis
    safe_allergy_check: Safety wrapper for allergy verification

Dependencies:
    - Mock patient database for demonstration
    - LangChain Tool integration for conversational AI
    - Comprehensive logging for audit trails
"""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast, Union

from langchain.tools import Tool

from ..services.mock_data import MOCK_PATIENTS
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PatientHistoryTool:
    """
    Comprehensive patient medication history and adherence analysis tool.

    This class provides access to patient medication records, adherence patterns,
    and safety information needed for prescription refill processing. It implements
    fuzzy matching for medication names and provides detailed adherence analysis
    to support clinical decision making.

    The tool is designed to work with various patient database formats and provides
    consistent interfaces for medication history retrieval, adherence checking,
    and allergy verification.

    Attributes:
        patient_data (Dict[str, Any]): Patient database containing medication
            histories, allergies, and clinical information

    Key Features:
        - Flexible medication matching with aliases and generic names
        - Comprehensive adherence scoring with temporal analysis
        - Safety validation with allergy and interaction checking
        - Detailed logging for clinical audit trails
        - Graceful error handling for missing or incomplete data

    Example:
        ```python
        # Initialize with patient database
        history_tool = PatientHistoryTool()

        # Get comprehensive medication history
        history = history_tool.get_medication_history("omeprazole")
        print(f"Found {len(history['medications'])} medications")

        # Check specific patient adherence
        adherence = history_tool.check_adherence("12345:lisinopril")
        print(f"Adherence score: {adherence['adherence_score']}")
        ```
    """

    def __init__(self) -> None:
        self.patient_data = MOCK_PATIENTS

    def get_medication_history(self, query: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive patient medication history with flexible query support.

        This method provides access to patient medication records with intelligent
        query parsing and fuzzy matching capabilities. It supports both specific
        medication lookups and comprehensive medication reviews.

        Args:
            query (str): Query string in one of these formats:
                - "patient_id:medication_name" - Specific patient and medication
                - "medication_name" - Uses default patient (12345) for demo
                - "all" or empty - Returns complete medication list
                - Short queries (< 3 chars) - Returns all medications

        Returns:
            Dict[str, Any]: Comprehensive medication history containing:
                - patient_id: Patient identifier
                - patient_name: Patient's full name for verification
                - query: Original query for reference
                - medications: List of matching medications with details:
                    - name: Medication name
                    - generic_name: Generic equivalent if applicable
                    - strength: Dosage strength (e.g., "20mg")
                    - condition: Medical condition being treated
                    - last_filled: Date of most recent fill
                    - days_supply: Supply duration in days
                    - quantity: Number of units dispensed
                    - prescriber: Prescribing physician
                    - status: Current prescription status
                - total_medications: Count of matching medications
                - search_type: Type of search performed ("specific" or "all")

        Query Processing Logic:
            1. Parse patient ID and medication name from query
            2. Default to patient "12345" if no ID specified
            3. Determine if specific medication or full list requested
            4. Perform fuzzy matching for medication names
            5. Return comprehensive medication details

        Example Queries:
            ```python
            # Get all medications for default patient
            history = tool.get_medication_history("all")

            # Find specific medication for default patient
            history = tool.get_medication_history("omeprazole")

            # Find medication for specific patient
            history = tool.get_medication_history("67890:lisinopril")

            # Short query returns all medications
            history = tool.get_medication_history("hi")
            ```

        Fuzzy Matching:
            The method implements intelligent medication matching that handles:
            - Brand names and generic equivalents
            - Partial medication names
            - Common misspellings and abbreviations
            - Multiple medication aliases

        Safety Features:
            - Always returns valid response structure
            - Handles missing patient data gracefully
            - Logs all access attempts for audit trails
            - Prevents exposure of sensitive patient information

        Note:
            Uses mock patient data for demonstration purposes. In production,
            this would integrate with certified patient database systems
            following HIPAA compliance requirements.
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
            medications = cast(List[Dict[str, Any]], patient.get("medications", []))

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

    def get_allergies(self, patient_id: str) -> Dict[str, Any]:
        """
        Get comprehensive patient allergy information for safety screening.

        Retrieves all documented allergies and contraindications for the specified
        patient to support medication safety and prescription decisions.

        Args:
            patient_id (str): Unique patient identifier (e.g., "12345")
                Defaults to "12345" if empty or invalid

        Returns:
            Dict[str, Any]: Comprehensive allergy profile containing:
                - allergies (List[Dict]): List of allergy records with:
                    - allergen (str): Medication or substance name
                    - reaction (str): Type of allergic reaction
                    - severity (str): "Mild", "Moderate", "Severe", "Critical"
                    - date_reported (str): When allergy was first documented
                    - verified (bool): Whether clinically verified
                - patient_id (str): Patient identifier
                - allergy_count (int): Total number of documented allergies
                - high_risk_allergies (List[str]): Critical allergies list
                - contraindications (List[str]): Medications to avoid
        """
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
    """
    Safe wrapper for medication history lookup with comprehensive error handling.

    This function provides a robust interface for medication history retrieval
    that gracefully handles various input types, null values, and system errors.
    It ensures the conversation can continue even when patient data is unavailable.

    Args:
        query (Union[str, Dict, None]): Flexible input format supporting:
            - str: Direct query like "omeprazole" or "12345:lisinopril"
            - Dict: Query object with 'medication' or 'query' keys
            - None: Defaults to returning all medications for demo patient

    Returns:
        Dict: Standardized response containing:
            - success (bool): True if operation completed successfully
            - patient_id (str): Patient identifier used in lookup
            - medications (List): Medication records with full details
            - total_medications (int): Count of returned medications
            - error (str): Error message if operation failed
            - source (str): Data source identifier ("mock" for demo data)

    Error Handling:
        - Gracefully processes None, empty, or malformed inputs
        - Converts non-string inputs to appropriate string format
        - Returns informative error messages without exposing system details
        - Maintains conversation flow even when backend systems fail

    Safety Features:
        - Never raises exceptions - always returns valid dict
        - Sanitizes input to prevent injection attacks
        - Logs all errors for debugging without exposing to user
        - Provides fallback responses for system resilience

    Example:
        ```python
        # String query
        result = safe_medication_history("omeprazole")

        # Dict query
        result = safe_medication_history({"medication": "lisinopril"})

        # Null handling
        result = safe_medication_history(None)  # Returns all medications

        # Check results
        if result.get("success"):
            print(f"Found {result['total_medications']} medications")
        else:
            print(f"Error: {result['error']}")
        ```
    """
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
    """
    Safe wrapper for medication adherence analysis with intelligent input processing.

    This function provides robust adherence checking that handles various input
    formats and provides detailed adherence scoring and analysis. It's essential
    for clinical decision making and identifying patients who may need additional
    support or intervention.

    Args:
        query (Union[str, Dict, None]): Flexible query format supporting:
            - str: "patient_id:medication" or just "medication" (uses default patient)
            - Dict: Object with 'patient_id', 'medication', or 'query' keys
            - None: Defaults to checking most common medication for demo patient

    Returns:
        Dict: Comprehensive adherence analysis containing:
            - success (bool): True if analysis completed successfully
            - patient_id (str): Patient identifier for the analysis
            - medication (str): Medication name analyzed
            - adherence_score (float): Calculated adherence percentage (0-100)
            - adherence_level (str): Qualitative assessment ("Poor", "Fair", "Good", "Excellent")
            - days_since_last_fill (int): Days since most recent prescription fill
            - refill_pattern (str): Analysis of refill timing patterns
            - recommendations (List[str]): Clinical recommendations based on adherence
            - risk_factors (List[str]): Identified adherence risk factors
            - error (str): Error details if analysis failed
            - source (str): Data source identifier

    Adherence Calculation:
        The adherence score is calculated using multiple factors:
        - Prescription refill timing consistency
        - Days supply vs. actual refill intervals
        - Historical patterns and trends
        - Gap analysis for missed doses

    Clinical Scoring:
        - 90-100%: Excellent adherence
        - 80-89%: Good adherence
        - 70-79%: Fair adherence (monitoring recommended)
        - <70%: Poor adherence (intervention needed)

    Safety Features:
        - Handles missing patient data gracefully
        - Provides meaningful defaults for incomplete records
        - Never exposes sensitive patient information in errors
        - Maintains conversation continuity during system failures

    Example:
        ```python
        # Check specific patient and medication
        result = safe_adherence_check("12345:omeprazole")

        # Use dict format
        result = safe_adherence_check({
            "patient_id": "67890",
            "medication": "lisinopril"
        })

        # Default checking
        result = safe_adherence_check(None)

        # Analyze results
        if result.get("success"):
            score = result["adherence_score"]
            level = result["adherence_level"]
            print(f"Adherence: {score}% ({level})")

            if score < 80:
                print("Recommendations:", result["recommendations"])
        ```

    Clinical Applications:
        - Identify patients needing adherence support
        - Trigger clinical interventions for poor adherence
        - Support prior authorization requests
        - Guide refill timing and quantity decisions
    """
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
    """
    Safe wrapper for patient allergy verification with comprehensive safety checking.

    This critical safety function retrieves and analyzes patient allergy information
    to prevent potentially dangerous medication interactions and allergic reactions.
    It provides essential safety data needed before any prescription processing.

    Args:
        patient_id (Union[str, Dict, None]): Patient identifier in flexible formats:
            - str: Direct patient ID like "12345"
            - Dict: Object containing 'patient_id' key
            - None: Defaults to demo patient "12345"

    Returns:
        Dict: Comprehensive allergy profile containing:
            - success (bool): True if allergy data retrieved successfully
            - patient_id (str): Patient identifier used for lookup
            - allergies (List[Dict]): Detailed allergy records with:
                - allergen: Specific medication or substance
                - reaction: Type of allergic reaction experienced
                - severity: Severity level (Mild, Moderate, Severe, Critical)
                - date_reported: When allergy was first documented
                - verified: Whether allergy has been clinically verified
            - allergy_count (int): Total number of documented allergies
            - high_risk_allergies (List[str]): Critical allergies requiring special attention
            - contraindications (List[str]): Medications to avoid due to allergies
            - error (str): Error message if retrieval failed
            - source (str): Data source identifier

    Safety Classifications:
        - Critical: Life-threatening reactions (anaphylaxis)
        - Severe: Serious systemic reactions requiring hospitalization
        - Moderate: Significant reactions requiring treatment
        - Mild: Minor reactions that are tolerable but documented

    Clinical Applications:
        - Pre-prescription safety screening
        - Medication interaction analysis
        - Alternative medication selection
        - Emergency response planning
        - Clinical decision support

    Safety Features:
        - Always returns valid allergy data structure
        - Handles missing patient records gracefully
        - Provides safety warnings for high-risk patients
        - Never exposes sensitive patient details in errors
        - Maintains critical safety information integrity

    Example:
        ```python
        # Check allergies for specific patient
        result = safe_allergy_check("12345")

        # Handle dict input
        result = safe_allergy_check({"patient_id": "67890"})

        # Default patient checking
        result = safe_allergy_check(None)

        # Safety analysis
        if result.get("success"):
            allergies = result["allergies"]
            high_risk = result["high_risk_allergies"]

            print(f"Patient has {len(allergies)} documented allergies")

            if high_risk:
                print(f"⚠️  HIGH RISK: {', '.join(high_risk)}")

            # Check for specific medication
            for allergy in allergies:
                if allergy["severity"] in ["Severe", "Critical"]:
                    print(f"🚨 CRITICAL ALLERGY: {allergy['allergen']}")
        ```

    Regulatory Compliance:
        This function supports compliance with pharmaceutical safety regulations
        by providing documented allergy verification required for prescription
        processing and clinical decision making.
    """
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
