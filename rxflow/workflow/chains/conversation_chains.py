"""
Conversation chains for RxFlow Pharmacy Assistant
Handles multi-turn conversations and user interactions
"""

from typing import Any, Dict

from langchain.prompts import ChatPromptTemplate

from rxflow.llm import get_conversational_llm
from rxflow.utils.logger import get_logger
from rxflow.workflow.conversation_manager import SmartConversationManager, ConversationContext

logger = get_logger(__name__)


class ConversationChain:
    """Base class for conversation chains with smart conversation management"""

    def __init__(self):
        """Initialize the conversation chain with smart conversation manager"""
        self.llm = get_conversational_llm()
        self.conversation_manager = SmartConversationManager()

    async def invoke(self, context: Dict[str, Any]) -> str:
        """Invoke the conversation chain with intelligent context handling"""
        # Convert context to ConversationContext if needed
        if isinstance(context, dict):
            conv_context = ConversationContext(
                patient_id=context.get("patient_id", "unknown"),
                session_id=context.get("session_id", "default"),
                extracted_entities=context.copy(),
                workflow_state=context.get("workflow_state", {})
            )
        else:
            conv_context = context
            
        # Use smart conversation manager for response
        user_message = context.get("user_input", "")
        response, updated_context = await self.conversation_manager.get_response(
            user_message, conv_context
        )
        
        return response


class MedicationConfirmationChain(ConversationChain):
    """Chain for confirming medication details with the user"""

    def __init__(self):
        super().__init__()
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self._get_system_prompt()),
                ("human", "{user_input}"),
                (
                    "assistant",
                    "I understand you need a refill. Let me confirm the details.",
                ),
                ("human", "Context: {context}"),
            ]
        )

    def _get_system_prompt(self) -> str:
        return """You are RxFlow, a professional pharmacy assistant AI. Your role is to help patients refill their prescriptions safely and efficiently.

IMPORTANT GUIDELINES:
1. Always confirm medication details before proceeding
2. Use clear, friendly, and professional language
3. Ask only ONE question at a time
4. Be specific about medication name, strength, and quantity
5. Never assume details - always confirm with the patient

Your current task is to confirm medication details that were extracted from the user's request."""

    async def invoke(self, context: Dict[str, Any]) -> str:
        """Generate confirmation message for medication details"""

        medication_name = context.get("medication_name", "").title()
        medication_strength = context.get("medication_strength", "")
        quantity = context.get("quantity", 30)

        # Build confirmation message
        if medication_name and medication_strength:
            confirmation = f"I'd be happy to help you refill your {medication_name} {medication_strength}."
        elif medication_name:
            confirmation = f"I'd be happy to help you refill your {medication_name}."
        else:
            confirmation = "I'd be happy to help you with your prescription refill."

        # Ask for confirmation with specific details
        if medication_name and medication_strength:
            question = f"To confirm, is this for {medication_name} {medication_strength}, 30-day supply?"
        elif medication_name:
            question = f"To confirm the details, what strength of {medication_name} do you need? (e.g., 10mg, 20mg)"
        else:
            question = "Could you please tell me which medication you'd like to refill?"

        return f"{confirmation}\n\n{question}"


class PharmacySelectionChain(ConversationChain):
    """Chain for helping users select a pharmacy"""

    def __init__(self):
        super().__init__()

    async def invoke(self, context: Dict[str, Any]) -> str:
        """Generate pharmacy selection message with options"""

        available_pharmacies = context.get("available_pharmacies", [])
        medication_name = context.get("medication_name", "your medication")

        if not available_pharmacies:
            return "I'm sorry, but I couldn't find any pharmacies with your medication in stock nearby. Would you like me to check a wider area?"

        message = f"Great! I found {len(available_pharmacies)} pharmacies with {medication_name} in stock:\n\n"

        for i, pharmacy in enumerate(available_pharmacies[:3], 1):  # Limit to top 3
            name = pharmacy.get("name", "Unknown Pharmacy")
            distance = pharmacy.get("distance_miles", 0)
            wait_time = pharmacy.get("wait_time_hours", 0)
            price = pharmacy.get("price", 0)

            wait_text = (
                f"{int(wait_time * 60)} minutes"
                if wait_time < 1
                else f"{wait_time:.1f} hours"
            )

            message += f"{i}. **{name}**\n"
            message += f"   📍 {distance:.1f} miles away\n"
            message += f"   ⏱️ Ready in {wait_text}\n"
            message += f"   💰 ${price:.2f}\n\n"

        message += "Which pharmacy would you prefer? You can say the number (1, 2, 3) or the pharmacy name."

        return message


