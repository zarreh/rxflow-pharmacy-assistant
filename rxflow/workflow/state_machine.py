"""
Advanced State Machine for Pharmacy Refill Workflow
Manages conversation flow, state transitions, and context persistence
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from .workflow_types import ConversationContext, RefillState, ToolResult


@dataclass
class StateTransition:
    """Defines a state transition with conditions and actions"""

    from_state: RefillState
    to_state: RefillState
    trigger: str
    condition: Optional[Callable[[ConversationContext], bool]] = None
    action: Optional[Callable[[ConversationContext], ConversationContext]] = None
    description: str = ""
    required_data: List[str] = field(default_factory=list)

    def can_transition(self, context: ConversationContext) -> bool:
        """Check if transition is valid given current context"""
        if self.condition:
            return self.condition(context)
        return True

    def execute_action(self, context: ConversationContext) -> ConversationContext:
        """Execute transition action if defined"""
        if self.action:
            return self.action(context)
        return context


@dataclass
class StateDefinition:
    """Defines a state with its properties and behaviors"""

    state: RefillState
    description: str
    entry_actions: List[Callable[[ConversationContext], ConversationContext]] = field(
        default_factory=list
    )
    exit_actions: List[Callable[[ConversationContext], ConversationContext]] = field(
        default_factory=list
    )
    required_tools: List[str] = field(default_factory=list)
    required_data: List[str] = field(default_factory=list)
    timeout_seconds: Optional[int] = None
    is_terminal: bool = False

    def enter_state(self, context: ConversationContext) -> ConversationContext:
        """Execute entry actions when entering this state"""
        for action in self.entry_actions:
            context = action(context)
        return context

    def exit_state(self, context: ConversationContext) -> ConversationContext:
        """Execute exit actions when leaving this state"""
        for action in self.exit_actions:
            context = action(context)
        return context


class RefillStateMachine:
    """
    Advanced state machine for pharmacy refill workflow

    Manages state transitions, context persistence, and workflow validation
    """

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.sessions: Dict[str, ConversationContext] = {}
        self.state_history: Dict[str, List[Tuple[RefillState, datetime, str]]] = {}

        # Initialize state definitions and transitions
        self._initialize_states()
        self._initialize_transitions()
        self._validate_state_machine()

    def _initialize_states(self) -> None:
        """Define all workflow states with their properties"""
        self.states = {
            RefillState.START: StateDefinition(
                state=RefillState.START,
                description="Initial state - gather basic patient intent",
                required_tools=[],
                required_data=[],
                timeout_seconds=300,
            ),
            RefillState.IDENTIFY_MEDICATION: StateDefinition(
                state=RefillState.IDENTIFY_MEDICATION,
                description="Extract and identify specific medication from user input",
                required_tools=[
                    "patient_medication_history",
                    "rxnorm_medication_lookup",
                ],
                required_data=["patient_id"],
                timeout_seconds=180,
            ),
            RefillState.CLARIFY_MEDICATION: StateDefinition(
                state=RefillState.CLARIFY_MEDICATION,
                description="Resolve ambiguous medication references",
                required_tools=["patient_medication_history"],
                required_data=["patient_id", "medication_candidates"],
                timeout_seconds=240,
            ),
            RefillState.CONFIRM_DOSAGE: StateDefinition(
                state=RefillState.CONFIRM_DOSAGE,
                description="Verify medication dosage and perform safety checks",
                required_tools=[
                    "verify_medication_dosage",
                    "check_drug_interactions",
                    "patient_allergies",
                ],
                required_data=["medication", "patient_id"],
                timeout_seconds=300,
            ),
            RefillState.CHECK_AUTHORIZATION: StateDefinition(
                state=RefillState.CHECK_AUTHORIZATION,
                description="Verify insurance coverage and prior authorization requirements",
                required_tools=[
                    "insurance_formulary_check",
                    "prior_authorization_lookup",
                ],
                required_data=["medication", "dosage", "insurance_info"],
                timeout_seconds=180,
            ),
            RefillState.SELECT_PHARMACY: StateDefinition(
                state=RefillState.SELECT_PHARMACY,
                description="Find and compare pharmacy options for optimal choice",
                required_tools=[
                    "find_nearby_pharmacies",
                    "check_pharmacy_inventory",
                    "goodrx_price_lookup",
                ],
                required_data=["medication", "dosage"],
                timeout_seconds=240,
            ),
            RefillState.CONFIRM_ORDER: StateDefinition(
                state=RefillState.CONFIRM_ORDER,
                description="Final confirmation before submitting refill order",
                required_tools=["submit_refill_order"],
                required_data=["medication", "dosage", "pharmacy", "patient_id"],
                timeout_seconds=300,
            ),
            RefillState.ESCALATE_PA: StateDefinition(
                state=RefillState.ESCALATE_PA,
                description="Handle prior authorization requirements",
                required_tools=["prior_authorization_lookup"],
                required_data=["medication", "insurance_info"],
                timeout_seconds=600,  # PA can take longer
                is_terminal=False,  # Can return to normal flow
            ),
            RefillState.COMPLETE: StateDefinition(
                state=RefillState.COMPLETE,
                description="Successful completion of refill process",
                required_tools=[],
                required_data=["order_details"],
                is_terminal=True,
            ),
            RefillState.ERROR: StateDefinition(
                state=RefillState.ERROR,
                description="Error state for handling failures and recovery",
                required_tools=[],
                required_data=["error_message"],
                timeout_seconds=180,
                is_terminal=False,  # Can recover from errors
            ),
        }

    def _initialize_transitions(self) -> None:
        """Define all valid state transitions with conditions"""
        self.transitions: List[StateTransition] = [
            # From START
            StateTransition(
                RefillState.START,
                RefillState.IDENTIFY_MEDICATION,
                trigger="medication_request",
                condition=lambda ctx: bool(ctx.patient_id),
                description="User requests medication refill",
            ),
            StateTransition(
                RefillState.START,
                RefillState.ERROR,
                trigger="invalid_input",
                description="Invalid or unclear initial input",
            ),
            # From IDENTIFY_MEDICATION
            StateTransition(
                RefillState.IDENTIFY_MEDICATION,
                RefillState.CLARIFY_MEDICATION,
                trigger="ambiguous_medication",
                condition=lambda ctx: ctx.medication is None
                or ctx.medication.get("ambiguous", False),
                description="Medication name is ambiguous or unclear",
            ),
            StateTransition(
                RefillState.IDENTIFY_MEDICATION,
                RefillState.CONFIRM_DOSAGE,
                trigger="medication_identified",
                condition=lambda ctx: ctx.medication is not None
                and not ctx.medication.get("ambiguous", False),
                description="Medication successfully identified",
            ),
            StateTransition(
                RefillState.IDENTIFY_MEDICATION,
                RefillState.ERROR,
                trigger="medication_not_found",
                description="Medication not found in patient history or database",
            ),
            # From CLARIFY_MEDICATION
            StateTransition(
                RefillState.CLARIFY_MEDICATION,
                RefillState.CONFIRM_DOSAGE,
                trigger="medication_clarified",
                condition=lambda ctx: ctx.medication is not None
                and not ctx.medication.get("ambiguous", False),
                description="Medication successfully clarified",
            ),
            StateTransition(
                RefillState.CLARIFY_MEDICATION,
                RefillState.ERROR,
                trigger="clarification_failed",
                description="Unable to resolve medication ambiguity",
            ),
            # From CONFIRM_DOSAGE
            StateTransition(
                RefillState.CONFIRM_DOSAGE,
                RefillState.CHECK_AUTHORIZATION,
                trigger="dosage_confirmed",
                condition=lambda ctx: ctx.dosage is not None
                and not (ctx.medication and ctx.medication.get("safety_issues", False)),
                description="Dosage confirmed and safety checks passed",
            ),
            StateTransition(
                RefillState.CONFIRM_DOSAGE,
                RefillState.ERROR,
                trigger="safety_concern",
                condition=lambda ctx: bool(
                    ctx.medication and ctx.medication.get("safety_issues", False)
                ),
                description="Safety concerns identified (allergies, interactions)",
            ),
            # From CHECK_AUTHORIZATION
            StateTransition(
                RefillState.CHECK_AUTHORIZATION,
                RefillState.SELECT_PHARMACY,
                trigger="authorized",
                condition=lambda ctx: not ctx.insurance_info.get(
                    "prior_auth_required", False
                )
                if ctx.insurance_info
                else True,
                description="Medication authorized by insurance",
            ),
            StateTransition(
                RefillState.CHECK_AUTHORIZATION,
                RefillState.ESCALATE_PA,
                trigger="prior_auth_required",
                condition=lambda ctx: ctx.insurance_info.get(
                    "prior_auth_required", False
                )
                if ctx.insurance_info
                else False,
                description="Prior authorization required",
            ),
            # From SELECT_PHARMACY
            StateTransition(
                RefillState.SELECT_PHARMACY,
                RefillState.CONFIRM_ORDER,
                trigger="pharmacy_selected",
                condition=lambda ctx: ctx.pharmacy is not None,
                description="Pharmacy selected by patient",
            ),
            StateTransition(
                RefillState.SELECT_PHARMACY,
                RefillState.ERROR,
                trigger="no_pharmacy_available",
                description="No pharmacies available or have medication in stock",
            ),
            # From CONFIRM_ORDER
            StateTransition(
                RefillState.CONFIRM_ORDER,
                RefillState.COMPLETE,
                trigger="order_confirmed",
                condition=lambda ctx: ctx.order_details is not None,
                description="Order successfully confirmed and submitted",
            ),
            StateTransition(
                RefillState.CONFIRM_ORDER,
                RefillState.SELECT_PHARMACY,
                trigger="change_pharmacy",
                description="Patient wants to change pharmacy selection",
            ),
            StateTransition(
                RefillState.CONFIRM_ORDER,
                RefillState.ERROR,
                trigger="order_failed",
                description="Order submission failed",
            ),
            # From ESCALATE_PA
            StateTransition(
                RefillState.ESCALATE_PA,
                RefillState.SELECT_PHARMACY,
                trigger="pa_approved",
                condition=lambda ctx: ctx.insurance_info.get("pa_status") == "approved"
                if ctx.insurance_info
                else False,
                description="Prior authorization approved",
            ),
            StateTransition(
                RefillState.ESCALATE_PA,
                RefillState.ERROR,
                trigger="pa_denied",
                condition=lambda ctx: ctx.insurance_info.get("pa_status") == "denied"
                if ctx.insurance_info
                else False,
                description="Prior authorization denied",
            ),
            # From ERROR - Recovery paths
            StateTransition(
                RefillState.ERROR,
                RefillState.START,
                trigger="restart_conversation",
                description="Start over from the beginning",
            ),
            StateTransition(
                RefillState.ERROR,
                RefillState.IDENTIFY_MEDICATION,
                trigger="retry_medication",
                description="Try medication identification again",
            ),
            StateTransition(
                RefillState.ERROR,
                RefillState.CLARIFY_MEDICATION,
                trigger="retry_clarification",
                description="Try medication clarification again",
            ),
        ]

        # Build transition lookup for efficient access
        self.transition_map: Dict[RefillState, Dict[str, StateTransition]] = {}
        for transition in self.transitions:
            if transition.from_state not in self.transition_map:
                self.transition_map[transition.from_state] = {}
            self.transition_map[transition.from_state][transition.trigger] = transition

    def _validate_state_machine(self) -> None:
        """Validate state machine configuration"""
        issues = []

        # Check all states are defined
        for state in RefillState:
            if state not in self.states:
                issues.append(f"State {state} not defined")

        # Check transition validity
        for transition in self.transitions:
            if transition.from_state not in self.states:
                issues.append(
                    f"Transition from undefined state: {transition.from_state}"
                )
            if transition.to_state not in self.states:
                issues.append(f"Transition to undefined state: {transition.to_state}")

        # Check for unreachable states (except START)
        reachable_states = {RefillState.START}
        for transition in self.transitions:
            reachable_states.add(transition.to_state)

        for state in RefillState:
            if state != RefillState.START and state not in reachable_states:
                issues.append(f"Unreachable state: {state}")

        if issues:
            self.logger.warning(f"State machine validation issues: {issues}")
        else:
            self.logger.info("State machine validation passed")

    def create_session(
        self, session_id: str, patient_id: str = "12345"
    ) -> ConversationContext:
        """Create new conversation session"""
        context = ConversationContext(
            session_id=session_id,
            current_state=RefillState.START,
            patient_id=patient_id,
        )

        self.sessions[session_id] = context
        self.state_history[session_id] = [
            (RefillState.START, datetime.now(), "Session created")
        ]

        self.logger.info(f"Created session {session_id} for patient {patient_id}")
        return context

    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Get existing session context"""
        return self.sessions.get(session_id)

    def transition(
        self, session_id: str, trigger: str, **kwargs
    ) -> Tuple[bool, Optional[ConversationContext], Optional[str]]:
        """
        Attempt state transition

        Returns:
            (success, updated_context, error_message)
        """
        context = self.get_session(session_id)
        if not context:
            return False, None, f"Session {session_id} not found"

        current_state = context.current_state

        # Find valid transition
        if current_state not in self.transition_map:
            return False, context, f"No transitions defined from state {current_state}"

        if trigger not in self.transition_map[current_state]:
            available_triggers = list(self.transition_map[current_state].keys())
            return (
                False,
                context,
                f"Invalid trigger '{trigger}' from {current_state}. Available: {available_triggers}",
            )

        transition = self.transition_map[current_state][trigger]

        # Update context with any provided data BEFORE checking conditions
        for key, value in kwargs.items():
            if hasattr(context, key):
                setattr(context, key, value)

        # Check transition conditions
        if not transition.can_transition(context):
            return (
                False,
                context,
                f"Transition condition failed for {trigger} from {current_state}",
            )

        # Execute exit actions for current state
        old_state_def = self.states[current_state]
        context = old_state_def.exit_state(context)

        # Execute transition action
        context = transition.execute_action(context)

        # Update state
        context.current_state = transition.to_state

        # Execute entry actions for new state
        new_state_def = self.states[transition.to_state]
        context = new_state_def.enter_state(context)

        # Update session and history
        self.sessions[session_id] = context
        self.state_history[session_id].append(
            (
                transition.to_state,
                datetime.now(),
                f"{trigger}: {transition.description}",
            )
        )

        self.logger.info(
            f"Session {session_id}: {current_state} -> {transition.to_state} via '{trigger}'"
        )

        return True, context, None

    def get_valid_triggers(self, session_id: str) -> List[str]:
        """Get valid triggers for current state"""
        context = self.get_session(session_id)
        if not context:
            return []

        current_state = context.current_state
        if current_state not in self.transition_map:
            return []

        # Return triggers where conditions are met
        valid_triggers = []
        for trigger, transition in self.transition_map[current_state].items():
            if transition.can_transition(context):
                valid_triggers.append(trigger)

        return valid_triggers

    def get_required_data(self, session_id: str) -> List[str]:
        """Get required data for current state"""
        context = self.get_session(session_id)
        if not context:
            return []

        state_def = self.states[context.current_state]
        return state_def.required_data

    def get_required_tools(self, session_id: str) -> List[str]:
        """Get required tools for current state"""
        context = self.get_session(session_id)
        if not context:
            return []

        state_def = self.states[context.current_state]
        return state_def.required_tools

    def is_terminal_state(self, session_id: str) -> bool:
        """Check if session is in terminal state"""
        context = self.get_session(session_id)
        if not context:
            return True

        state_def = self.states[context.current_state]
        return state_def.is_terminal

    def get_state_history(
        self, session_id: str
    ) -> List[Tuple[RefillState, datetime, str]]:
        """Get state transition history for session"""
        return self.state_history.get(session_id, [])

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        context = self.get_session(session_id)
        if not context:
            return {"error": f"Session {session_id} not found"}

        history = self.get_state_history(session_id)
        current_state_def = self.states[context.current_state]

        return {
            "session_id": session_id,
            "current_state": context.current_state.value,
            "patient_id": context.patient_id,
            "is_terminal": current_state_def.is_terminal,
            "valid_triggers": self.get_valid_triggers(session_id),
            "required_tools": current_state_def.required_tools,
            "required_data": current_state_def.required_data,
            "context_data": context.to_dict(),
            "state_history": [
                {
                    "state": state.value,
                    "timestamp": timestamp.isoformat(),
                    "description": description,
                }
                for state, timestamp, description in history
            ],
            "total_transitions": len(history) - 1,
        }

    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Remove expired sessions from memory"""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, history in self.state_history.items():
            if history:
                last_activity = history[-1][1]
                age_hours = (current_time - last_activity).total_seconds() / 3600
                if age_hours > max_age_hours:
                    expired_sessions.append(session_id)

        for session_id in expired_sessions:
            self.sessions.pop(session_id, None)
            self.state_history.pop(session_id, None)
            self.logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)

    def export_session_data(self, session_id: str) -> Optional[str]:
        """Export session data as JSON for persistence"""
        summary = self.get_session_summary(session_id)
        if "error" in summary:
            return None

        return json.dumps(summary, indent=2)

    def get_workflow_diagram(self) -> str:
        """Generate Mermaid diagram of the workflow"""
        lines = ["graph TD"]

        # Add states
        for state in RefillState:
            state_def = self.states[state]
            shape = "((" if state_def.is_terminal else "["
            end_shape = "))" if state_def.is_terminal else "]"
            lines.append(
                f"    {state.value}{shape}{state.value.replace('_', ' ').title()}{end_shape}"
            )

        # Add transitions
        for transition in self.transitions:
            lines.append(
                f"    {transition.from_state.value} -->|{transition.trigger}| {transition.to_state.value}"
            )

        return "\n".join(lines)

    # Legacy methods for backward compatibility
    @property
    def current_state(self) -> Optional[ConversationContext]:
        """Get current state for default session"""
        return self.get_session("default")

    def get_state_handler(self) -> str:
        """Get the handler method name for current state"""
        context = self.get_session("default")
        if context:
            return f"handle_{context.current_state.value}"
        return "handle_start"

    def is_complete(self) -> bool:
        """Check if workflow is complete for default session"""
        return self.is_terminal_state("default")
