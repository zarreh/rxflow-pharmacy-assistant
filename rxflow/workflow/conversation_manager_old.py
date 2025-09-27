"""
Advanced Conversation Manager for RxFlow Pharmacy Assistant - Step 6
Integrates LangChain agent with tools, state machine, and prompt management
"""

from typing import Any, Dict, List, Optional, Tuple, Union
import json
import uuid
import asyncio
from datetime import datetime
from dataclasses import dataclass, field

from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import Tool

from rxflow.llm import get_conversational_llm
from rxflow.utils.logger import get_logger
from rxflow.workflow.state_machine import RefillStateMachine
from rxflow.workflow.workflow_types import RefillState, ConversationContext, ToolResult
from rxflow.prompts.prompt_manager import PromptManager
from rxflow.tools import (
    patient_history_tool, rxnorm_tool, pharmacy_inventory_tool, 
    pharmacy_location_tool, goodrx_tool, insurance_tool, ToolManager
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


class ConversationMemory:
    """Enhanced conversation memory with entity tracking"""
    
    def __init__(self, window_size: int = 10):
        self.memory = ConversationBufferWindowMemory(
            k=window_size,
            return_messages=True,
            memory_key="chat_history"
        )
        self.entities = {}
        self.intents = []
    
    def add_message(self, message: BaseMessage):
        """Add message to memory and extract entities"""
        self.memory.chat_memory.add_message(message)
        
        # Extract and store entities from message
        if isinstance(message, HumanMessage) and isinstance(message.content, str):
            self._extract_entities(message.content)
    
    def _extract_entities(self, text: str):
        """Extract medication, pharmacy, and other entities from text"""
        # Simple entity extraction - can be enhanced with NER later
        text_lower = text.lower()
        
        # Common medications
        medications = [
            "lisinopril", "metformin", "eliquis", "lipitor", "atorvastatin",
            "omeprazole", "meloxicam", "methocarbamol", "famotidine"
        ]
        
        for med in medications:
            if med in text_lower:
                self.entities["medication"] = med.title()
                break
        
        # Dosage patterns
        import re
        dosage_match = re.search(r'(\d+)\s*mg', text_lower)
        if dosage_match:
            self.entities["dosage"] = f"{dosage_match.group(1)}mg"
        
        # Pharmacy names
        pharmacies = ["cvs", "walmart", "walgreens", "h-e-b", "heb"]
        for pharmacy in pharmacies:
            if pharmacy in text_lower:
                self.entities["pharmacy"] = pharmacy.upper()
                break
    
    def get_relevant_context(self) -> Dict[str, Any]:
        """Get relevant context for current conversation"""
        return {
            "entities": self.entities,
            "recent_intents": self.intents[-3:],  # Last 3 intents
            "message_count": len(self.memory.chat_memory.messages)
        }


class IntentClassifier:
    """Classifies user intents for better conversation routing"""
    
    INTENT_PROMPTS = {
        "refill_request": "User wants to refill a prescription",
        "pharmacy_inquiry": "User asking about pharmacy locations or services",
        "cost_inquiry": "User asking about medication costs or insurance",
        "side_effects": "User asking about medication side effects",
        "drug_interactions": "User asking about drug interactions",
        "dosage_question": "User asking about medication dosage",
        "general_question": "General question about medications or health",
        "escalation_needed": "Issue requires human pharmacist intervention"
    }
    
    def __init__(self):
        self.llm = get_analytical_llm()
    
    async def classify_intent(self, message: str, context: ConversationContext) -> Tuple[str, float]:
        """Classify user intent with confidence score"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classification system for a pharmacy assistant.
            
Analyze the user message and classify it into one of these intents:
- refill_request: User wants to refill a prescription
- pharmacy_inquiry: Asking about pharmacy locations or services  
- cost_inquiry: Asking about medication costs or insurance
- side_effects: Asking about medication side effects
- drug_interactions: Asking about drug interactions
- dosage_question: Asking about medication dosage
- general_question: General question about medications or health
- escalation_needed: Complex issue requiring pharmacist

Consider the conversation context and respond with JSON:
{
    "intent": "intent_name",
    "confidence": 0.95,
    "reasoning": "brief explanation"
}"""),
            ("human", f"Message: {message}\nContext: {context.extracted_entities}")
        ])
        
        try:
            response = await self.llm.ainvoke(prompt.format_messages())
            # Try to parse JSON response
            content = response.content.strip()
            
            # Handle cases where response might not be pure JSON
            if not content.startswith('{'):
                # Look for JSON in the response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")
            
            result = json.loads(content)
            return result.get("intent", "general_question"), result.get("confidence", 0.5)
            
        except Exception as e:
            logger.warning(f"Intent classification failed: {e}")
            # Simple rule-based fallback
            message_lower = message.lower()
            if any(word in message_lower for word in ["refill", "prescription", "medication"]):
                return "refill_request", 0.8
            elif any(word in message_lower for word in ["pharmacy", "location", "where"]):
                return "pharmacy_inquiry", 0.8
            elif any(word in message_lower for word in ["cost", "price", "insurance", "copay"]):
                return "cost_inquiry", 0.8
            else:
                return "general_question", 0.5


