"""Shared types and enums for workflow management"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class RefillState(Enum):
    """States in the pharmacy refill workflow"""

    START = "start"
    IDENTIFY_MEDICATION = "identify_medication"
    CLARIFY_MEDICATION = "clarify_medication"
    CONFIRM_DOSAGE = "confirm_dosage"
    CHECK_AUTHORIZATION = "check_authorization"
    SELECT_PHARMACY = "select_pharmacy"
    CONFIRM_ORDER = "confirm_order"
    ESCALATE_PA = "escalate_pa"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ConversationContext:
    """Holds conversation state and data"""

    session_id: str
    current_state: RefillState
    patient_id: str = "12345"  # Mock for demo
    medication: Optional[Dict[str, Any]] = None
    dosage: Optional[str] = None
    pharmacy: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None
    order_details: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "patient_id": self.patient_id,
            "medication": self.medication,
            "dosage": self.dosage,
            "pharmacy": self.pharmacy,
            "insurance_info": self.insurance_info,
            "order_details": self.order_details,
            "error_message": self.error_message,
        }


@dataclass
class ToolResult:
    """Standardized tool response format"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    source: str = "unknown"  # "api", "mock", "cache"


class WorkflowState(Enum):
    """Basic workflow states"""

    GREETING = "greeting"
    PROCESSING = "processing"
    ESCALATED = "escalated"
    COMPLETED = "completed"
    ERROR = "error"
