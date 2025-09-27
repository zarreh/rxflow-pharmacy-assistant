"""
Focused refill conversation system for RxFlow Pharmacy Assistant
Provides a streamlined, intelligent conversation flow for prescription refills
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import uuid

from rxflow.workflow.conversation_manager import SmartConversationManager, ConversationContext
from rxflow.utils.logger import get_logger

logger = get_logger(__name__)


class RefillConversationFlow:
    """Intelligent prescription refill conversation flow"""
    
    def __init__(self):
        self.conversation_manager = SmartConversationManager()
        self.active_sessions = {}
    
    async def start_conversation(
        self, 
        patient_id: str, 
        initial_message: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a new refill conversation"""
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Create conversation context
        context = ConversationContext(
            patient_id=patient_id,
            session_id=session_id,
            tools_available=["pharmacy_search", "cost_comparison", "refill_processing"]
        )
        
        # Get intelligent response
        response, updated_context = await self.conversation_manager.get_response(
            initial_message, context
        )
        
        # Store session
        self.active_sessions[session_id] = updated_context
        
        logger.info(f"Started conversation session {session_id} for patient {patient_id}")
        
        return {
            "session_id": session_id,
            "response": response,
            "context": updated_context,
            "intent": updated_context.current_intent,
            "entities": updated_context.extracted_entities
        }
    
    async def continue_conversation(
        self, 
        session_id: str, 
        message: str
    ) -> Dict[str, Any]:
        """Continue an existing conversation"""
        
        context = self.active_sessions.get(session_id)
        if not context:
            # Create new context if session not found
            context = ConversationContext(
                patient_id="unknown",
                session_id=session_id
            )
        
        # Get intelligent response
        response, updated_context = await self.conversation_manager.get_response(
            message, context
        )
        
        # Update session
        self.active_sessions[session_id] = updated_context
        
        return {
            "session_id": session_id,
            "response": response,
            "context": updated_context,
            "intent": updated_context.current_intent,
            "entities": updated_context.extracted_entities,
            "workflow_state": updated_context.workflow_state
        }
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation session summary"""
        context = self.active_sessions.get(session_id)
        if not context:
            return {"error": "Session not found"}
        
        return {
            "session_id": session_id,
            "patient_id": context.patient_id,
            "current_intent": context.current_intent,
            "entities": context.extracted_entities,
            "workflow_state": context.workflow_state,
            "message_count": len(context.conversation_history),
            "last_updated": context.last_updated.isoformat(),
            "status": self._determine_status(context)
        }
    
    def _determine_status(self, context: ConversationContext) -> str:
        """Determine conversation status based on context"""
        
        entities = context.extracted_entities
        workflow = context.workflow_state
        
        # Check if we have basic refill information
        if entities.get("medication") and entities.get("dosage"):
            if workflow.get("pharmacy_selected"):
                if workflow.get("order_confirmed"):
                    return "completed"
                else:
                    return "confirming_order"
            else:
                return "selecting_pharmacy"
        elif entities.get("medication"):
            return "confirming_details"
        else:
            return "gathering_info"
    
    def end_conversation(self, session_id: str):
        """End a conversation session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            self.conversation_manager.clear_conversation(session_id)
            logger.info(f"Ended conversation session {session_id}")
    
    def list_active_sessions(self) -> List[str]:
        """List all active conversation sessions"""
        return list(self.active_sessions.keys())


# Global conversation flow instance
refill_conversation = RefillConversationFlow()


# Convenience functions
async def start_refill_conversation(
    patient_id: str, 
    message: str, 
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Start a new refill conversation"""
    return await refill_conversation.start_conversation(patient_id, message, session_id)


async def continue_refill_conversation(session_id: str, message: str) -> Dict[str, Any]:
    """Continue an existing refill conversation"""
    return await refill_conversation.continue_conversation(session_id, message)


def get_refill_session_summary(session_id: str) -> Dict[str, Any]:
    """Get refill conversation session summary"""
    return refill_conversation.get_session_summary(session_id)


def end_refill_conversation(session_id: str):
    """End a refill conversation session"""
    refill_conversation.end_conversation(session_id)