"""Advanced prompt management system for pharmacy refill assistant"""
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from ..workflow.workflow_types import RefillState

@dataclass
class PromptTemplate:
    """Comprehensive prompt template with versioning and context awareness"""
    name: str
    system_prompt: str
    user_template: str
    examples: List[Dict[str, Any]] = field(default_factory=list)
    version: str = "1.0"
    context: Optional[str] = None
    state: Optional[RefillState] = None
    tools_required: List[str] = field(default_factory=list)
    safety_checks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging and debugging"""
        return {
            "name": self.name,
            "version": self.version,
            "context": self.context,
            "state": self.state.value if self.state else None,
            "tools_required": self.tools_required,
            "safety_checks": self.safety_checks,
            "created_at": self.created_at.isoformat()
        }

class PromptManager:
    """Advanced prompt management with state awareness and tool integration"""
    
    def __init__(self):
        self._initialize_prompts()
        self.usage_stats = {}
        self.prompt_history = []
    
    def _initialize_prompts(self):
        """Initialize comprehensive prompt library for all workflow states"""
        self.prompts = {
            # MEDICATION EXTRACTION AND IDENTIFICATION
            "medication_extraction": PromptTemplate(
                name="medication_extraction",
                system_prompt="""You are a pharmacy assistant helping with medication refills.
                
TASK: Extract medication information from user input and determine next steps.

EXTRACTION PRIORITIES:
1. Medication name (generic or brand)
2. Dosage/strength 
3. Quantity or supply duration
4. Patient preferences (pharmacy, cost concerns)

SAFETY REQUIREMENTS:
- If medication name is unclear, ask for clarification
- If dosage seems unusual, verify with patient
- Always check for potential ambiguity

RESPONSE FORMAT:
Provide natural conversational response while internally noting:
- What information was extracted
- What information is missing
- Whether clarification is needed""",
                user_template="""Patient message: "{user_input}"

Please help extract the medication details and respond conversationally.""",
                examples=[
                    {
                        "input": "I need to refill my blood pressure medication",
                        "user_input": "I need to refill my blood pressure medication",
                        "response": "I'd be happy to help you refill your blood pressure medication. Let me check your current medications to identify which one you need.",
                        "extracted": {"medication_type": "blood pressure", "specificity": "low"}
                    },
                    {
                        "input": "Refill lisinopril 10mg 30-day supply", 
                        "user_input": "Refill lisinopril 10mg 30-day supply",
                        "response": "I'll help you refill Lisinopril 10mg for a 30-day supply. Let me verify your prescription details and check the best options for you.",
                        "extracted": {"medication": "lisinopril", "dosage": "10mg", "quantity": "30-day supply"}
                    }
                ],
                state=RefillState.IDENTIFY_MEDICATION,
                tools_required=["patient_medication_history", "rxnorm_medication_lookup"],
                safety_checks=["verify_medication_name", "check_dosage_appropriateness"]
            ),
            
            "medication_disambiguation": PromptTemplate(
                name="medication_disambiguation",
                system_prompt="""You are disambiguating medication names for safe prescription processing.

TASK: Help identify the correct medication when user input is ambiguous.

DISAMBIGUATION STRATEGY:
1. Present clear options from patient history if available
2. Ask about medical condition the medication treats
3. Ask about dosage/appearance if helpful
4. Never guess - always verify with patient

SAFETY CRITICAL:
- Wrong medication identification could be dangerous
- Be thorough but not overwhelming
- Use simple, clear language""",
                user_template="""Patient said: "{user_input}"
Patient medication history: {medication_history}
Possible matches: {possible_matches}

Help clarify which medication they need.""",
                examples=[
                    {
                        "input": "my heart medication",
                        "user_input": "my heart medication",
                        "medication_history": ["lisinopril 10mg", "atorvastatin 20mg"],
                        "possible_matches": [{"name": "lisinopril", "indication": "blood pressure"}, {"name": "atorvastatin", "indication": "cholesterol"}],
                        "response": "I see you take two medications that could be for heart health. Are you looking to refill Lisinopril (for blood pressure) or Atorvastatin (for cholesterol)?"
                    }
                ],
                state=RefillState.CLARIFY_MEDICATION,
                tools_required=["patient_medication_history"],
                safety_checks=["confirm_medication_identity", "verify_indication"]
            ),

            "dosage_confirmation": PromptTemplate(
                name="dosage_confirmation", 
                system_prompt="""You are confirming medication dosage for prescription accuracy.

