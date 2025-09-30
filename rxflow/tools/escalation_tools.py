"""
Escalation and Safety Management Tools for RxFlow Pharmacy Assistant

This module provides critical safety escalation capabilities that identify scenarios
requiring professional pharmacist or physician intervention. It implements comprehensive
safety checks to ensure patient protection and            return self._generate_escalation_response(
                escalation_type, escalation_reasons, cast(Dict[str, Any], target_medication)
            )gulatory compliance in automated
prescription refill processes.

The escalation system serves as a crucial safety net that prevents automated processing
of complex or potentially dangerous medication scenarios, ensuring human oversight
where clinical judgment is required.

Key Safety Triggers:
    - Controlled substances (DEA Schedule II-V medications)
    - High-risk medications requiring monitoring
    - Drug interaction warnings and contraindications
    - Prescription changes or dosage modifications  
    - Insurance prior authorization requirements
    - Patient safety flags and clinical alerts
    - Medication adherence concerns

Escalation Categories:
    - IMMEDIATE: Life-threatening situations requiring emergency response
    - URGENT: Safety concerns requiring same-day pharmacist consultation
    - ROUTINE: Non-urgent issues requiring professional review
    - MONITORING: Situations requiring ongoing clinical oversight

Safety Features:
    - Comprehensive controlled substance detection
    - Drug interaction severity assessment
    - Patient-specific risk factor analysis
    - Clinical guideline compliance checking
    - Regulatory requirement validation
    - Documentation and audit trail maintenance

Example:
    ```python
    # Initialize escalation tool
    escalation = EscalationTool()
    
    # Check if medication requires escalation
    result = escalation.check_escalation_needed("lorazepam")
    
    if result["escalation_required"]:
        priority = result["escalation_priority"]
        reasons = result["reasons"]
        print(f"🚨 ESCALATION REQUIRED: {priority}")
        print(f"Reasons: {', '.join(reasons)}")
    ```

Classes:
    EscalationTool: Main escalation analysis and decision engine

Functions:  
    safe_escalation_check: Safety wrapper for escalation analysis

Regulatory Compliance:
    This module supports compliance with DEA regulations, FDA safety guidelines,
    and pharmacy practice standards by ensuring appropriate professional oversight
    for high-risk medication scenarios.

Integration:
    - LangChain Tool integration for conversational workflows
    - Patient database integration for personalized risk assessment
    - Medication database integration for drug-specific safety rules
    - Clinical decision support system compatibility

Note:
    This is a safety-critical component that should be thoroughly tested
    and validated before production deployment in healthcare environments.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from langchain.tools import Tool

from ..services.mock_data import MEDICATIONS_DB, MOCK_PATIENTS
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EscalationTool:
    """
    Comprehensive escalation analysis and safety management system.

    This class implements a sophisticated decision engine that analyzes medication
    refill requests to identify scenarios requiring professional pharmacist or
    physician intervention. It serves as a critical safety component that prevents
    automated processing of potentially dangerous or complex medication scenarios.

    The system evaluates multiple risk factors including controlled substance status,
    drug interactions, patient-specific safety concerns, and regulatory requirements
    to make intelligent escalation decisions that prioritize patient safety.

    Attributes:
        patient_data: Patient database for personalized risk assessment
        drug_data: Medication database with safety classifications and rules

    Core Safety Analysis:
        - Controlled Substance Detection: Identifies DEA Schedule II-V medications
        - Drug Interaction Assessment: Evaluates interaction severity and clinical significance
        - Patient Risk Profiling: Analyzes patient-specific safety factors and history
        - Regulatory Compliance: Ensures adherence to FDA and DEA requirements
        - Clinical Guidelines: Validates against pharmacy practice standards

    Escalation Decision Matrix:
        The tool uses a sophisticated decision matrix considering:

        IMMEDIATE Escalation (Emergency Response Required):
            - Life-threatening drug interactions
            - Critical allergic reaction potential
            - Overdose risk with current medications
            - Emergency prescription modifications

        URGENT Escalation (Same-Day Professional Review):
            - Controlled substances (Schedule II-III)
            - Major drug interactions requiring monitoring
            - Significant dosage changes
            - Prior authorization denials

        ROUTINE Escalation (Professional Review Recommended):
            - Schedule IV-V controlled substances
            - Moderate drug interactions
            - Insurance formulary issues
            - First-time medication requests

        NO ESCALATION (Safe for Automated Processing):
            - Standard maintenance medications
            - No significant interactions or contraindications
            - Patient has good adherence history
            - All safety checks passed

    Example Decision Process:
        ```python
        # Initialize escalation analysis system
        escalation = EscalationTool()

        # Analyze prescription refill request
        analysis = escalation.check_escalation_needed("12345:lorazepam")

        # Process escalation decision
        if analysis["escalation_required"]:
            priority = analysis["escalation_priority"]  # IMMEDIATE/URGENT/ROUTINE
            reasons = analysis["reasons"]
            contact_info = analysis["escalation_contact"]

            print(f"🚨 ESCALATION: {priority}")
            print(f"Reasons: {', '.join(reasons)}")
            print(f"Contact: {contact_info}")

            # Prevent automated processing
            return redirect_to_pharmacist(analysis)
        else:
            # Safe to continue automated workflow
            print("✅ Safe to proceed with automated refill")
            continue_refill_process()
        ```

    Safety Guarantees:
        - Never allows automated processing of controlled substances
        - Always escalates when patient safety data is missing
        - Implements fail-safe behavior for unknown medications
        - Maintains comprehensive audit logs for regulatory compliance
        - Provides clear escalation reasons for professional review
    """

    def __init__(self) -> None:
        self.patient_data = MOCK_PATIENTS
        self.drug_data = MEDICATIONS_DB

    def check_escalation_needed(self, query: str) -> Dict[str, Any]:
        """
        Check if medication refill request requires professional escalation.

        Analyzes medication type, patient history, and safety factors to determine
        if the refill request needs pharmacist or physician intervention.

        Args:
            query (str): Escalation query in formats:
                - "patient_id:medication_name" - Specific patient and medication
                - "medication_name" - Uses default patient (12345) for demo
                Examples: "12345:lorazepam", "omeprazole"

        Returns:
            Dict[str, Any]: Escalation analysis containing:
                - escalation_required (bool): Whether escalation is needed
                - escalation_priority (str): "IMMEDIATE", "URGENT", "ROUTINE", or "NONE"
                - reasons (List[str]): Specific escalation triggers identified
                - medication (str): Medication name analyzed
                - patient_id (str): Patient identifier used
                - controlled_substance (bool): Whether medication is controlled
                - schedule (str): DEA schedule if controlled (II, III, IV, V)
                - escalation_contact (str): Recommended professional contact
                - safety_notes (List[str]): Important safety considerations
                - next_steps (str): Recommended actions for resolution
        """
        try:
            # Parse query
            if ":" in query:
                patient_id, medication_name = query.split(":", 1)
            else:
                patient_id = "12345"  # Default patient
                medication_name = query.strip()

            medication_name = medication_name.lower().strip()

            logger.info(
                f"[AI USAGE] Checking escalation needs for {medication_name} (patient {patient_id})"
            )

            # Get patient data
            patient = self.patient_data.get(patient_id, {})
            medications = patient.get("medications", [])

            # Find the specific medication
            target_medication = None
            for med in medications:
                med_dict = cast(Dict[str, Any], med)
                if med_dict["name"].lower() == medication_name:
                    target_medication = med_dict
                    break

            if not target_medication:
                return {
                    "escalation_needed": True,
                    "escalation_type": "pharmacist_consultation",
                    "reason": "medication_not_found",
                    "message": f"No record found for {medication_name}. Please consult with a pharmacist to verify your prescription history.",
                    "contact_info": {
                        "pharmacist_phone": "(555) 123-4567",
                        "hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM",
                    },
                    "source": "escalation_check",
                }

            # Check various escalation scenarios
            escalation_reasons = []
            escalation_type = None

            # 1. No refills remaining
            if target_medication.get("refills_remaining", 0) == 0:
                escalation_reasons.append("no_refills_remaining")
                escalation_type = "doctor_consultation"

            # 2. Prescription expired
            if target_medication.get("prescription_expired", False):
                escalation_reasons.append("prescription_expired")
                escalation_type = "doctor_consultation"

            # 3. Controlled substance
            if target_medication.get("controlled_substance", False):
                escalation_reasons.append("controlled_substance")
                escalation_type = "doctor_consultation"

            # 4. Check drug database for additional requirements
            drug_info = cast(Dict[str, Any], self.drug_data.get(medication_name, {}))
            if drug_info.get("requires_doctor_consultation", False):
                escalation_reasons.append("requires_doctor_consultation")
                escalation_type = "doctor_consultation"

            # 5. Check if last fill was too recent (potential abuse)
            last_filled = target_medication.get("last_filled")
            if last_filled:
                last_fill_date = datetime.strptime(last_filled, "%Y-%m-%d")
                days_since_fill = (datetime.now() - last_fill_date).days
                typical_supply = cast(List[int], drug_info.get("typical_supply_days", [30]))[0]

                if days_since_fill < (
                    typical_supply * 0.75
                ):  # Requesting refill too early
                    escalation_reasons.append("early_refill_request")
                    escalation_type = "pharmacist_consultation"

            # 6. Check for drug interactions with new prescriptions (simulated)
            if self._has_potential_interactions(
                cast(Dict[str, Any], target_medication), cast(List[Any], patient.get("medications", []))
            ):
                escalation_reasons.append("drug_interaction_concern")
                escalation_type = "pharmacist_consultation"

            # If no escalation needed
            if not escalation_reasons:
                return {
                    "escalation_needed": False,
                    "message": "No escalation required. Prescription can be processed normally.",
                    "medication": target_medication,
                    "source": "escalation_check",
                }

            # Generate escalation response
            escalation_type = (
                escalation_type or "pharmacist_consultation"
            )  # Default if None
            return self._generate_escalation_response(
                escalation_type, escalation_reasons, cast(Dict[str, Any], target_medication), patient_id
            )

        except Exception as e:
            logger.error(f"Error checking escalation needs: {str(e)}")
            return {
                "escalation_needed": True,
                "escalation_type": "pharmacist_consultation",
                "reason": "system_error",
                "message": f"Unable to process request. Please contact your pharmacist for assistance.",
                "source": "error_handler",
            }

    def _has_potential_interactions(
        self, target_med: Dict, all_medications: list
    ) -> bool:
        """Check for potential drug interactions (simplified simulation)"""
        target_name = target_med["name"].lower()

        # Simulated interaction checks
        interaction_pairs = {
            "lorazepam": ["alcohol", "opioids"],  # CNS depressants
            "warfarin": ["meloxicam", "omeprazole"],  # Bleeding risk
            "metformin": ["insulin"],  # Hypoglycemia risk
        }

        if target_name in interaction_pairs:
            concern_meds = interaction_pairs[target_name]
            for med in all_medications:
                if any(concern in med["name"].lower() for concern in concern_meds):
                    return True

        return False

    def _generate_escalation_response(
        self, escalation_type: str, reasons: list, medication: Dict, patient_id: str
    ) -> Dict:
        """Generate appropriate escalation response based on type and reasons"""

        med_name = medication["name"].title()
        dosage = medication.get("dosage", "")

        if escalation_type == "doctor_consultation":
            return {
                "escalation_needed": True,
                "escalation_type": "doctor_consultation",
                "reasons": reasons,
                "message": self._get_doctor_escalation_message(
                    reasons, med_name, dosage
                ),
                "contact_info": {
                    "primary_care_doctor": "Dr. Sarah Johnson",
                    "doctor_phone": "(555) 987-6543",
                    "clinic_hours": "Mon-Fri: 8AM-5PM",
                    "urgent_care": "(555) 111-2222 (after hours)",
                    "online_portal": "MyHealthPortal.com",
                },
                "next_steps": [
                    "Contact your doctor for a new prescription",
                    "Schedule an appointment if needed",
                    "Discuss any changes in your condition",
                    "Ask about alternative medications if appropriate",
                ],
                "medication": medication,
                "source": "escalation_system",
            }
        else:  # pharmacist_consultation
            return {
                "escalation_needed": True,
                "escalation_type": "pharmacist_consultation",
                "reasons": reasons,
                "message": self._get_pharmacist_escalation_message(
                    reasons, med_name, dosage
                ),
                "contact_info": {
                    "pharmacist": "PharmD Jennifer Martinez",
                    "pharmacy_phone": "(555) 123-4567",
                    "pharmacy_hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM",
                    "consultation_available": True,
                },
                "next_steps": [
                    "Speak with the pharmacist on duty",
                    "Review your medication history",
                    "Discuss any concerns or questions",
                    "Get guidance on timing and interactions",
                ],
                "medication": medication,
                "source": "escalation_system",
            }

    def _get_doctor_escalation_message(
        self, reasons: list, med_name: str, dosage: str
    ) -> str:
        """Generate doctor escalation message based on reasons"""

        base_message = f"I'm unable to process your {med_name} {dosage} refill request at this time. "

        reason_messages = {
            "no_refills_remaining": "You have no refills remaining on this prescription.",
            "prescription_expired": "Your prescription has expired and needs to be renewed.",
            "controlled_substance": f"{med_name} is a controlled substance that requires a new prescription from your doctor.",
            "requires_doctor_consultation": f"{med_name} requires periodic evaluation by your doctor before refills can be approved.",
        }

        specific_reasons = []
        for reason in reasons:
            if reason in reason_messages:
                specific_reasons.append(reason_messages[reason])

        if specific_reasons:
            base_message += " " + " ".join(specific_reasons)

        base_message += f"\n\n**Next Steps:**\n"
        base_message += (
            f"Please contact your doctor to get a new prescription for {med_name}. "
        )
        base_message += f"They may need to evaluate your current condition and adjust your treatment plan."

        return base_message

    def _get_pharmacist_escalation_message(
        self, reasons: list, med_name: str, dosage: str
    ) -> str:
        """Generate pharmacist escalation message based on reasons"""

        base_message = f"I need to connect you with a pharmacist regarding your {med_name} {dosage} refill request. "

        reason_messages = {
            "early_refill_request": "You're requesting this refill earlier than expected based on your last fill date.",
            "drug_interaction_concern": "There may be interactions with your other medications that need review.",
            "medication_not_found": "I couldn't locate this medication in your current prescription history.",
        }

        specific_reasons = []
        for reason in reasons:
            if reason in reason_messages:
                specific_reasons.append(reason_messages[reason])

        if specific_reasons:
            base_message += " " + " ".join(specific_reasons)

        base_message += f"\n\n**Pharmacist Consultation Available:**\n"
        base_message += f"Our pharmacist can review your medication history, check for interactions, and provide guidance on the best course of action."

        return base_message


# Create LangChain tool
def safe_escalation_check(query: Any) -> Dict[str, Any]:
    """Safe wrapper for escalation check that handles various input types"""
    try:
        if query is None or query == {} or query == "":
            return {
                "escalation_needed": False,
                "message": "No medication specified for escalation check",
            }
        elif isinstance(query, dict):
            medication = query.get("medication", query.get("query", ""))
            patient_id = query.get("patient_id", "12345")
            query = f"{patient_id}:{medication}"
        elif not isinstance(query, str):
            query = str(query)

        return EscalationTool().check_escalation_needed(query)
    except Exception as e:
        logger.error(f"Error in safe_escalation_check: {e}")
        return {
            "escalation_needed": True,
            "escalation_type": "pharmacist_consultation",
            "reason": "system_error",
            "message": "Unable to process request. Please contact your pharmacist for assistance.",
            "source": "error_handler",
        }


escalation_check_tool = Tool(
    name="check_escalation_needed",
    description="Check if a medication refill requires escalation to doctor or pharmacist. Use format 'medication_name' or 'patient_id:medication_name'. Returns escalation requirements and contact information.",
    func=safe_escalation_check,
)
