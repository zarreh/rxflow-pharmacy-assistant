"""
State definitions for RxFlow Pharmacy Assistant workflow
"""

from typing import Dict, List, Optional, TypedDict, Any
from enum import Enum


class InteractionRisk(Enum):
    """Drug interaction risk levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"


class FormularyStatus(Enum):
    """Insurance formulary coverage status"""
    COVERED = "covered"
    NOT_COVERED = "not_covered"
    PRIOR_AUTH_REQUIRED = "prior_auth_required"
    STEP_THERAPY_REQUIRED = "step_therapy_required"


class RefillState(TypedDict):
    """Main state object for the refill workflow"""
    
    # Patient Information
    patient_id: str
    insurance_id: str
    
    # Medication Information
    medication_input: str  # Original user input
    medication_name: Optional[str]
    medication_strength: Optional[str]
    medication_form: Optional[str]
    rxnorm_code: Optional[str]
    quantity: Optional[int]
    days_supply: Optional[int]
    
    # Prescription Status
    prescription_id: Optional[str]
    refills_remaining: Optional[int]
    last_fill_date: Optional[str]
    prescriber_name: Optional[str]
    
    # Safety Checks
    interaction_score: Optional[float]
    interaction_risk: Optional[InteractionRisk]
    interaction_details: Optional[List[str]]
    
    # Insurance & Cost
    formulary_status: Optional[FormularyStatus]
    insurance_copay: Optional[float]
    cash_price: Optional[float]
    prior_auth_required: bool
    
    # Alternatives & Optimization
    generic_available: bool
    generic_name: Optional[str]
    alternatives: List[Dict[str, Any]]
    cost_optimized_option: Optional[Dict[str, Any]]
    
    # Pharmacy Selection
    user_location: Optional[Dict[str, float]]  # {"lat": float, "lon": float}
    available_pharmacies: List[Dict[str, Any]]
    selected_pharmacy: Optional[Dict[str, Any]]
    pickup_time: Optional[str]
    
    # User Interactions & Consents
    user_consents: Dict[str, bool]  # Track user approvals
    pending_user_input: Optional[str]  # What we're waiting for from user
    
    # Workflow Control
    current_step: str
    conversation_history: List[Dict[str, str]]
    error_messages: List[str]
    escalation_required: bool
    escalation_type: Optional[str]  # "pharmacist", "provider", "prior_auth"
    
    # Final Results
    order_confirmation: Optional[str]
    estimated_savings: Optional[float]
    workflow_complete: bool


# Helper function to create initial state
def create_initial_state(
    patient_id: str = "patient_001",
    insurance_id: str = "BCBS_TX_001",
    medication_input: str = ""
) -> RefillState:
    """Create initial state for the refill workflow"""
    return RefillState(
        # Patient Information
        patient_id=patient_id,
        insurance_id=insurance_id,
        
        # Medication Information
        medication_input=medication_input,
        medication_name=None,
        medication_strength=None,
        medication_form=None,
        rxnorm_code=None,
        quantity=None,
        days_supply=None,
        
        # Prescription Status
        prescription_id=None,
        refills_remaining=None,
        last_fill_date=None,
        prescriber_name=None,
        
        # Safety Checks
        interaction_score=None,
        interaction_risk=None,
        interaction_details=None,
        
        # Insurance & Cost
        formulary_status=None,
        insurance_copay=None,
        cash_price=None,
        prior_auth_required=False,
        
        # Alternatives & Optimization
        generic_available=False,
        generic_name=None,
        alternatives=[],
        cost_optimized_option=None,
        
        # Pharmacy Selection
        user_location=None,
        available_pharmacies=[],
        selected_pharmacy=None,
        pickup_time=None,
        
        # User Interactions & Consents
        user_consents={},
        pending_user_input=None,
        
        # Workflow Control
        current_step="input_parser",
        conversation_history=[],
        error_messages=[],
        escalation_required=False,
        escalation_type=None,
        
        # Final Results
        order_confirmation=None,
        estimated_savings=None,
        workflow_complete=False
    )