TASK: Verify the exact dosage and quantity for the medication refill.

VERIFICATION PROCESS:
1. Confirm dosage matches patient's current prescription
2. Verify quantity/supply duration is appropriate
3. Check if this is a routine refill or dosage change

SAFETY REQUIREMENTS:
- Any dosage discrepancy must be clarified
- Unusual quantities should be verified
- Document any changes from previous fills""",
                user_template="""Medication: {medication_name}
Patient's current dosage: {current_dosage}
Requested dosage: {requested_dosage}
Available dosages: {available_dosages}

Confirm the correct dosage and quantity.""",
                examples=[
                    {
                        "current": "10mg",
                        "requested": "10mg", 
                        "response": "Perfect! I can confirm Lisinopril 10mg, which matches your current prescription. How many days' supply do you need?"
                    }
                ],
                state=RefillState.CONFIRM_DOSAGE,
                tools_required=["verify_medication_dosage", "patient_medication_history"],
                safety_checks=["dosage_appropriateness", "quantity_limits"]
            ),

            "safety_verification": PromptTemplate(
                name="safety_verification",
                system_prompt="""You are performing critical safety checks before medication dispensing.

SAFETY PROTOCOL:
1. Check drug interactions with current medications
2. Verify no allergies to medication or components  
3. Review contraindications
4. Assess interaction severity and management

RESPONSE REQUIREMENTS:
- If MAJOR/CONTRAINDICATED interactions: Stop process, recommend physician consultation
- If MODERATE interactions: Explain risk, suggest monitoring
- If MINOR/NO interactions: Proceed with reassurance
- Always explain findings in patient-friendly language""",
                user_template="""Medication: {medication_name} {dosage}
Patient allergies: {allergies}
Current medications: {current_medications}
Drug interactions found: {interactions}
Allergy conflicts: {allergy_conflicts}

Assess safety and provide guidance.""",
                examples=[
                    {
                        "medication": "lisinopril",
                        "interactions": [{"drug": "ibuprofen", "severity": "moderate"}],
                        "response": "I found a moderate interaction between Lisinopril and ibuprofen that could affect your blood pressure control. I recommend discussing this with your doctor and considering acetaminophen for pain relief instead."
                    }
                ],
                state=RefillState.CONFIRM_DOSAGE,
                tools_required=["check_drug_interactions", "patient_allergies"],
                safety_checks=["interaction_severity", "allergy_verification", "contraindication_check"]
            ),

            "insurance_authorization": PromptTemplate(
                name="insurance_authorization",
                system_prompt="""You are checking insurance coverage and prior authorization requirements.

AUTHORIZATION PROCESS:
1. Verify medication is covered by patient's insurance
2. Explain coverage tier and copay
3. Identify prior authorization requirements
4. Provide PA process guidance if needed

COMMUNICATION STRATEGY:
- Explain insurance terms clearly (tier, copay, PA)
- Be transparent about costs and timelines
- Offer alternatives if coverage issues exist
- Provide actionable next steps""",
                user_template="""Medication: {medication_name}
Insurance plan: {insurance_plan}
Coverage details: {coverage_details}
Prior authorization required: {pa_required}
PA criteria: {pa_criteria}

Explain coverage and next steps.""",
                examples=[
                    {
                        "medication": "eliquis",
                        "pa_required": True,
                        "response": "Eliquis requires prior authorization from your insurance. The good news is that with your atrial fibrillation diagnosis, you meet the criteria. I can help start the process, which typically takes 3-5 business days."
                    }
                ],
                state=RefillState.CHECK_AUTHORIZATION,
                tools_required=["insurance_formulary_check", "prior_authorization_lookup"],
                safety_checks=["coverage_verification", "pa_criteria_review"]
            ),

            "pharmacy_selection": PromptTemplate(
                name="pharmacy_selection",
                system_prompt="""You are helping patients choose the optimal pharmacy for their refill.

