"""Escalation tools for scenarios requiring doctor or pharmacist consultation."""

from langchain.tools import Tool
from typing import Dict, Optional
from datetime import datetime, timedelta
from ..services.mock_data import MOCK_PATIENTS, MEDICATIONS_DB
from ..utils.logger import get_logger

logger = get_logger(__name__)

class EscalationTool:
    """Handles escalation scenarios for medication refill requests"""
    
    def __init__(self):
        self.patient_data = MOCK_PATIENTS
        self.drug_data = MEDICATIONS_DB
    
    def check_escalation_needed(self, query: str) -> Dict:
        """
        Check if a medication refill request needs escalation to doctor or pharmacist
        Query format: "patient_id:medication_name" or just "medication_name"
        """
        try:
            # Parse query
            if ':' in query:
                patient_id, medication_name = query.split(':', 1)
            else:
                patient_id = "12345"  # Default patient
                medication_name = query.strip()
            
            medication_name = medication_name.lower().strip()
            
            logger.info(f"[AI USAGE] Checking escalation needs for {medication_name} (patient {patient_id})")
            
            # Get patient data
            patient = self.patient_data.get(patient_id, {})
            medications = patient.get("medications", [])
            
            # Find the specific medication
            target_medication = None
            for med in medications:
                if med["name"].lower() == medication_name:
                    target_medication = med
                    break
            
            if not target_medication:
                return {
                    "escalation_needed": True,
                    "escalation_type": "pharmacist_consultation",
                    "reason": "medication_not_found",
                    "message": f"No record found for {medication_name}. Please consult with a pharmacist to verify your prescription history.",
                    "contact_info": {
                        "pharmacist_phone": "(555) 123-4567",
                        "hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM"
                    },
                    "source": "escalation_check"
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
            drug_info = self.drug_data.get(medication_name, {})
            if drug_info.get("requires_doctor_consultation", False):
                escalation_reasons.append("requires_doctor_consultation")
                escalation_type = "doctor_consultation"
            
            # 5. Check if last fill was too recent (potential abuse)
            last_filled = target_medication.get("last_filled")
            if last_filled:
                last_fill_date = datetime.strptime(last_filled, "%Y-%m-%d")
                days_since_fill = (datetime.now() - last_fill_date).days
                typical_supply = drug_info.get("typical_supply_days", [30])[0]
                
                if days_since_fill < (typical_supply * 0.75):  # Requesting refill too early
                    escalation_reasons.append("early_refill_request")
                    escalation_type = "pharmacist_consultation"
            
            # 6. Check for drug interactions with new prescriptions (simulated)
            if self._has_potential_interactions(target_medication, patient.get("medications", [])):
                escalation_reasons.append("drug_interaction_concern")
                escalation_type = "pharmacist_consultation"
            
            # If no escalation needed
            if not escalation_reasons:
                return {
                    "escalation_needed": False,
                    "message": "No escalation required. Prescription can be processed normally.",
                    "medication": target_medication,
                    "source": "escalation_check"
                }
            
            # Generate escalation response
            escalation_type = escalation_type or "pharmacist_consultation"  # Default if None
            return self._generate_escalation_response(
                escalation_type, escalation_reasons, target_medication, patient_id
            )
            
        except Exception as e:
            logger.error(f"Error checking escalation needs: {str(e)}")
            return {
                "escalation_needed": True,
                "escalation_type": "pharmacist_consultation",
                "reason": "system_error",
                "message": f"Unable to process request. Please contact your pharmacist for assistance.",
                "source": "error_handler"
            }
    
    def _has_potential_interactions(self, target_med: Dict, all_medications: list) -> bool:
        """Check for potential drug interactions (simplified simulation)"""
        target_name = target_med["name"].lower()
        
        # Simulated interaction checks
        interaction_pairs = {
            "lorazepam": ["alcohol", "opioids"],  # CNS depressants
            "warfarin": ["meloxicam", "omeprazole"],  # Bleeding risk
            "metformin": ["insulin"]  # Hypoglycemia risk
        }
        
        if target_name in interaction_pairs:
            concern_meds = interaction_pairs[target_name]
            for med in all_medications:
                if any(concern in med["name"].lower() for concern in concern_meds):
                    return True
        
        return False
    
    def _generate_escalation_response(self, escalation_type: str, reasons: list, medication: Dict, patient_id: str) -> Dict:
        """Generate appropriate escalation response based on type and reasons"""
        
        med_name = medication["name"].title()
        dosage = medication.get("dosage", "")
        
        if escalation_type == "doctor_consultation":
            return {
                "escalation_needed": True,
                "escalation_type": "doctor_consultation",
                "reasons": reasons,
                "message": self._get_doctor_escalation_message(reasons, med_name, dosage),
                "contact_info": {
                    "primary_care_doctor": "Dr. Sarah Johnson",
                    "doctor_phone": "(555) 987-6543",
                    "clinic_hours": "Mon-Fri: 8AM-5PM",
                    "urgent_care": "(555) 111-2222 (after hours)",
                    "online_portal": "MyHealthPortal.com"
                },
                "next_steps": [
                    "Contact your doctor for a new prescription",
                    "Schedule an appointment if needed",
                    "Discuss any changes in your condition",
                    "Ask about alternative medications if appropriate"
                ],
                "medication": medication,
                "source": "escalation_system"
            }
        else:  # pharmacist_consultation
            return {
                "escalation_needed": True,
                "escalation_type": "pharmacist_consultation", 
                "reasons": reasons,
                "message": self._get_pharmacist_escalation_message(reasons, med_name, dosage),
                "contact_info": {
                    "pharmacist": "PharmD Jennifer Martinez",
                    "pharmacy_phone": "(555) 123-4567",
                    "pharmacy_hours": "Mon-Fri: 8AM-10PM, Sat-Sun: 9AM-7PM",
                    "consultation_available": True
                },
                "next_steps": [
                    "Speak with the pharmacist on duty",
                    "Review your medication history",
                    "Discuss any concerns or questions",
                    "Get guidance on timing and interactions"
                ],
                "medication": medication,
                "source": "escalation_system"
            }
    
    def _get_doctor_escalation_message(self, reasons: list, med_name: str, dosage: str) -> str:
        """Generate doctor escalation message based on reasons"""
        
        base_message = f"I'm unable to process your {med_name} {dosage} refill request at this time. "
        
        reason_messages = {
            "no_refills_remaining": "You have no refills remaining on this prescription.",
            "prescription_expired": "Your prescription has expired and needs to be renewed.",
            "controlled_substance": f"{med_name} is a controlled substance that requires a new prescription from your doctor.",
            "requires_doctor_consultation": f"{med_name} requires periodic evaluation by your doctor before refills can be approved."
        }
        
        specific_reasons = []
        for reason in reasons:
            if reason in reason_messages:
                specific_reasons.append(reason_messages[reason])
        
        if specific_reasons:
            base_message += " " + " ".join(specific_reasons)
        
        base_message += f"\n\n**Next Steps:**\n"
        base_message += f"Please contact your doctor to get a new prescription for {med_name}. "
        base_message += f"They may need to evaluate your current condition and adjust your treatment plan."
        
        return base_message
    
    def _get_pharmacist_escalation_message(self, reasons: list, med_name: str, dosage: str) -> str:
        """Generate pharmacist escalation message based on reasons"""
        
        base_message = f"I need to connect you with a pharmacist regarding your {med_name} {dosage} refill request. "
        
        reason_messages = {
            "early_refill_request": "You're requesting this refill earlier than expected based on your last fill date.",
            "drug_interaction_concern": "There may be interactions with your other medications that need review.",
            "medication_not_found": "I couldn't locate this medication in your current prescription history."
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
def safe_escalation_check(query):
    """Safe wrapper for escalation checking"""
    try:
        if query is None or query == {} or query == "":
            return {"escalation_needed": False, "message": "No medication specified for escalation check"}
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
            "source": "error_handler"
        }

escalation_check_tool = Tool(
    name="check_escalation_needed",
    description="Check if a medication refill requires escalation to doctor or pharmacist. Use format 'medication_name' or 'patient_id:medication_name'. Returns escalation requirements and contact information.",
    func=safe_escalation_check
)