"""Centralized tool management and registration"""

from typing import List, Dict, Optional
from langchain.tools import Tool
import logging

class ToolManager:
    """Manages tool registration and access"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.logger = logging.getLogger(__name__)
        
    def register_tool(self, tool: Tool) -> None:
        """Register a tool for use"""
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
        
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get tool by name"""
        return self.tools.get(name)
        
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
        
    def get_tools_for_state(self, state: str) -> List[Tool]:
        """Get relevant tools for a specific state"""
        state_tool_mapping = {
            "identify_medication": ["patient_medication_history", "rxnorm_medication_lookup"],
            "check_authorization": ["insurance_formulary_check"],
            "select_pharmacy": ["find_nearby_pharmacies", "check_pharmacy_inventory", "goodrx_price_lookup"],
            "confirm_order": ["submit_refill_order"]
        }
        
        tool_names = state_tool_mapping.get(state, [])
        return [self.tools[name] for name in tool_names if name in self.tools]
