"""
Enhanced Conversation Manager for RxFlow Pharmacy Assistant v2.0
Interactive Step-by-Step Workflow Implementation
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import SecretStr

from rxflow.config.settings import get_settings
from rxflow.workflow.workflow_types import WorkflowState
from rxflow.utils.logger import get_logger

# Import essential tools
from rxflow.tools.patient_history_tool import patient_history_tool, allergy_tool, adherence_tool
from rxflow.tools.rxnorm_tool import rxnorm_tool, dosage_verification_tool, interaction_tool
from rxflow.tools.pharmacy_tools import pharmacy_location_tool, pharmacy_inventory_tool, pharmacy_wait_times_tool, pharmacy_details_tool, find_cheapest_pharmacy_tool
from rxflow.tools.cost_tools import goodrx_tool, insurance_tool, brand_generic_tool, prior_auth_tool
from rxflow.tools.order_tools import order_submission_tool, order_tracking_tool, order_cancellation_tool
from rxflow.tools.escalation_tools import escalation_check_tool

logger = get_logger(__name__)

@dataclass
class ConversationResponse:
    """Response object for conversation interactions"""
    message: str
    session_id: str
    current_state: WorkflowState
    tool_results: Optional[List[Dict[str, Any]]] = None
    next_steps: Optional[str] = None
    error: Optional[str] = None

class ConversationManager:
    """Enhanced conversation manager with interactive step-by-step workflow"""
    
    def __init__(self):
        logger.info("[INIT] Initializing Enhanced Conversation Manager v2.0")
        self.settings = get_settings()
        self.sessions: Dict[str, Dict[str, Any]] = {}
        
        # Initialize LLM
        api_key = SecretStr(self.settings.openai_api_key) if self.settings.openai_api_key else None
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.1,
            api_key=api_key
        )
        
        # Register tools and setup agent
        self._register_tools()
        self._setup_agent()
        
        logger.info("[INIT] Conversation Manager initialized successfully")

    def _register_tools(self):
        """Register all essential RxFlow tools"""
        logger.info("[TOOLS] Registering tools for LangChain agent")
        
        self.tools = [
            # Patient Tools
            patient_history_tool, allergy_tool, adherence_tool,
            # Medication Tools
            rxnorm_tool, dosage_verification_tool, interaction_tool,
            # Pharmacy Tools
            pharmacy_location_tool, pharmacy_inventory_tool, pharmacy_wait_times_tool,
            pharmacy_details_tool, find_cheapest_pharmacy_tool,
            # Cost Tools
            goodrx_tool, insurance_tool, brand_generic_tool, prior_auth_tool,
            # Order Tools
            order_submission_tool, order_tracking_tool, order_cancellation_tool,
            # Escalation Tool
            escalation_check_tool
        ]
        
        logger.info(f"[TOOLS] Registered {len(self.tools)} tools successfully")

    def _setup_agent(self):
        """Setup LangChain agent with interactive step-by-step workflow"""
        logger.info("[AGENT] Setting up LangChain agent")
        
        system_prompt = """You are RxFlow, an intelligent AI pharmacy assistant helping patients with prescription refills.

🎯 CRITICAL: INTERACTIVE STEP-BY-STEP CONVERSATION REQUIRED

INTERACTIVE WORKFLOW RULES:
🔄 ONE STEP AT A TIME - Never do all steps in one response
🔄 WAIT FOR CONFIRMATION - Ask "Is this correct?" or "Would you like to proceed?" 
🔄 USER CHOICE REQUIRED - Let user choose between options before continuing
🔄 PROGRESSIVE DISCLOSURE - Only show next step after previous step is confirmed

STEP-BY-STEP PROCESS:
Step 1: Find the medication using patient_history_tool, then IMMEDIATELY check escalation_check_tool
Step 2: If escalation needed, inform user and stop; Otherwise ask for confirmation 
Step 3: After confirmation, verify dosage using dosage_verification_tool, then ask to proceed
Step 4: After dosage OK, show cost options using brand_generic_tool, then ask preference
Step 5: After cost choice, show pharmacy options using find_cheapest_pharmacy_tool, then ask to choose

CONVERSATION EXAMPLES:
❌ WRONG (All at once): "I found omeprazole, verified dosage, found savings, here are 3 pharmacies..."
✅ CORRECT (Step by step): "I found your omeprazole 20mg for acid reflux. Is this the medication you want to refill?"

