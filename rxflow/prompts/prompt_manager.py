"""Centralized prompt management with clear separation of concerns"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PromptTemplate:
    """Structured prompt template"""
    name: str
    system_prompt: str
    user_template: str
    examples: Optional[List[Dict]] = None
    version: str = "1.0"

class PromptManager:
    """Manages all prompts with versioning and clear structure"""
    
    def __init__(self):
        self.prompts = {
            "medication_extraction": PromptTemplate(
                name="medication_extraction",
                system_prompt="""You are a pharmacy assistant AI. Extract medication information from user input.
                Return a JSON with: {medication_name, dosage, quantity, refill_type}
                If information is missing, mark as null.""",
                user_template="User said: {user_input}",
                examples=[
                    {"input": "I need to refill my lisinopril 10mg", 
                     "output": {"medication_name": "lisinopril", "dosage": "10mg", "quantity": null, "refill_type": "refill"}}
                ]
            ),
            
            "medication_disambiguation": PromptTemplate(
                name="medication_disambiguation", 
                system_prompt="""Help clarify ambiguous medication names. Given a user input and list of possible matches,
                ask a clarifying question to identify the correct medication.""",
                user_template="User said: {user_input}\nPossible matches: {matches}",
            ),
            
            "pharmacy_recommendation": PromptTemplate(
                name="pharmacy_recommendation",
                system_prompt="""Recommend pharmacies based on user preferences. Consider cost, distance, and wait time.
                Explain the tradeoffs clearly.""",
                user_template="Options: {pharmacy_options}\nUser preference: {preference}",
            )
        }
    
    def get_prompt(self, prompt_name: str) -> PromptTemplate:
        """Get prompt by name with versioning support"""
        return self.prompts.get(prompt_name)
    
    def format_prompt(self, prompt_name: str, **kwargs) -> tuple[str, str]:
        """Format prompt with variables"""
        template = self.get_prompt(prompt_name)
        if not template:
            raise ValueError(f"Prompt {prompt_name} not found")
        
        user_prompt = template.user_template.format(**kwargs)
        return template.system_prompt, user_prompt
