"""
Enhanced Conversation Manager for RxFlow Pharmacy Assistant v2.0

This module provides a comprehensive conversation management system for pharmacy refill 
workflows. It orchestrates LangChain agents, manages conversation state, and provides 
interactive step-by-step guidance for prescription refill processes.

The conversation manager integrates 19 specialized pharmacy tools including patient 
history lookup, medication verification, pharmacy location services, cost optimization, 
and order processing capabilities.

Key Features:
    - Interactive step-by-step workflow guidance
    - Automatic escalation detection for controlled substances
    - Multi-tool coordination for comprehensive pharmacy operations
    - Session-based conversation state management
    - LangChain agent integration with OpenAI GPT-4

Example:
    ```python
    # Initialize conversation manager
    manager = ConversationManager()
    
    # Process a refill request
    response = await manager.process_message(
        message="I need to refill my omeprazole",
        session_id="user_123"
    )
    
    print(response.message)  # Step-by-step guidance response
    ```

Classes:
    ConversationResponse: Structured response object for conversation interactions
    ConversationManager: Main orchestration class for pharmacy workflows

Dependencies:
    - LangChain for agent orchestration and tool coordination
    - OpenAI GPT-4 for natural language understanding and generation
    - 19 specialized pharmacy tools for comprehensive operations
    - Session management for conversation state persistence

Note:
    This manager enforces interactive workflows to ensure patient safety and 
    regulatory compliance in pharmaceutical operations.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, cast

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from rxflow.config.settings import get_settings
from rxflow.tools.cost_tools import (
    brand_generic_tool,
    goodrx_tool,
    insurance_tool,
    prior_auth_tool,
)
from rxflow.tools.escalation_tools import escalation_check_tool
from rxflow.tools.order_tools import (
    order_cancellation_tool,
    order_submission_tool,
    order_tracking_tool,
)

# Import essential tools
from rxflow.tools.patient_history_tool import (
    adherence_tool,
    allergy_tool,
    patient_history_tool,
)
from rxflow.tools.pharmacy_tools import (
    find_cheapest_pharmacy_tool,
    pharmacy_details_tool,
    pharmacy_inventory_tool,
    pharmacy_location_tool,
    pharmacy_wait_times_tool,
)
from rxflow.tools.rxnorm_tool import (
    dosage_verification_tool,
    interaction_tool,
    rxnorm_tool,
)
from rxflow.utils.logger import get_logger
from rxflow.workflow.workflow_types import WorkflowState

logger = get_logger(__name__)


@dataclass
class ConversationResponse:
    """
    Structured response object for conversation interactions in pharmacy workflows.

    This dataclass encapsulates all information returned from a conversation turn,
    including the agent's response message, session management data, workflow state,
    and any tool execution results or errors that occurred during processing.

    Attributes:
        message (str): The formatted response message from the AI agent to display
            to the user. Contains step-by-step guidance and instructions.
        session_id (str): Unique identifier for the conversation session to maintain
            state persistence across multiple message exchanges.
        current_state (WorkflowState): The current workflow state after processing
            the message, used for state machine transitions.
        tool_results (Optional[List[Dict[str, Any]]]): Results from any pharmacy tools
            executed during message processing, including patient data, medication info,
            pharmacy details, or cost calculations.
        next_steps (Optional[str]): Suggested next actions or prompts to guide the
            user through the workflow process.
        error (Optional[str]): Error message if any issues occurred during processing,
            including tool failures, validation errors, or safety escalations.

    Example:
        ```python
        response = ConversationResponse(
            message="I found your omeprazole 20mg. Is this correct?",
            session_id="user_123",
            current_state=WorkflowState.MEDICATION_VERIFIED,
            tool_results=[{"medication": "omeprazole", "strength": "20mg"}],
            next_steps="Confirm medication before proceeding to cost options"
        )
        ```
    """

    message: str
    session_id: str
    current_state: WorkflowState
    tool_results: Optional[List[Dict[str, Any]]] = None
    next_steps: Optional[str] = None
    error: Optional[str] = None


class ConversationManager:
    """
    Enhanced conversation manager with interactive step-by-step pharmacy workflows.

    This class serves as the main orchestration layer for the RxFlow pharmacy assistant,
    coordinating between LangChain agents, specialized pharmacy tools, and conversation
    state management. It implements a safety-first approach with mandatory escalation
    checks and interactive user confirmations at each step.

    The manager integrates 19 specialized tools across 5 categories:
    - Patient Tools: History, allergies, adherence tracking
    - Medication Tools: RxNorm lookup, dosage verification, interaction checks
    - Pharmacy Tools: Location services, inventory, wait times, cost comparison
    - Cost Tools: Insurance formulary, GoodRx pricing, generic alternatives
    - Order Tools: Submission, tracking, cancellation capabilities

    Key Features:
        - Interactive step-by-step workflow enforcement
        - Automatic escalation detection for controlled substances
        - Session-based conversation state persistence
        - Comprehensive tool result aggregation and formatting
        - Safety-first design with mandatory confirmation steps

    Workflow States:
        The manager transitions through defined workflow states ensuring proper
        progression from medication identification → verification → cost analysis
        → pharmacy selection → order processing.

    Safety Measures:
        - Mandatory escalation_check_tool execution after medication identification
        - Interactive confirmations prevent automated dangerous operations
        - Tool failure handling with graceful degradation
        - Comprehensive logging for audit trails

    Example:
        ```python
        # Initialize the conversation manager
        manager = ConversationManager()

        # Process a refill request with interactive guidance
        response = await manager.process_message(
            message="I need to refill my blood pressure medication",
            session_id="patient_456"
        )

        # Manager will guide through step-by-step process:
        # 1. Find medication in patient history
        # 2. Check for escalation requirements
        # 3. Verify dosage and interactions
        # 4. Present cost options for user choice
        # 5. Show pharmacy options for selection
        # 6. Facilitate order submission
        ```

    Thread Safety:
        This class maintains session state in memory and is not thread-safe.
        Use separate instances for concurrent conversations or implement
        external session storage for multi-threaded environments.
    """

    def __init__(self) -> None:
        logger.info("[INIT] Initializing Enhanced Conversation Manager v2.0")
        self.settings = get_settings()
        self.sessions: Dict[str, Dict[str, Any]] = {}

        # Initialize LLM using centralized LLM manager
        from rxflow.llm import get_tool_llm
        self.llm = get_tool_llm()

        # Register tools and setup agent
        self._register_tools()
        self._setup_agent()

        logger.info("[INIT] Conversation Manager initialized successfully")

    def _register_tools(self) -> None:
        """
        Register all essential RxFlow pharmacy tools for LangChain agent integration.

        This method initializes and registers 19 specialized pharmacy tools across
        5 functional categories, making them available for the LangChain agent to
        use during conversation processing. Each tool is designed with safety wrappers
        and comprehensive error handling.

        Tool Categories Registered:
            Patient Tools (3):
                - patient_history_tool: Retrieve patient medication history
                - allergy_tool: Check patient allergies and contraindications
                - adherence_tool: Analyze medication adherence patterns

            Medication Tools (3):
                - rxnorm_tool: RxNorm medication lookup and standardization
                - dosage_verification_tool: Validate dosing and strength
                - interaction_tool: Check drug-drug interactions

            Pharmacy Tools (5):
                - pharmacy_location_tool: Find nearby pharmacies by location
                - pharmacy_inventory_tool: Check medication availability
                - pharmacy_wait_times_tool: Get current wait time estimates
                - pharmacy_details_tool: Retrieve pharmacy contact and hours
                - find_cheapest_pharmacy_tool: Compare costs across pharmacies

            Cost Tools (4):
                - goodrx_tool: Get GoodRx discount pricing information
                - insurance_tool: Check insurance formulary coverage
                - brand_generic_tool: Compare brand vs generic options
                - prior_auth_tool: Check prior authorization requirements

            Order Tools (3):
                - order_submission_tool: Submit prescription refill orders
                - order_tracking_tool: Track order status and delivery
                - order_cancellation_tool: Cancel or modify existing orders

            Safety Tools (1):
                - escalation_check_tool: Detect controlled substances and safety issues

        Returns:
            None: Tools are stored in self.tools list for agent access

        Raises:
            ImportError: If any required tool modules cannot be imported
            AttributeError: If tool objects are not properly configured

        Note:
            This method is called automatically during __init__ and should not be
            called directly. All tools include safety wrappers that prevent
            dangerous operations and provide graceful error handling.
        """
        logger.info("[TOOLS] Registering tools for LangChain agent")

        self.tools = [
            # Patient Tools
            patient_history_tool,
            allergy_tool,
            adherence_tool,
            # Medication Tools
            rxnorm_tool,
            dosage_verification_tool,
            interaction_tool,
            # Pharmacy Tools
            pharmacy_location_tool,
            pharmacy_inventory_tool,
            pharmacy_wait_times_tool,
            pharmacy_details_tool,
            find_cheapest_pharmacy_tool,
            # Cost Tools
            goodrx_tool,
            insurance_tool,
            brand_generic_tool,
            prior_auth_tool,
            # Order Tools
            order_submission_tool,
            order_tracking_tool,
            order_cancellation_tool,
            # Escalation Tool
            escalation_check_tool,
        ]

        logger.info(f"[TOOLS] Registered {len(self.tools)} tools successfully")

    def _setup_agent(self) -> None:
        """
        Setup LangChain agent with interactive step-by-step workflow capabilities.

        This method configures the core LangChain agent with a comprehensive system
        prompt that enforces interactive, safety-first pharmacy workflows. The agent
        is designed to guide users through prescription refills one step at a time,
        requiring confirmations and preventing automated dangerous operations.

        Agent Configuration:
            - Model: OpenAI GPT-4o-mini with temperature 0.1 for consistent responses
            - Tools: All 19 registered pharmacy tools with safety wrappers
            - Prompt: Comprehensive system prompt with workflow rules and examples
            - Memory: Conversation history with MessagesPlaceholder for context

        Interactive Workflow Rules Enforced:
            1. ONE STEP AT A TIME: Never complete entire workflow in single response
            2. WAIT FOR CONFIRMATION: Ask "Is this correct?" before proceeding
            3. USER CHOICE REQUIRED: Present options and wait for selection
            4. PROGRESSIVE DISCLOSURE: Only reveal next step after confirmation
            5. MANDATORY ESCALATION: Always check controlled substances

        Safety Measures Implemented:
            - Automatic escalation detection after medication identification
            - Interactive confirmations prevent dangerous automated operations
            - Tool failure handling with graceful degradation
            - Comprehensive error reporting and user guidance

        Workflow Steps Enforced:
            1. Find medication using patient_history_tool + escalation_check_tool
            2. Verify dosage using dosage_verification_tool (after confirmation)
            3. Show cost options using brand_generic_tool (after user choice)
            4. Present pharmacy options using find_cheapest_pharmacy_tool
            5. Facilitate order submission only after all confirmations

        Returns:
            None: Agent executor is stored in self.agent for message processing

        Raises:
            ValueError: If OpenAI API key is invalid or missing
            LangChainError: If agent creation fails due to configuration issues

        Example System Prompt Behavior:
            User: "I need to refill my omeprazole"
            Agent: "I found your omeprazole 20mg for acid reflux. Is this correct?"
            [Waits for confirmation before proceeding to next step]

        Note:
            The agent is configured with strict interaction rules to ensure patient
            safety and regulatory compliance. It will not complete workflows without
            explicit user confirmations at each critical step.
        """
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

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        # Create agent
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=15,
            early_stopping_method="generate",
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
            "escalation_reason": None,
        }

        self.sessions[session_id] = session_data
        return session_data

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve existing session data for conversation state management.

        Args:
            session_id (str): Unique identifier for the conversation session

        Returns:
            Optional[Dict[str, Any]]: Session data dictionary containing conversation
                history, workflow state, and metadata, or None if session doesn't exist

        Example:
            ```python
            session = manager.get_session("user_123")
            if session:
                messages = session.get("messages", [])
                state = session.get("state")
            ```
        """
        return self.sessions.get(session_id)

    async def process_message(
        self, session_id: str, message: str
    ) -> ConversationResponse:
        """
        Process user message with interactive step-by-step pharmacy workflow guidance.

        This is the core method that orchestrates the entire conversation flow,
        coordinating between the LangChain agent, pharmacy tools, and safety systems.
        It maintains conversation history, enforces interactive workflows, and handles
        escalations to ensure patient safety and regulatory compliance.

        Args:
            session_id (str): Unique identifier for the conversation session
                Used to maintain state persistence across multiple interactions
                Format: UUID string (e.g., "550e8400-e29b-41d4-a716-446655440000")
            message (str): User's input message requesting pharmacy assistance
                Examples: "I need to refill my omeprazole", "Yes, that's correct"
                Supports natural language queries and confirmation responses

        Returns:
            ConversationResponse: Structured response dataclass containing:
                - message (str): Agent's step-by-step guidance response text
                - session_id (str): Session identifier for conversation continuity
                - current_state (WorkflowState): Updated workflow state after processing
                - tool_results (Optional[List[Dict[str, Any]]]): Results from executed tools
                - next_steps (Optional[str]): Guidance for user's next action
                - error (Optional[str]): Error details if processing failed

        Raises:
            Exception: All exceptions are caught and returned as ConversationResponse
                with error field populated and user-friendly message

        Raises:
            Exception: Catches all exceptions and returns error response with
                user-friendly message and technical details in error field

        Safety Features:
            - Automatic escalation detection for controlled substances
            - Interactive confirmation requirements at each step
            - Tool failure handling with graceful degradation
            - Comprehensive audit logging for regulatory compliance

        Example:
            ```python
            # Process a prescription refill request
            response = await manager.process_message(
                session_id="patient_456",
                message="I need to refill my omeprazole 20mg"
            )

            print(response.message)
            # "I found your omeprazole 20mg for acid reflux. Is this correct?"

            # Continue conversation with confirmation
            response2 = await manager.process_message(
                session_id="patient_456",
                message="Yes, that's correct"
            )

            print(response2.message)
            # "Great! Let me verify the dosage for safety..."
            ```

        Note:
            This method enforces interactive workflows and will not complete
            entire prescription processes in a single call. Each step requires
            user confirmation before proceeding to maintain safety standards.
        """
        logger.info(f"[PROCESS] Processing message for session {session_id}")

        # Get or create session
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)

        try:
            # Prepare conversation history
            chat_history: List[Union[HumanMessage, AIMessage]] = []
            for msg in session.get("messages", []):
                if msg.get("role") == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))

            # Execute agent with current message
            logger.info(
                f"[AGENT] Executing agent with {len(chat_history)} history messages"
            )

            result = await self.agent_executor.ainvoke(
                {"input": message, "chat_history": chat_history}
            )

            # Extract response
            response_text = result["output"]

            # Update session with new messages
            session["messages"].extend(
                [
                    {
                        "role": "user",
                        "content": message,
                        "timestamp": datetime.now().isoformat(),
                    },
                    {
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": datetime.now().isoformat(),
                    },
                ]
            )

            # Check if escalation occurred
            escalated = "escalat" in response_text.lower()
            if escalated:
                session["escalated"] = True
                session["state"] = WorkflowState.ESCALATED
                logger.info(
                    f"[ESCALATION] Session {session_id} escalated to pharmacist"
                )

            # Create response
            return ConversationResponse(
                message=response_text,
                session_id=session_id,
                current_state=session["state"],
                tool_results=[],
                next_steps="Await pharmacist consultation" if escalated else None,
            )

        except Exception as e:
            logger.error(f"[ERROR] Failed to process message: {str(e)}")
            return ConversationResponse(
                message="I apologize, but I'm experiencing technical difficulties. Please try again or speak with a pharmacist directly.",
                session_id=session_id,
                current_state=WorkflowState.ERROR,
                error=str(e),
            )

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get complete conversation history for audit and context reconstruction.

        Retrieves the full message history for a conversation session, including
        timestamps, user inputs, agent responses, and metadata. Useful for
        debugging, audit trails, and context restoration.

        Args:
            session_id (str): Unique identifier for the conversation session

        Returns:
            List[Dict[str, Any]]: List of message dictionaries with structure:
                - role: "user" or "assistant"
                - content: The message text content
                - timestamp: ISO format timestamp of the message
                - metadata: Additional context (tool results, escalations, etc.)

        Example:
            ```python
            history = manager.get_conversation_history("user_123")
            for msg in history:
                print(f"{msg['role']}: {msg['content']} [{msg['timestamp']}]")
            ```
        """
        session = self.get_session(session_id)
        if session:
            return cast(List[Dict[str, Any]], session.get("messages", []))
        return cast(List[Dict[str, Any]], [])

    def clear_session(self, session_id: str) -> bool:
        """
        Clear session data for privacy and memory management.

        Removes all conversation history, workflow state, and metadata for the
        specified session. This is important for user privacy and memory management
        in long-running applications.

        Args:
            session_id (str): Unique identifier for the session to clear

        Returns:
            bool: True if session was successfully cleared, False if session
                didn't exist or clearing failed

        Example:
            ```python
            # Clear session after conversation completion
            success = manager.clear_session("user_123")
            if success:
                print("Session cleared successfully")
            ```

        Note:
            This operation is irreversible. Consider exporting conversation
            history for audit purposes before clearing if required by
            regulatory compliance.
        """
        if session_id in self.sessions:
            logger.info(f"[SESSION] Clearing session: {session_id}")
            del self.sessions[session_id]
            return True
        return False
