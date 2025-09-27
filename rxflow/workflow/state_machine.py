"""State machine for pharmacy refill workflow"""
from enum import Enum
from typing import Dict, Optional, Callable
import logging

class RefillState(Enum):
    """States in the refill workflow"""
    START = "start"
    IDENTIFY_MEDICATION = "identify_medication"
    CLARIFY_MEDICATION = "clarify_medication"
    CONFIRM_DOSAGE = "confirm_dosage"
    CHECK_AUTHORIZATION = "check_authorization"
    SELECT_PHARMACY = "select_pharmacy"
    CONFIRM_ORDER = "confirm_order"
    ESCALATE_PA = "escalate_pa"
    COMPLETE = "complete"

class RefillStateMachine:
    """Manages conversation state transitions"""
    
    def __init__(self):
        self.current_state = RefillState.START
        self.context = {}
        self.transitions = self._define_transitions()
        self.logger = logging.getLogger(__name__)
    
    def _define_transitions(self) -> Dict:
        """Define valid state transitions"""
        return {
            RefillState.START: {
                "medication_mentioned": RefillState.IDENTIFY_MEDICATION,
                "greeting": RefillState.START
            },
            RefillState.IDENTIFY_MEDICATION: {
                "medication_found": RefillState.CONFIRM_DOSAGE,
                "medication_ambiguous": RefillState.CLARIFY_MEDICATION,
                "medication_not_found": RefillState.START
            },
            RefillState.CLARIFY_MEDICATION: {
                "medication_clarified": RefillState.CONFIRM_DOSAGE,
                "still_ambiguous": RefillState.CLARIFY_MEDICATION
            },
            RefillState.CONFIRM_DOSAGE: {
                "dosage_confirmed": RefillState.CHECK_AUTHORIZATION,
                "dosage_missing": RefillState.CONFIRM_DOSAGE
            },
            RefillState.CHECK_AUTHORIZATION: {
                "no_pa_required": RefillState.SELECT_PHARMACY,
                "pa_required": RefillState.ESCALATE_PA
            },
            RefillState.SELECT_PHARMACY: {
                "pharmacy_selected": RefillState.CONFIRM_ORDER,
                "need_more_options": RefillState.SELECT_PHARMACY
            },
            RefillState.CONFIRM_ORDER: {
                "order_confirmed": RefillState.COMPLETE,
                "order_cancelled": RefillState.START
            },
            RefillState.ESCALATE_PA: {
                "pa_approved": RefillState.COMPLETE,
                "pa_declined": RefillState.START
            }
        }
    
    def transition(self, trigger: str) -> bool:
        """Transition to next state based on trigger"""
        if self.current_state not in self.transitions:
            return False
        
        next_state = self.transitions[self.current_state].get(trigger)
        if next_state:
            self.logger.info(f"State transition: {self.current_state.value} -> {next_state.value} (trigger: {trigger})")
            self.current_state = next_state
            return True
        
        self.logger.warning(f"Invalid transition: {self.current_state.value} with trigger {trigger}")
        return False
    
    def get_state_handler(self) -> str:
        """Get the handler method name for current state"""
        return f"handle_{self.current_state.value}"
    
    def is_complete(self) -> bool:
        """Check if workflow is complete"""
        return self.current_state == RefillState.COMPLETE