class ConversationManager:
    """Intelligent conversation manager with context awareness and tool integration"""
    
    def __init__(self):
        self.llm = get_conversational_llm()
        self.intent_classifier = IntentClassifier()
        self.conversations = {}  # Session ID -> ConversationMemory
        self.prompt_manager = PromptManager()
        self.state_machines = {}  # session_id -> RefillStateMachine
        
        self.system_prompt = """You are RxFlow, an intelligent AI pharmacy assistant. You help patients with prescription refills, medication questions, and pharmacy services.

CORE PRINCIPLES:
- Be conversational, helpful, and professional
- Always prioritize patient safety
- Ask clarifying questions when needed
- Remember context from earlier in the conversation
- Guide users through the refill process naturally
- Escalate complex medical questions to human pharmacists

CONVERSATION STYLE:
- Use natural language, not templates
- Be empathetic and understanding
- Keep responses concise but complete
- Use emojis sparingly for clarity

CAPABILITIES:
- Process prescription refill requests
- Find nearby pharmacies and compare prices
- Explain medication information (basic)
- Handle insurance and cost questions
- Schedule pharmacy consultations
- Escalate complex medical questions

WORKFLOW AWARENESS:
You can guide users through these workflows:
1. Medication confirmation and details
2. Pharmacy selection and comparison
3. Cost optimization and insurance
4. Order processing and confirmation
5. Escalation to human pharmacist when needed

Remember: You're having a real conversation, not following a script."""

    async def get_response(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Tuple[str, ConversationContext]:
        """Get intelligent response with context awareness"""
        
        # Get or create conversation memory
        memory = self.conversations.get(context.session_id)
        if not memory:
            memory = ConversationMemory()
            self.conversations[context.session_id] = memory
        
        # Add user message to memory
        user_msg = HumanMessage(content=message)
        memory.add_message(user_msg)
        
        # Classify intent
        intent, confidence = await self.intent_classifier.classify_intent(message, context)
        context.current_intent = intent
        
        # Get relevant context
        relevant_context = memory.get_relevant_context()
        
        # Build conversation prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("system", f"""CURRENT CONTEXT:
Patient ID: {context.patient_id}
Current Intent: {intent} (confidence: {confidence:.2f})
Extracted Entities: {relevant_context['entities']}
Workflow State: {context.workflow_state}
Available Tools: {context.tools_available}

CONVERSATION GUIDELINES FOR THIS INTENT:
{self._get_intent_guidelines(intent)}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
        
        # Get chat history
        chat_history = memory.memory.chat_memory.messages[-10:]  # Last 10 messages
        
        try:
            # Generate response
            formatted_messages = prompt.format_messages(
                chat_history=chat_history,
                input=message
            )
            
            logger.debug(f"Sending {len(formatted_messages)} messages to LLM")
            
            response = await self.llm.ainvoke(formatted_messages)
            
            response_text = response.content
            logger.debug(f"LLM response length: {len(response_text) if response_text else 0}")
            
            # Add AI response to memory
            ai_msg = AIMessage(content=response_text)
            memory.add_message(ai_msg)
            
            # Update context with new entities
            context.extracted_entities.update(relevant_context['entities'])
            context.last_updated = datetime.now()
            
            # Add to conversation history
            context.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_message": message,
                "ai_response": response_text,
                "intent": intent,
                "confidence": confidence
            })
            
            logger.info(f"Generated response for intent '{intent}' with confidence {confidence:.2f}")
            
            return response_text, context
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            fallback_response = "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question?"
            return fallback_response, context
    
    def _get_intent_guidelines(self, intent: str) -> str:
        """Get specific guidelines for handling different intents"""
        
        guidelines = {
            "refill_request": """
- Confirm medication name, strength, and quantity
- Ask about preferred pharmacy if not specified
- Check for any changes in dosage or instructions
- Guide through pharmacy selection and cost comparison
- Complete the refill workflow step by step""",
            
            "pharmacy_inquiry": """
- Help find nearby pharmacy locations
- Compare wait times, prices, and services
- Explain pharmacy-specific benefits
- Consider user preferences (distance, cost, etc.)""",
            
            "cost_inquiry": """
- Explain insurance coverage and copays
- Compare brand vs generic pricing
- Suggest cost-saving options
- Explain patient assistance programs if applicable""",
            
            "side_effects": """
- Provide basic, factual information about common side effects
- Always recommend consulting with pharmacist or doctor for concerns
- Do not provide medical advice
- Escalate if serious side effects reported""",
            
            "drug_interactions": """
- Express concern for patient safety
- Recommend immediate pharmacist consultation
- Do not attempt to provide interaction advice
- Escalate to human pharmacist immediately""",
            
            "dosage_question": """
- Refer to prescription label for current dosage
- Do not provide dosage advice or changes
- Recommend consulting prescriber or pharmacist
- Escalate if dosage concerns expressed""",
            
            "escalation_needed": """
- Acknowledge the complexity of the question
- Explain why pharmacist consultation is recommended
- Offer to schedule consultation or transfer to pharmacist
- Provide timeframe for human response""",
            
            "general_question": """
- Provide helpful, factual information
- Stay within scope of pharmacy assistant
- Offer to help with refills or pharmacy services
- Suggest appropriate resources for medical questions"""
        }
        
        return guidelines.get(intent, "Provide helpful, accurate information while staying within your role as a pharmacy assistant.")
    
    def clear_conversation(self, session_id: str):
        """Clear conversation memory for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation memory for session {session_id}")
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation state"""
        memory = self.conversations.get(session_id)
        if not memory:
            return {"status": "no_conversation"}
        
        return {
            "message_count": len(memory.memory.chat_memory.messages),
            "entities": memory.entities,
            "recent_intents": memory.intents[-5:],
            "status": "active"
        }
    
    async def handle_message(self, user_input: str, session_id: str) -> str:
        """Main entry point with explicit AI usage tracking"""
        
        # Get or create state machine for session
        if session_id not in self.state_machines:
            self.state_machines[session_id] = RefillStateMachine()
        
        state_machine = self.state_machines[session_id]
        
        # Log where AI is being used
        logger.info(f"[AI USAGE] Processing input in state: {state_machine.current_state.value}")
        
        # Route to appropriate handler based on current state
        handler_name = state_machine.get_state_handler()
        handler = getattr(self, handler_name, self.handle_default)
        
        response = await handler(user_input, session_id, state_machine)
        
        return response
    
    async def handle_identify_medication(self, user_input: str, session_id: str, state_machine: RefillStateMachine) -> str:
        """Handle medication identification with AI"""
        
        # [AI USAGE] Extract medication using LLM
        system_prompt, user_prompt = self.prompt_manager.format_prompt(
            "medication_extraction", 
            user_input=user_input
        )
        
        extraction_result = await self.llm_manager.get_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_format="json"
        )
        
        logger.info(f"[AI USAGE] Medication extraction result: {extraction_result}")
        
        # Verify medication with service
        medication = extraction_result.get("medication_name")
        if medication:
            med_info = self.medication_service.verify_medication(medication)
            if med_info:
                state_machine.context["medication"] = med_info
                state_machine.transition("medication_found")
                return f"I found {medication}. What dosage are you currently taking?"
            else:
                # [AI USAGE] Disambiguation needed
                similar_meds = self.medication_service.find_similar(medication)
                if similar_meds:
                    state_machine.transition("medication_ambiguous")
                    state_machine.context["similar_medications"] = similar_meds
                    return await self._generate_disambiguation_response(medication, similar_meds)
        
        return "I couldn't find that medication. Could you please check the spelling or provide more details?"
    
    async def _generate_disambiguation_response(self, user_input: str, similar_meds: List[str]) -> str:
        """[AI USAGE] Generate clarifying question for ambiguous medication"""
        system_prompt, user_prompt = self.prompt_manager.format_prompt(
            "medication_disambiguation",
            user_input=user_input,
            matches=", ".join(similar_meds)
        )
        
        response = await self.llm_manager.get_completion(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        logger.info("[AI USAGE] Generated disambiguation question")
        return response
    
    async def handle_default(self, user_input: str, session_id: str, state_machine: RefillStateMachine) -> str:
        """Default handler for unrecognized states"""
        return "I'm sorry, I didn't understand that. Can you please rephrase?"