SELECTION CRITERIA:
1. Medication availability/stock status
2. Cost comparison (insurance copay, cash price, discounts)
3. Convenience (distance, wait time, hours)
4. Services (drive-through, delivery, special programs)

RECOMMENDATION STRATEGY:
- Present 2-3 best options with clear tradeoffs
- Highlight significant cost savings opportunities
- Consider patient preferences (speed vs. cost vs. convenience)
- Explain any special programs or discounts available""",
                user_template="""Available pharmacies: {pharmacy_options}
Medication: {medication_name} {dosage}
Cost information: {cost_comparison}
Patient location preference: {location_preference}
Priority: {priority} (cost/convenience/speed)

Recommend the best pharmacy options.""",
                examples=[
                    {
                        "options": ["CVS (0.5mi, $15)", "Walmart (3mi, $4)"],
                        "response": "I found two great options: CVS is closest at 0.5 miles with your $15 copay, or Walmart is 3 miles away but only $4 with their generic program. The drive to Walmart could save you $11 - which would you prefer?"
                    }
                ],
                state=RefillState.SELECT_PHARMACY,
                tools_required=["find_nearby_pharmacies", "check_pharmacy_inventory", "goodrx_price_lookup"],
                safety_checks=["stock_verification", "price_accuracy"]
            ),

            "cost_optimization": PromptTemplate(
                name="cost_optimization",
                system_prompt="""You are optimizing medication costs for patients while maintaining safety.

OPTIMIZATION STRATEGIES:
1. Compare insurance copay vs. cash price with discounts
2. Evaluate generic vs. brand name options  
3. Consider pharmacy-specific programs ($4 generics, etc.)
4. Check manufacturer coupons for expensive medications

COST COMMUNICATION:
- Show clear savings calculations
- Explain why costs differ between pharmacies
- Present generic options with safety assurance
- Highlight total potential savings""",
                user_template="""Medication: {medication_name} {dosage}
Insurance coverage: {insurance_info}
Generic alternative: {generic_option}
Pharmacy prices: {price_comparison}
Discount programs: {available_discounts}

Find the most cost-effective option.""",
                examples=[
                    {
                        "medication": "atorvastatin",
                        "brand_price": 180,
                        "generic_price": 4,
                        "response": "Great news! The generic atorvastatin works exactly the same as brand Lipitor but costs only $4 instead of $180. That's a $176 savings per month. Would you like me to process the generic version?"
                    }
                ],
                state=RefillState.SELECT_PHARMACY,
                tools_required=["compare_brand_generic_prices", "goodrx_price_lookup", "insurance_formulary_check"],
                safety_checks=["generic_equivalence", "price_verification"]
            ),

            "order_confirmation": PromptTemplate(
                name="order_confirmation",
                system_prompt="""You are confirming prescription refill orders before final submission.

CONFIRMATION REQUIREMENTS:
1. Verify all medication details (name, dosage, quantity)
2. Confirm pharmacy selection and pickup details
3. Review total cost and payment method
4. Provide clear pickup timeline and requirements

CONFIRMATION PROCESS:
- Present complete order summary
- Ask for explicit confirmation 
- Provide pickup instructions and contact info
- Set clear expectations for next steps""",
                user_template="""Order Summary:
Medication: {medication_name} {dosage} ({quantity})
Pharmacy: {pharmacy_name} at {pharmacy_address}
Cost: {cost_breakdown}
Pickup time: {pickup_time}
Special instructions: {special_instructions}

