"""
Simplified intelligent conversation system for RxFlow Pharmacy Assistant
Provides reliable, context-aware conversations without complex intent classification
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage

from rxflow.llm import get_conversational_llm
from rxflow.utils.logger import get_logger

logger = get_logger(__name__)


class SimpleConversationManager:
    """Simplified conversation manager for reliable pharmacy assistant interactions"""
    
    def __init__(self):
        self.llm = get_conversational_llm()
        self.conversations = {}  # Session ID -> Memory
        
        # Enhanced system prompt for pharmacy assistance
        self.system_prompt = """You are RxFlow, an intelligent AI pharmacy assistant. Your role is to help patients with prescription refills and pharmacy-related questions in a natural, conversational way.

CORE CAPABILITIES:
• Process prescription refill requests
• Help find nearby pharmacies and compare prices
• Explain basic medication information
• Handle insurance and cost questions
• Guide users through the refill workflow
• Escalate complex medical questions to pharmacists

CONVERSATION GUIDELINES:
• Be conversational, helpful, and professional
• Ask clarifying questions when information is missing
• Remember what the user has already told you
• Guide users step-by-step through processes
• Use natural language, not rigid templates
• Always prioritize patient safety

WORKFLOW AWARENESS:
When helping with refills, guide users through:
1. Medication identification and confirmation
2. Pharmacy selection (location, price, wait time)
3. Insurance and cost optimization
4. Final confirmation and next steps

RESPONSE STYLE:
• Keep responses helpful but concise
• Use emojis sparingly for clarity
• Ask only one main question at a time
• Acknowledge what the user has already provided
• Be empathetic and understanding

SAFETY REMINDERS:
• Never provide medical advice
• Refer complex medication questions to pharmacists
• Always confirm medication details carefully
• Escalate safety concerns immediately

Remember: You're having a real conversation with a real person who needs help with their medication. Be helpful, natural, and genuinely useful."""

    async def get_response(self, session_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get intelligent response for user message"""
        
        try:
            # Get or create conversation memory
            if session_id not in self.conversations:
                self.conversations[session_id] = ConversationBufferWindowMemory(
                    k=10, return_messages=True, memory_key="chat_history"
                )
            
            memory = self.conversations[session_id]
            
            # Add user message to memory
            memory.chat_memory.add_user_message(message)
            
            # Build conversation context
            conversation_context = ""
            if context:
                patient_id = context.get("patient_id", "unknown")
                conversation_context = f"\nPatient ID: {patient_id}"
                
                # Add any extracted entities
                if context.get("extracted_entities"):
                    entities = context["extracted_entities"]
                    if entities:
                        conversation_context += f"\nKnown Information: {entities}"
            
            # Create prompt with conversation history
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt + conversation_context),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}")
            ])
            
            # Get chat history
            chat_variables = memory.load_memory_variables({})
            chat_history = chat_variables.get("chat_history", [])
            
            # Generate response
            response = await self.llm.ainvoke(
                prompt.format_messages(
                    chat_history=chat_history,
                    input=message
                )
            )
            
            response_text = response.content
            
            # Add AI response to memory
            memory.chat_memory.add_ai_message(response_text)
            
            # Extract simple entities from the conversation
            entities = self._extract_simple_entities(message, response_text)
            
            # Determine conversation status
            status = self._determine_status(chat_history, entities)
            
            logger.info(f"Generated response for session {session_id}")
            
            return {
                "response": response_text,
                "entities": entities,
                "status": status,
                "message_count": len(chat_history) + 2  # +2 for current exchange
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Could you please try rephrasing your question?",
                "entities": {},
                "status": "error",
                "message_count": 0
            }
    
    def _extract_simple_entities(self, user_message: str, ai_response: str) -> Dict[str, str]:
        """Extract simple entities from conversation"""
        entities = {}
        
        # Combine both messages for entity extraction
        combined_text = f"{user_message} {ai_response}".lower()
        
        # Common medications
        medications = {
            "lisinopril": ["lisinopril", "prinivil", "zestril"],
            "metformin": ["metformin", "glucophage"],
            "eliquis": ["eliquis", "apixaban"],
            "lipitor": ["lipitor", "atorvastatin"],
            "omeprazole": ["omeprazole", "prilosec"],
            "meloxicam": ["meloxicam", "mobic"],
            "methocarbamol": ["methocarbamol", "robaxin"],
            "famotidine": ["famotidine", "pepcid"]
        }
        
        for med_name, variations in medications.items():
            if any(var in combined_text for var in variations):
                entities["medication"] = med_name.title()
                break
        
        # Dosage patterns
        import re
        dosage_match = re.search(r'(\d+)\s*mg', combined_text)
        if dosage_match:
            entities["dosage"] = f"{dosage_match.group(1)}mg"
        
        # Pharmacy names
        pharmacies = {
            "CVS": ["cvs"],
            "Walmart": ["walmart"],
            "Walgreens": ["walgreens"],
            "H-E-B": ["heb", "h-e-b", "h e b"]
        }
        
        for pharmacy_name, variations in pharmacies.items():
            if any(var in combined_text for var in variations):
                entities["pharmacy"] = pharmacy_name
                break
        
        return entities
    
    def _determine_status(self, chat_history: List, entities: Dict[str, str]) -> str:
        """Determine conversation status based on history and entities"""
        
        if not chat_history:
            return "new_conversation"
        
        # Look at recent messages for status indicators
        recent_messages = chat_history[-4:] if len(chat_history) >= 4 else chat_history
        recent_text = " ".join([msg.content.lower() for msg in recent_messages if hasattr(msg, 'content')])
        
        # Check for completion indicators
        if any(phrase in recent_text for phrase in ["confirmed", "confirmation number", "ready for pickup"]):
            return "completed"
        
        # Check for escalation indicators
        if any(phrase in recent_text for phrase in ["pharmacist", "doctor", "prescriber", "no refills"]):
            return "escalation"
        
        # Check progress based on entities and conversation
        if entities.get("medication") and entities.get("dosage"):
            if "pharmacy" in recent_text or entities.get("pharmacy"):
                if any(phrase in recent_text for phrase in ["cost", "price", "insurance", "generic"]):
                    return "cost_review"
                else:
                    return "pharmacy_selection"
            else:
                return "medication_confirmed"
        elif entities.get("medication"):
            return "gathering_details"
        else:
            return "initial_inquiry"
    
    def clear_conversation(self, session_id: str):
        """Clear conversation memory for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Cleared conversation for session {session_id}")
    
    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        memory = self.conversations.get(session_id)
        if not memory:
            return {"status": "no_conversation", "message_count": 0}
        
        chat_variables = memory.load_memory_variables({})
        chat_history = chat_variables.get("chat_history", [])
        
        return {
            "session_id": session_id,
            "message_count": len(chat_history),
            "status": "active",
            "last_messages": [
                msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                for msg in chat_history[-2:] if hasattr(msg, 'content')
            ]
        }


# Global instance
simple_conversation_manager = SimpleConversationManager()


# Convenience functions
async def get_simple_response(session_id: str, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get response from simple conversation manager"""
    return await simple_conversation_manager.get_response(session_id, message, context)


def clear_simple_conversation(session_id: str):
    """Clear simple conversation"""
    simple_conversation_manager.clear_conversation(session_id)


def get_simple_conversation_summary(session_id: str) -> Dict[str, Any]:
    """Get simple conversation summary"""
    return simple_conversation_manager.get_conversation_summary(session_id)