class CostOptimizationChain(ConversationChain):
    """Chain for presenting cost optimization options"""

    def __init__(self):
        super().__init__()

    async def invoke(self, context: Dict[str, Any]) -> str:
        """Generate cost optimization message with savings options"""

        medication_name = context.get("medication_name", "your medication")
        brand_price = context.get("brand_price", 0)
        generic_price = context.get("generic_price", 0)
        generic_name = context.get("generic_name", "")
        insurance_copay = context.get("insurance_copay", 0)

        if generic_price and brand_price and generic_price < brand_price:
            savings = brand_price - generic_price

            message = f"💰 **Cost Savings Opportunity!**\n\n"

            if generic_name and generic_name.lower() != medication_name.lower():
                message += f"I found that {medication_name} (brand name) costs ${brand_price:.2f}, "
                message += f"but the generic version ({generic_name}) costs only ${generic_price:.2f}.\n\n"
            else:
                message += f"I found pricing options for {medication_name}:\n"
                message += f"• Brand name: ${brand_price:.2f}\n"
                message += f"• Generic: ${generic_price:.2f}\n\n"

            message += f"**You could save ${savings:.2f}** by choosing the generic version.\n\n"

            if insurance_copay and insurance_copay < generic_price:
                message += f"With your insurance, your copay would be ${insurance_copay:.2f}.\n\n"

            message += (
                "Would you like to proceed with the generic version to save money?"
            )

            return message

        return f"I've found {medication_name} at the selected pharmacy. Shall I proceed with submitting your refill request?"


class EscalationChain(ConversationChain):
    """Chain for handling escalation scenarios"""

    def __init__(self):
        super().__init__()

    async def invoke(self, context: Dict[str, Any]) -> str:
        """Generate escalation message based on the issue type"""

        escalation_type = context.get("escalation_type", "")
        medication_name = context.get("medication_name", "your medication")
        prescriber_name = context.get("prescriber_name", "your doctor")

        if escalation_type == "no_refills":
            return self._handle_no_refills(medication_name, prescriber_name)
        elif escalation_type == "prior_auth":
            return self._handle_prior_authorization(medication_name, prescriber_name)
        elif escalation_type == "high_interaction":
            return self._handle_drug_interaction(medication_name)
        elif escalation_type == "not_covered":
            return self._handle_not_covered(medication_name)
        else:
            return f"I need to escalate your {medication_name} request for review. I'll get back to you within 24 hours."

    def _handle_no_refills(self, medication: str, prescriber: str) -> str:
        return f"""⚠️ **No Refills Remaining**

I see that you have no refills remaining for {medication}. To continue your medication, I need to request a new prescription from {prescriber}.

I can send an electronic request that includes:
• Your current medication and dosage
• Your recent refill history
• A request for continued therapy

Would you like me to send this request to {prescriber}? They typically respond within 24-48 hours."""

    def _handle_prior_authorization(self, medication: str, prescriber: str) -> str:
        return f"""📋 **Prior Authorization Required**

{medication} requires prior authorization from your insurance. I can help streamline this process by sending the necessary documentation to {prescriber}.

The request will include:
• Clinical criteria for {medication}
• Your medical history supporting the need
• Insurance-specific requirements

This process typically takes 2-3 business days. Shall I initiate the prior authorization request?"""

    def _handle_drug_interaction(self, medication: str) -> str:
        return f"""⚠️ **Drug Interaction Alert**

I've detected a potential interaction between {medication} and your current medications that requires pharmacist review for your safety.

A licensed pharmacist will:
• Review your complete medication profile
• Assess the interaction risk
• Provide safety recommendations

This review typically takes 30-60 minutes. Would you like me to schedule this safety consultation?"""

    def _handle_not_covered(self, medication: str) -> str:
        return f"""❌ **Insurance Coverage Issue**

{medication} is not covered under your current insurance plan. However, I can help find alternatives:

• Generic equivalents that are covered
• Alternative medications in the same class
• Patient assistance programs
• GoodRx or other discount options

Would you like me to search for covered alternatives that work similarly to {medication}?"""


class OrderConfirmationChain(ConversationChain):
    """Chain for final order confirmation"""

    def __init__(self):
        super().__init__()

    async def invoke(self, context: Dict[str, Any]) -> str:
        """Generate final confirmation message"""

        medication_name = context.get("medication_name", "your medication")
        pharmacy_name = context.get("pharmacy_name", "the selected pharmacy")
        pickup_time = context.get("pickup_time", "within 2 hours")
        confirmation_number = context.get(
            "confirmation_number", "RX" + str(hash(str(context)) % 100000)
        )
        total_savings = context.get("estimated_savings", 0)

        message = f"""✅ **Refill Request Confirmed!**

**Medication:** {medication_name}
**Pharmacy:** {pharmacy_name}
**Ready for pickup:** {pickup_time}
**Confirmation #:** {confirmation_number}

"""

        if total_savings and total_savings > 0:
            message += f"💰 **You saved ${total_savings:.2f}** with this refill!\n\n"

        message += """📱 **What's Next:**
• You'll receive an SMS when your prescription is ready
• Bring a valid ID for pickup
• Your insurance card (if applicable)

Is there anything else I can help you with today?"""

        return message
