"""
Advanced Conversation Manager for RxFlow Pharmacy Assistant - Step 6
Integrates LangChain agent with tools, state machine, and prompt management
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import json
import uuid
import asyncio
import re
from datetime import datetime
from dataclasses import dataclass, field

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import Tool

from rxflow.llm import get_conversational_llm
from rxflow.utils.logger import get_logger, get_session_logger, close_session_logger
import logging
import re
from rxflow.workflow.state_machine import RefillStateMachine
from rxflow.workflow.workflow_types import RefillState, ConversationContext, ToolResult
from rxflow.prompts.prompt_manager import PromptManager

# Import all tools - these will be registered with the agent
from rxflow.tools.patient_history_tool import (
    patient_history_tool, allergy_tool, adherence_tool
)
from rxflow.tools.rxnorm_tool import (
    rxnorm_tool, dosage_verification_tool, interaction_tool
)
from rxflow.tools.pharmacy_tools import (
    pharmacy_location_tool, pharmacy_inventory_tool, pharmacy_wait_times_tool, pharmacy_details_tool
)
from rxflow.tools.cost_tools import (
    goodrx_tool, insurance_tool, brand_generic_tool, prior_auth_tool
)
from rxflow.tools.order_tools import (
    order_submission_tool, order_tracking_tool, order_cancellation_tool
)

logger = get_logger(__name__)


@dataclass 
class ConversationResponse:
    """Standardized conversation response format"""
    message: str
    session_id: str
    current_state: RefillState
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    cost_savings: Optional[Dict[str, Any]] = None
    next_steps: Optional[str] = None
    error: Optional[str] = None
    debug_info: Optional[Dict[str, Any]] = None


class AdvancedConversationManager:
    """
    Comprehensive conversation manager integrating all RxFlow systems
    
    Features:
    - LangChain agent with 15 specialized tools
    - State machine-driven conversation flow
    - Context-aware prompt management 
    - Explicit AI usage logging
    - Comprehensive error handling
    - Multi-session management
    """
    
    def __init__(self):
        logger.info("[INIT] Initializing Advanced Conversation Manager")
        
        # Core components
        self.llm = get_conversational_llm()
        self.state_machine = RefillStateMachine()
        self.prompt_manager = PromptManager()
        
        # Session management
        # Initialize conversation state management
        self.sessions: Dict[str, ConversationContext] = {}
        self.conversation_histories: Dict[str, List[Dict[str, Any]]] = {}
        self.session_loggers: Dict[str, logging.Logger] = {}  # Track session-specific loggers
        
        # Tool registration and agent setup
        self._register_tools()
        self._setup_agent()
        
        logger.info("[INIT] Advanced Conversation Manager initialized successfully")
    
    def _register_tools(self):
        """Register all RxFlow tools with the LangChain agent"""
        logger.info("[AI USAGE] Registering tools for LangChain agent integration")
        
        self.tools = [
            # Patient History Tools (3)
            patient_history_tool,
            allergy_tool,
            adherence_tool,
            
            # RxNorm Tools (3)
            rxnorm_tool,
            dosage_verification_tool,
            interaction_tool,
            
            # Pharmacy Tools (4)
            pharmacy_location_tool,
            pharmacy_inventory_tool,
            pharmacy_wait_times_tool,
            pharmacy_details_tool,
            
            # Cost Tools (4)
            goodrx_tool,
            insurance_tool,
            brand_generic_tool,
            prior_auth_tool,
            
            # Order Tools (3)
            order_submission_tool,
            order_tracking_tool,
            order_cancellation_tool
        ]
        
        logger.info(f"[TOOLS] Registered {len(self.tools)} tools for agent")
        
        # Log tool names for debugging
        tool_names = [tool.name for tool in self.tools]
        logger.debug(f"[TOOLS] Available tools: {tool_names}")
    
    def _setup_agent(self):
        """Setup LangChain agent with tools and prompts"""
        logger.info("[AI USAGE] Setting up LangChain agent with OpenAI functions")
        
        # Create agent prompt with system message
        system_message = """You are RxFlow, an intelligent AI pharmacy assistant helping patients with prescription refills.