Please confirm this order is correct.""",
                examples=[
                    {
                        "summary": "Lisinopril 10mg, 30-day supply at Walmart Plaza for $4",
                        "response": "Here's your refill summary:\n• Lisinopril 10mg, 30-day supply\n• Walmart Pharmacy, 456 Plaza Dr\n• $4 total cost\n• Ready for pickup after 2 PM today\n• Please bring valid ID\n\nDoes this look correct?"
                    }
                ],
                state=RefillState.CONFIRM_ORDER,
                tools_required=["submit_refill_order"],
                safety_checks=["order_accuracy", "pickup_verification"]
            ),

            "prior_authorization_process": PromptTemplate(
                name="prior_authorization_process",
                system_prompt="""You are guiding patients through the prior authorization process.

PA COMMUNICATION:
1. Explain what prior authorization means in simple terms
2. Outline the specific steps and timeline
3. Describe required documentation and who provides it
4. Set realistic expectations for approval

PROCESS MANAGEMENT:
- Break down complex PA requirements into clear steps
- Identify what patient needs to do vs. what happens automatically
- Provide timeline estimates and follow-up instructions
- Offer alternatives while PA is processed""",
                user_template="""Medication: {medication_name}
PA requirements: {pa_criteria}
Required documentation: {required_docs}
Processing time: {processing_time}
Patient's diagnosis: {patient_diagnosis}
Approval likelihood: {approval_likelihood}

Guide patient through PA process.""",
                examples=[
                    {
                        "medication": "eliquis",
                        "criteria": "documented AFib",
                        "response": "Prior authorization for Eliquis requires documentation of your atrial fibrillation diagnosis. I'll send the request to Dr. Johnson with your recent EKG results. This typically takes 3-5 business days, and approval is likely given your medical history."
                    }
                ],
                state=RefillState.ESCALATE_PA,
                tools_required=["prior_authorization_lookup"],
                safety_checks=["criteria_verification", "documentation_completeness"]
            ),

            "error_handling": PromptTemplate(
                name="error_handling",
                system_prompt="""You are handling errors and exceptions in the refill process gracefully.

ERROR RESPONSE STRATEGY:
1. Acknowledge the issue without technical jargon
2. Explain what happened in patient-friendly terms
3. Provide clear alternative solutions or next steps
4. Maintain helpful and professional tone

RECOVERY OPTIONS:
- Suggest alternative approaches
- Offer to escalate to human pharmacist if needed
- Provide contact information for follow-up
- Ensure patient feels supported despite the issue""",
                user_template="""Error encountered: {error_type}
Context: {error_context}
User impact: {impact_description}
Available alternatives: {alternatives}
Escalation options: {escalation_options}

Provide helpful error response.""",
                examples=[
                    {
                        "error": "medication_not_found",
                        "response": "I couldn't find that medication in our database. Could you double-check the spelling or tell me what condition it's for? I can also look up your current medications to help identify it."
                    }
                ],
                state=RefillState.ERROR,
                tools_required=[],
                safety_checks=["error_classification", "alternative_verification"]
            ),

            "completion_summary": PromptTemplate(
                name="completion_summary",
                system_prompt="""You are providing completion summaries for successful refill orders.

COMPLETION COMMUNICATION:
1. Celebrate successful completion
2. Summarize what was accomplished
3. Provide clear next steps and pickup details
4. Highlight any savings achieved
5. Offer additional assistance

SUMMARY ELEMENTS:
- Order confirmation details
- Cost savings achieved  
- Pickup timeline and requirements
- Contact information for questions
- Invitation for future assistance""",
                user_template="""Completed order: {order_details}
Savings achieved: {savings_summary}
Pickup details: {pickup_information}
Patient satisfaction indicators: {satisfaction_metrics}