🚨 MANDATORY ESCALATION CHECKS:
AFTER finding ANY medication with patient_history_tool, you MUST immediately use escalation_check_tool(medication_name) to check for:
- Controlled substances (lorazepam, hydrocodone, etc.)
- Expired prescriptions 
- No refills remaining
- Doctor consultation requirements

ESCALATION EXAMPLES:
✅ CORRECT: "I found lorazepam 0.5mg. *Uses escalation_check_tool* I need to escalate this to your doctor because it's a controlled substance."
✅ CORRECT: "I found lisinopril 10mg. *Uses escalation_check_tool* Your prescription has expired. You'll need to contact your doctor for a new prescription."

CRITICAL RULES:
- Only perform ONE workflow step per response
- Always end with a question asking for user confirmation or choice
- Wait for user input before proceeding to next step
- Use tools for current step only, not future steps
- Keep responses focused on current step only
- ALWAYS use escalation_check_tool after finding medication and BEFORE asking for confirmation

TOOL USAGE GUIDELINES:
- Always check patient medication history FIRST using patient_history_tool
- IMMEDIATELY after finding medication, use escalation_check_tool(medication_name)
- For "acid reflux" → use patient_history_tool("acid reflux")
- For "blood pressure" → use patient_history_tool("blood pressure")
- NEVER ask for patient ID - use tools to find information

SAFETY PROTOCOLS:
- Check for drug interactions and allergies before confirming medications
- Use escalation_check_tool for EVERY medication before proceeding
- Escalate controlled substances, expired prescriptions, and no-refill situations
- Verify all medication details before processing

Remember: Be interactive, ask for confirmation at each step, wait for responses before proceeding."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create agent
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            early_stopping_method="generate"
        )
        
        logger.info("[AGENT] LangChain agent configured successfully")

    def create_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new conversation session"""
        logger.info(f"[SESSION] Creating new session: {session_id}")
        
        session_data = {
            "session_id": session_id,
            "state": WorkflowState.GREETING,
            "messages": [],
            "context": {},
            "created_at": datetime.now().isoformat(),
            "escalated": False,
            "escalation_reason": None
        }
        
        self.sessions[session_id] = session_data
        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        return self.sessions.get(session_id)

    async def process_message(self, session_id: str, message: str) -> ConversationResponse:
        """Process user message with interactive step-by-step workflow"""
        logger.info(f"[PROCESS] Processing message for session {session_id}")
        
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)

        try:
            # Prepare conversation history
            chat_history = []
            for msg in session.get("messages", []):
                if msg.get("role") == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))

            # Execute agent with current message
            logger.info(f"[AGENT] Executing agent with {len(chat_history)} history messages")
            
            result = await self.agent_executor.ainvoke({
                "input": message,
                "chat_history": chat_history
            })

            # Extract response
            response_text = result["output"]

            # Update session with new messages
            session["messages"].extend([
                {"role": "user", "content": message, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": response_text, "timestamp": datetime.now().isoformat()}
            ])

            # Check if escalation occurred
            escalated = "escalat" in response_text.lower()
            if escalated:
                session["escalated"] = True
                session["state"] = WorkflowState.ESCALATED
                logger.info(f"[ESCALATION] Session {session_id} escalated to pharmacist")

            # Create response
            return ConversationResponse(
                message=response_text,
                session_id=session_id,
                current_state=session["state"],
                tool_results=[],
                next_steps="Await pharmacist consultation" if escalated else None
            )

        except Exception as e:
            logger.error(f"[ERROR] Failed to process message: {str(e)}")
            return ConversationResponse(
                message="I apologize, but I'm experiencing technical difficulties. Please try again or speak with a pharmacist directly.",
                session_id=session_id,
                current_state=WorkflowState.ERROR,
                error=str(e)
            )

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Get complete conversation history for a session"""
        session = self.get_session(session_id)
        if session:
            return session.get("messages", [])
        return []

    def clear_session(self, session_id: str) -> bool:
        """Clear session data"""
        if session_id in self.sessions:
            logger.info(f"[SESSION] Clearing session: {session_id}")
            del self.sessions[session_id]
            return True
        return False