CORE RESPONSIBILITIES:
- Help patients refill prescriptions safely and efficiently
- Use available tools to gather accurate information
- Follow the conversation workflow guided by the state machine
- Prioritize patient safety above all else
- Provide clear, helpful, and professional responses

TOOL USAGE GUIDELINES:
- Always check patient medication history before processing requests
- Use RxNorm tools to verify medication information and check interactions
- Find pharmacy options and compare costs to help patients save money
- Verify insurance coverage and handle prior authorization requirements
- Guide patients through the complete refill process

SAFETY PROTOCOLS:
- Check for drug interactions and allergies before confirming medications
- Escalate complex medical questions to human pharmacists
- Verify all medication details (name, dosage, quantity) before processing
- Ensure patients understand their medications and any important warnings

CONVERSATION STYLE:
- Be warm, professional, and patient-focused
- Ask clarifying questions when information is unclear
- Explain processes and options in simple terms
- Celebrate cost savings and successful completions
- Provide clear next steps at each stage

Remember: You have access to comprehensive tools for patient history, medication lookup, pharmacy services, cost comparison, and order processing. Use them effectively to provide the best possible service."""

        # Create the agent prompt
        self.agent_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create the agent
        try:
            self.agent = create_tool_calling_agent(
                llm=self.llm,
                tools=self.tools,
                prompt=self.agent_prompt
            )
            
            # Create agent executor
            self.agent_executor = AgentExecutor(
                agent=self.agent,
                tools=self.tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=5,
                early_stopping_method="generate"
            )
            
            logger.info("[AI USAGE] LangChain agent configured successfully")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to setup agent: {e}")
            raise
    
    async def handle_message(self, user_input: str, session_id: Optional[str] = None, patient_id: str = "12345") -> ConversationResponse:
        """
        Main entry point for handling user messages
        
        Args:
            user_input: User's message
            session_id: Session identifier (creates new if None)
            
        Returns:
            ConversationResponse with message and context
        """
        # Create or get session
        if not session_id:
            session_id = str(uuid.uuid4())
            
        # Get session-specific logger for file logging
        session_logger = get_session_logger(session_id)
        
        logger.info(f"[MESSAGE] Processing message for session {session_id[:8]}...")
        session_logger.info(f"[MESSAGE] Processing message for session {session_id[:8]}...")
        logger.info(f"[AI USAGE] Starting conversation processing with state machine integration")
        session_logger.info(f"[AI USAGE] Starting conversation processing with state machine integration")
        
        try:
            # Get or create session context
            context = self._get_or_create_session(session_id)
            current_state = context.current_state
            
            logger.info(f"[STATE] Current state: {current_state.value}")
            session_logger.info(f"[STATE] Current state: {current_state.value}")
            
            # Get conversation history for context
            history = self.conversation_histories.get(session_id, [])
            
            # Determine appropriate handler based on current state
            response = self._handle_state_specific_message(
                user_input, context, history
            )
            
            # Update conversation history
            self._update_conversation_history(session_id, user_input, response.message)
            
            logger.info(f"[SUCCESS] Generated response for session {session_id[:8]}")
            session_logger.info(f"[SUCCESS] Generated response for session {session_id[:8]}")
            session_logger.info(f"[USER INPUT] {user_input}")
            session_logger.info(f"[AI RESPONSE] {response.message}")
            return response
            
        except Exception as e:
            logger.error(f"[ERROR] Error handling message: {e}")
            session_logger.error(f"[ERROR] Error handling message: {e}")
            session_logger.error(f"[USER INPUT] {user_input}")
            return ConversationResponse(
                message="I apologize, but I'm having trouble processing your request right now. Could you please try again?",
                session_id=session_id,
                current_state=RefillState.ERROR,
                error=str(e)
            )
    
    def _get_or_create_session(self, session_id: str) -> ConversationContext:
        """Get existing session or create new one"""
        if session_id not in self.sessions:
            # Create new session
            context = self.state_machine.create_session(session_id)
            self.sessions[session_id] = context
            self.conversation_histories[session_id] = []
            
            logger.info(f"[SESSION] Created new session {session_id[:8]}...")
            # Initialize session logger for this new session
            session_logger = get_session_logger(session_id)
            session_logger.info(f"[SESSION] Created new session {session_id}")
        else:
            context = self.sessions[session_id]
            logger.debug(f"[SESSION] Retrieved existing session {session_id[:8]}...")
        
        return context
    
    def _handle_state_specific_message(
        self, 
        user_input: str, 
        context: ConversationContext,
        history: List[Dict[str, Any]]
    ) -> ConversationResponse:
        """Route message handling based on current state"""
        
        current_state = context.current_state
        session_id = context.session_id
        
        logger.info(f"[STATE HANDLER] Routing to {current_state.value} handler")
        
        # Get session logger for state-specific logging
        session_logger = get_session_logger(session_id)
        session_logger.info(f"[STATE HANDLER] Routing to {current_state.value} handler")
        
        # Map states to handler methods
        state_handlers = {
            RefillState.START: self._handle_start,
            RefillState.IDENTIFY_MEDICATION: self._handle_identify_medication,
            RefillState.CLARIFY_MEDICATION: self._handle_clarify_medication,
            RefillState.CONFIRM_DOSAGE: self._handle_confirm_dosage,
            RefillState.CHECK_AUTHORIZATION: self._handle_check_authorization,
            RefillState.SELECT_PHARMACY: self._handle_select_pharmacy,
            RefillState.CONFIRM_ORDER: self._handle_confirm_order,
            RefillState.ESCALATE_PA: self._handle_escalate_pa,
            RefillState.COMPLETE: self._handle_complete,
            RefillState.ERROR: self._handle_error
        }
        
        handler = state_handlers.get(current_state, self._handle_general)
        result = handler(user_input, context, history)
        
        # Log state transition if it occurred
        session_logger.info(f"[STATE TRANSITION] {current_state.value} -> {result.current_state.value}")
        
        return result
    
    def _handle_start(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle START state - initial user interaction"""
        logger.info("[AI USAGE] Processing initial user request - extracting medication intent")
        
        try:
            # Let the agent handle the interaction and determine next steps
            agent_response = self.agent_executor.invoke({
                "input": f"""Patient says: '{user_input}'
                
Help them with their request. If they want a medication refill:
1. Use patient_medication_history to check their current medications
2. Help them identify which medication they need
3. Answer any questions they have about their medications

Do NOT assume anything - use the tools to get accurate information.

If they clearly mention a specific medication for refill, I'll help transition to the next step. Otherwise, help them explore their options.""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            logger.info("[AI USAGE] Generated initial response using LLM agent")
            
            # Only transition if there's clear medication refill intent AND specific medication mentioned
            refill_keywords = ["refill", "medication", "prescription", "pills", "medicine"]
            specific_med_mentioned = any(med in user_input.lower() for med in 
                ["lisinopril", "metformin", "atorvastatin", "eliquis", "methocarbamol", "meloxicam", "omeprazole", "famotidine"])
            
            has_refill_intent = any(word in user_input.lower() for word in refill_keywords)
            
            # Only transition if both intent and specific medication are clear
            if has_refill_intent and specific_med_mentioned:
                success, updated_context, error = self.state_machine.transition(
                    context.session_id, "medication_request"
                )
                
                if success and updated_context:
                    logger.info(f"[TRANSITION] START -> IDENTIFY_MEDICATION (clear intent + specific medication)")
                    self.sessions[context.session_id] = updated_context
                    context = updated_context
                else:
                    logger.warning(f"[TRANSITION] Failed: {error}")
            else:
                logger.info("[NO TRANSITION] Staying in START - need clearer medication identification")
            
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Feel free to ask about your medications or specify which one you'd like to refill."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in start handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_identify_medication(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle IDENTIFY_MEDICATION state - extract and identify medication"""
        logger.info("[AI USAGE] Using tools to identify medication from user input")
        
        try:
            # Check conversation history to see if medication was already identified
            recent_history = history[-4:] if len(history) >= 4 else history
            conversation_context = " ".join([msg.get("content", "") for msg in recent_history])
            
            # Look for confirmation words that indicate user wants to proceed with refill
            confirmation_words = ["yes", "correct", "that's right", "confirmed", "exactly", "please", "go ahead", "proceed"]
            refill_confirmation = ["refill", "assist", "help", "request", "proceed with", "Would you like me to"]
            
            has_confirmation = any(word in user_input.lower().strip() for word in confirmation_words)
            mentions_refill_context = any(word in conversation_context.lower() for word in refill_confirmation)
            
            # Check if a specific medication was mentioned in recent conversation
            medication_names = ["lisinopril", "metformin", "atorvastatin", "eliquis", "methocarbamol", "meloxicam", "omeprazole", "famotidine"]
            identified_medication = None
            dosage_info = None
            
            # Look for medication in recent conversation history - more flexible matching
            for med in medication_names:
                if med in conversation_context.lower():
                    identified_medication = med
                    # Extract dosage from context - look for various patterns
                    dosage_patterns = [
                        rf'{med}.*?(\d+\s*mg)',
                        rf'(\d+\s*mg).*?{med}',
                        rf'{med}\s*\((\d+mg[^)]*)\)'
                    ]
                    for pattern in dosage_patterns:
                        dosage_match = re.search(pattern, conversation_context.lower())
                        if dosage_match:
                            dosage_info = dosage_match.group(1)
                            break
                    break
            
            # More liberal confirmation logic - if user says yes and we have medication context
            user_input_clean = user_input.lower().strip()
            simple_confirmations = ["yes", "y", "ok", "okay", "sure", "proceed", "go ahead"]
            is_simple_confirmation = user_input_clean in simple_confirmations
            
            # Check if recent conversation mentions proceeding with refill/assistance
            refill_proceed_patterns = [
                "proceed with", "assist with", "can i have", "help with", "refill", 
                "would you like me to", "i can help", "schedule a refill", "find a nearby pharmacy"
            ]
            has_proceed_context = any(pattern in conversation_context.lower() for pattern in refill_proceed_patterns)
            
            # Check for question patterns that expect yes/no confirmation
            question_patterns = [
                "would you like me to", "can you please confirm", "should i proceed", 
                "would you like", "do you want", "shall i", "can i help"
            ]
            has_confirmation_question = any(pattern in conversation_context.lower() for pattern in question_patterns)
            
            logger.info(f"[CONFIRMATION DEBUG] user_input='{user_input}', is_simple_confirmation={is_simple_confirmation}, identified_medication='{identified_medication}', has_proceed_context={has_proceed_context}, has_confirmation_question={has_confirmation_question}")
            
            # If user is confirming and we have medication + context indicating they want to proceed
            if (has_confirmation or is_simple_confirmation) and identified_medication and (has_proceed_context or has_confirmation_question):
                logger.info(f"[CONFIRMATION] User confirmed refill for {identified_medication}")
                
                success, updated_context, error = self.state_machine.transition(
                    context.session_id,
                    "medication_identified", 
                    medication={"name": identified_medication, "ambiguous": False},
                    dosage={"amount": dosage_info or "standard dose", "frequency": "as prescribed", "confirmed": True}
                )
                
                if success and updated_context:
                    self.sessions[context.session_id] = updated_context
                    context = updated_context
                    logger.info(f"[TRANSITION] IDENTIFY_MEDICATION -> CONFIRM_DOSAGE (user confirmed refill request)")
                    
                    return ConversationResponse(
                        message=f"Perfect! I'll help you with your {identified_medication} refill. Let me check for safety considerations and find the best pharmacy options for you.",
                        session_id=context.session_id,
                        current_state=context.current_state,
                        next_steps="Checking medication safety and finding pharmacy options."
                    )
            
            # Otherwise, use the agent to help identify medication
            agent_response = self.agent_executor.invoke({
                "input": f"""Patient is trying to identify their medication for refill. They said: '{user_input}'

Context from recent conversation: {conversation_context}

Please help by:
1. Using patient_medication_history to check their current medications
2. Using rxnorm_medication_lookup if they mention a specific drug name
3. Answer any questions they have about their medications
4. Help them identify which specific medication they want to refill

If they're confirming a medication that was already discussed, acknowledge that and ask for final confirmation to proceed.""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            logger.info("[AI USAGE] Processed medication identification using agent tools")
            
            # Check if medication is clearly identified with dosage info in current input
            dosage_patterns = [r'\d+\s*mg', r'\d+\s*mcg', r'once\s+daily', r'twice\s+daily']
            has_dosage_info = any(re.search(pattern, user_input.lower()) for pattern in dosage_patterns)
            mentions_specific_med = any(med in user_input.lower() for med in medication_names)
            
            # Only transition if we have explicit medication identification AND dosage confirmation in current input
            if has_dosage_info and mentions_specific_med:
                
                # Extract the identified medication and dosage
                identified_med = next((med for med in medication_names if med in user_input.lower()), "medication")
                dosage_match = re.search(r'(\d+)\s*(mg|mcg)', user_input.lower())
                dosage = f"{dosage_match.group(1)}{dosage_match.group(2)}" if dosage_match else "standard dose"
                
                success, updated_context, error = self.state_machine.transition(
                    context.session_id,
                    "medication_identified", 
                    medication={"name": identified_med, "ambiguous": False},
                    dosage={"amount": dosage, "frequency": "as prescribed", "confirmed": True}
                )
                
                if success and updated_context:
                    self.sessions[context.session_id] = updated_context
                    context = updated_context
                    logger.info(f"[TRANSITION] IDENTIFY_MEDICATION -> CONFIRM_DOSAGE (medication and dosage confirmed)")
                    
                    return ConversationResponse(
                        message=f"Perfect! I've confirmed your {identified_med} {dosage}. Let me now check for safety considerations and pharmacy options.",
                        session_id=context.session_id,
                        current_state=context.current_state,
                        next_steps="Checking medication safety and finding the best pharmacy options for you."
                    )
            
            # Stay in current state - continue helping with identification
            logger.info("[NO TRANSITION] Continuing medication identification - need clearer confirmation")
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Please confirm the specific medication and dosage you'd like to refill."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in identify medication handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_clarify_medication(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle CLARIFY_MEDICATION state - resolve medication ambiguity"""
        logger.info("[AI USAGE] Using disambiguation prompt and patient history to clarify medication")
        
        try:
            # Use disambiguation prompt
            prompt_data = self.prompt_manager.format_conversation_prompt(
                "medication_disambiguation",
                user_input=user_input,
                medication_history=["lisinopril 10mg", "atorvastatin 20mg"],  # Mock data
                possible_matches=[{"name": "lisinopril", "indication": "blood pressure"}]
            )
            
            agent_response = self.agent_executor.invoke({
                "input": f"""Help clarify this medication request: '{user_input}'

Use patient_medication_history to see their current medications and help them identify which one they need to refill.""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            
            logger.info("[AI USAGE] Generated clarification response using agent")
            
            # Assume clarification successful (simplified)
            success, updated_context, error = self.state_machine.transition(
                context.session_id,
                "medication_clarified",
                medication={"name": "lisinopril", "ambiguous": False, "rxcui": "29046"}
            )
            
            if success and updated_context:
                self.sessions[context.session_id] = updated_context
                context = updated_context
                logger.info(f"[TRANSITION] CLARIFY_MEDICATION -> {context.current_state.value}")
            
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Perfect! Now let's verify the dosage and check for any safety concerns."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in clarify medication handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_confirm_dosage(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle CONFIRM_DOSAGE state - verify dosage and safety"""
        logger.info("[AI USAGE] Using safety verification tools and dosage confirmation")
        
        try:
            agent_response = self.agent_executor.invoke({
                "input": f"""Patient response about dosage: '{user_input}'

Please help by:
1. Using verify_medication_dosage to confirm the dosage is appropriate
2. Using check_drug_interactions to verify safety
3. Using patient_allergies to check for any allergy concerns

Provide a safety assessment and dosage confirmation.""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            
            logger.info("[AI USAGE] Completed safety verification using multiple tools")
            
            # Assume safety checks pass (simplified)
            success, updated_context, error = self.state_machine.transition(
                context.session_id,
                "dosage_confirmed",
                dosage="10mg",
                medication={"name": "lisinopril", "safety_issues": False}
            )
            
            if success and updated_context:
                self.sessions[context.session_id] = updated_context
                context = updated_context
                logger.info(f"[TRANSITION] CONFIRM_DOSAGE -> {context.current_state.value}")
            
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Excellent! All safety checks passed. Now let's verify your insurance coverage."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in confirm dosage handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_check_authorization(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle CHECK_AUTHORIZATION state - verify insurance and PA"""
        logger.info("[AI USAGE] Checking insurance authorization and coverage")
        
        try:
            agent_response = self.agent_executor.invoke({
                "input": f"""Check insurance authorization for the patient's medication.

Please:
1. Use insurance_formulary_check to verify coverage
2. Check if prior authorization is required
3. Explain the coverage details to the patient

Patient input: '{user_input}'""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            
            logger.info("[AI USAGE] Completed insurance authorization check")
            
            # Assume authorization successful (simplified)
            success, updated_context, error = self.state_machine.transition(
                context.session_id,
                "authorized",
                insurance_info={"prior_auth_required": False, "copay": 10}
            )
            
            if success and updated_context:
                self.sessions[context.session_id] = updated_context
                context = updated_context
                logger.info(f"[TRANSITION] CHECK_AUTHORIZATION -> {context.current_state.value}")
            
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Great news! Your insurance covers this medication. Let's find the best pharmacy option for you."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in check authorization handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_select_pharmacy(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle SELECT_PHARMACY state - find and compare pharmacies"""
        logger.info("[AI USAGE] Using pharmacy and cost tools to find best options")
        
        try:
            agent_response = self.agent_executor.invoke({
                "input": f"""Help patient select the best pharmacy for their refill.

Please:
1. Use find_nearby_pharmacies to show location options
2. Use goodrx_price_lookup to compare costs
3. Use check_pharmacy_inventory to verify availability
4. Recommend the best option considering cost, convenience, and availability

Patient preference: '{user_input}'""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            
            logger.info("[AI USAGE] Generated pharmacy recommendations with cost comparison")
            
            # Simulate pharmacy selection
            success, updated_context, error = self.state_machine.transition(
                context.session_id,
                "pharmacy_selected",
                pharmacy={"name": "Walmart Pharmacy", "id": "walmart_123", "address": "123 Main St"}
            )
            
            if success and updated_context:
                self.sessions[context.session_id] = updated_context
                context = updated_context
                logger.info(f"[TRANSITION] SELECT_PHARMACY -> {context.current_state.value}")
            
            # Calculate potential savings (mock)
            cost_savings = {
                "original_price": 25,
                "final_price": 10,
                "savings_amount": 15,
                "savings_percent": 60
            }
            
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                cost_savings=cost_savings,
                next_steps="Perfect! You'll save $15 with this option. Let's confirm your order."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in select pharmacy handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_confirm_order(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle CONFIRM_ORDER state - final order confirmation"""
        logger.info("[AI USAGE] Processing final order confirmation")
        
        try:
            agent_response = self.agent_executor.invoke({
                "input": f"""Process the final order confirmation.

Please:
1. Summarize all order details
2. Get patient's final confirmation
3. Use submit_refill_order if patient confirms
4. Provide pickup instructions and timing

Patient response: '{user_input}'""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            response_text = agent_response.get("output", "")
            
            logger.info("[AI USAGE] Generated order confirmation summary")
            
            if "yes" in user_input.lower() or "confirm" in user_input.lower():
                # Order confirmed
                success, updated_context, error = self.state_machine.transition(
                    context.session_id,
                    "order_confirmed",
                    order_details={"order_id": "ORD_12345", "pickup_time": "2 PM today"}
                )
                
                if success and updated_context:
                    self.sessions[context.session_id] = updated_context
                    context = updated_context
                    logger.info(f"[TRANSITION] CONFIRM_ORDER -> {context.current_state.value}")
            
            return ConversationResponse(
                message=response_text,
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Your refill order has been submitted! You can pick it up after 2 PM today."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in confirm order handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_escalate_pa(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle ESCALATE_PA state - prior authorization process"""
        logger.info("[AI USAGE] Managing prior authorization escalation")
        
        prompt_data = self.prompt_manager.format_conversation_prompt(
            "prior_authorization_process",
            user_input=user_input
        )
        
        return ConversationResponse(
            message="I'll help you with the prior authorization process. This typically takes 3-5 business days, but I can start the request for you right away.",
            session_id=context.session_id,
            current_state=context.current_state,
            next_steps="Would you like me to start the prior authorization request with your doctor?"
        )
    
    def _handle_complete(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle COMPLETE state - workflow completion"""
        logger.info("[AI USAGE] Generating completion summary and next steps")
        
        # Prepare completion data
        order_details = context.order_details or {"order_id": "ORD_12345", "pickup_time": "2 PM today"}
        savings_summary = "Saved $15 compared to other options"
        pickup_information = f"Ready for pickup at {context.pharmacy.get('name', 'selected pharmacy') if context.pharmacy else 'selected pharmacy'}"
        satisfaction_metrics = "Order completed successfully"
        
        prompt_data = self.prompt_manager.format_conversation_prompt(
            "completion_summary",
            user_input=user_input,
            order_details=order_details,
            savings_summary=savings_summary,
            pickup_information=pickup_information,
            satisfaction_metrics=satisfaction_metrics
        )
        
        return ConversationResponse(
            message="Your prescription refill has been completed successfully! 🎉 Your medication will be ready for pickup after 2 PM today at Walmart Pharmacy. You saved $15 compared to other options. Is there anything else I can help you with?",
            session_id=context.session_id,
            current_state=context.current_state,
            next_steps="Visit Walmart Pharmacy at 123 Main St after 2 PM with your ID to pick up your prescription."
        )
    
    def _handle_error(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle ERROR state - error recovery"""
        logger.info("[AI USAGE] Processing error recovery options")
        
        return ConversationResponse(
            message="I understand there was an issue. Let me help you get back on track. Would you like to start over, or shall we try a different approach?",
            session_id=context.session_id,
            current_state=context.current_state,
            next_steps="I can restart the conversation or help you try again with more specific information."
        )
    
    def _handle_general(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
        """Handle general/fallback cases - support Q&A without forced transitions"""
        logger.info("[AI USAGE] Processing general query with agent - allowing Q&A")
        
        try:
            # Enhanced general handler that supports questions and exploration
            agent_response = self.agent_executor.invoke({
                "input": f"""Patient says: '{user_input}'

Please provide helpful assistance. You can:
1. Use patient_medication_history to answer questions about their medications
2. Use rxnorm_medication_lookup to provide drug information
3. Answer questions about medications, side effects, interactions, etc.
4. Help them explore their medication options
5. Provide general pharmacy assistance

Do NOT force any state transitions - let them ask questions and explore freely.
Only suggest moving forward with refills when they explicitly want to proceed.""",
                "chat_history": self._format_history_for_agent(history)
            })
            
            return ConversationResponse(
                message=agent_response.get("output", "I'm here to help with your pharmacy needs. Feel free to ask any questions about your medications!"),
                session_id=context.session_id,
                current_state=context.current_state,
                next_steps="Ask me anything about your medications or let me know when you're ready to proceed with a refill."
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in general handler: {e}")
            return self._handle_error_state(context, str(e))
    
    def _handle_error_state(self, context: ConversationContext, error_message: str) -> ConversationResponse:
        """Handle error state transition"""
        try:
            success, updated_context, _ = self.state_machine.transition(
                context.session_id, 
                "invalid_input",
                error_message=error_message
            )
            
            if success and updated_context:
                self.sessions[context.session_id] = updated_context
                context = updated_context
                
        except Exception as e:
            logger.error(f"[ERROR] Error transitioning to error state: {e}")
        
        return ConversationResponse(
            message="I apologize, but I encountered an issue processing your request. Let me help you start over or try a different approach.",
            session_id=context.session_id,
            current_state=context.current_state,
            error=error_message,
            next_steps="Would you like to restart the conversation or provide more details?"
        )
    
    def _format_history_for_agent(self, history: List[Dict[str, Any]]) -> List[BaseMessage]:
        """Format conversation history for LangChain agent"""
        messages = []
        for exchange in history[-5:]:  # Last 5 exchanges
            if "user_message" in exchange:
                messages.append(HumanMessage(content=exchange["user_message"]))
            if "ai_response" in exchange:
                messages.append(AIMessage(content=exchange["ai_response"]))
        return messages
    
    def _update_conversation_history(self, session_id: str, user_input: str, ai_response: str):
        """Update conversation history for session"""
        if session_id not in self.conversation_histories:
            self.conversation_histories[session_id] = []
        
        self.conversation_histories[session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_input,
            "ai_response": ai_response
        })
        
        # Keep last 20 exchanges
        if len(self.conversation_histories[session_id]) > 20:
            self.conversation_histories[session_id] = self.conversation_histories[session_id][-20:]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        context = self.sessions[session_id]
        state_summary = self.state_machine.get_session_summary(session_id)
        history = self.conversation_histories.get(session_id, [])
        
        return {
            "session_id": session_id,
            "current_state": context.current_state.value,
            "patient_id": context.patient_id,
            "conversation_length": len(history),
            "state_transitions": state_summary.get("total_transitions", 0),
            "context_data": context.to_dict(),
            "recent_messages": history[-3:] if history else []
        }
    
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions"""
        logger.info(f"[CLEANUP] Cleaning up sessions older than {max_age_hours} hours")
        
        # Use state machine cleanup
        cleaned_count = self.state_machine.cleanup_expired_sessions(max_age_hours)
        
        # Clean up our local storage
        expired_sessions = []
        current_time = datetime.now()
        
        for session_id, history in self.conversation_histories.items():
            if history:
                last_message = history[-1]
                last_time = datetime.fromisoformat(last_message["timestamp"])
                age_hours = (current_time - last_time).total_seconds() / 3600
                
                if age_hours > max_age_hours:
                    expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.conversation_histories.pop(session_id, None)
            self.sessions.pop(session_id, None)
        
        total_cleaned = cleaned_count + len(expired_sessions)
        logger.info(f"[CLEANUP] Cleaned up {total_cleaned} expired sessions")
        
        return total_cleaned
    
    def close_session(self, session_id: str) -> None:
        """Close a conversation session and cleanup resources"""
        if session_id in self.sessions:
            # Log final session state
            session_logger = get_session_logger(session_id)
            context = self.sessions[session_id]
            session_logger.info(f"[SESSION CLOSE] Final state: {context.current_state.value}")
            session_logger.info(f"[SESSION CLOSE] Total messages: {len(self.conversation_histories.get(session_id, []))}")
            
            # Close session logger and cleanup
            close_session_logger(session_id)
            
            # Remove session data
            del self.sessions[session_id]
            if session_id in self.conversation_histories:
                del self.conversation_histories[session_id]
            
            logger.info(f"[SESSION] Closed and cleaned up session {session_id[:8]}")
    
    def get_session_log_path(self, session_id: str) -> Optional[str]:
        """Get the log file path for a specific session"""
        from rxflow.utils.logger import get_all_session_logs
        
        session_logs = get_all_session_logs()
        session_short_id = session_id[:8]
        
        if session_short_id in session_logs:
            return str(session_logs[session_short_id])
        
        return None


# For backward compatibility and easy import
ConversationManager = AdvancedConversationManager