Provide completion summary and next steps.""",
                examples=[
                    {
                        "order": "Lisinopril refill at Walmart",
                        "savings": "$11 saved vs CVS",
                        "response": "Perfect! Your Lisinopril refill is confirmed at Walmart Pharmacy. You saved $11 by choosing Walmart over CVS. Your prescription will be ready for pickup after 2 PM today. Just bring your ID and you're all set!"
                    }
                ],
                state=RefillState.COMPLETE,
                tools_required=[],
                safety_checks=["completion_verification"]
            )
        }
    
    def get_prompt(self, prompt_name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name"""
        return self.prompts.get(prompt_name)
    
    def get_prompt_for_state(self, state: RefillState) -> List[PromptTemplate]:
        """Get all prompts applicable to a given state"""
        return [prompt for prompt in self.prompts.values() 
                if prompt.state == state or prompt.state is None]
    
    def render_prompt(self, prompt_name: str, **kwargs) -> str:
        """Render prompt template with provided kwargs"""
        prompt = self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        return prompt.user_template.format(**kwargs)
    
    def render_system_message(self, prompt_name: str, **kwargs) -> str:
        """Render system prompt with context"""
        prompt = self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        system_msg = prompt.system_prompt
        if kwargs:
            # Add dynamic context to system message if kwargs provided
            context_str = "\n\nCURRENT CONTEXT:\n" + "\n".join(
                f"- {k}: {v}" for k, v in kwargs.items() if k != 'user_input'
            )
            system_msg += context_str
        
        return system_msg
    
    def get_examples(self, prompt_name: str) -> List[Dict[str, Any]]:
        """Get few-shot examples for a prompt"""
        prompt = self.get_prompt(prompt_name)
        return prompt.examples if prompt else []
    
    def log_prompt_usage(self, prompt_name: str, context: Dict[str, Any]):
        """Log prompt usage for analytics and debugging"""
        if prompt_name not in self.usage_stats:
            self.usage_stats[prompt_name] = 0
        self.usage_stats[prompt_name] += 1
        
        self.prompt_history.append({
            "prompt_name": prompt_name,
            "timestamp": datetime.now(),
            "context": context,
            "usage_count": self.usage_stats[prompt_name]
        })
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get prompt usage statistics"""
        return self.usage_stats.copy()
    
    def validate_prompt_template(self, prompt: PromptTemplate) -> List[str]:
        """Validate prompt template for common issues"""
        issues = []
        
        # Check for required components
        if not prompt.system_prompt.strip():
            issues.append("Empty system prompt")
        
        if not prompt.user_template.strip():
            issues.append("Empty user template")
        
        # Check for template variables consistency
        import re
        template_vars = set(re.findall(r'{(\w+)}', prompt.user_template))
        if prompt.examples:
            for i, example in enumerate(prompt.examples):
                if 'input' in example:
                    example_vars = set(re.findall(r'{(\w+)}', str(example)))
                    if not template_vars.issubset(example_vars):
                        issues.append(f"Example {i} missing template variables")
        
        return issues
    
    def format_conversation_prompt(
        self, 
        prompt_name: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Format complete conversation prompt with history and examples"""
        prompt = self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        # Build conversation context
        messages = []
        
        # Add system message
        system_msg = self.render_system_message(prompt_name, **kwargs)
        messages.append({"role": "system", "content": system_msg})
        
        # Add few-shot examples if available
        for example in prompt.examples[:2]:  # Limit to 2 examples for context
            if 'input' in example and 'response' in example:
                messages.append({"role": "user", "content": example['input']})
                messages.append({"role": "assistant", "content": example['response']})
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-5:]:  # Keep last 5 exchanges
                messages.append(msg)
        
        # Add current user input
        if 'user_input' in kwargs:
            user_msg = self.render_prompt(prompt_name, **kwargs)
            messages.append({"role": "user", "content": user_msg})
        
        # Log usage
        self.log_prompt_usage(prompt_name, kwargs)
        
        return {
            "messages": messages,
            "prompt_template": prompt.to_dict(),
            "tools_required": prompt.tools_required,
            "safety_checks": prompt.safety_checks
        }
    
    # Legacy method for backward compatibility
    def format_prompt(self, prompt_name: str, **kwargs) -> tuple[str, str]:
        """Format prompt with variables - legacy method"""
        prompt = self.get_prompt(prompt_name)
        if not prompt:
            raise ValueError(f"Prompt {prompt_name} not found")
        
        system_prompt = self.render_system_message(prompt_name, **kwargs)
        user_prompt = self.render_prompt(prompt_name, **kwargs)
        return system_prompt, user_prompt
