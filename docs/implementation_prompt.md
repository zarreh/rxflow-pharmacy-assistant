# Pharmacy Refill AI Assistant - Complete Implementation Prompt

## Overview
This document contains the complete implementation prompt for building the pharmacy refill AI assistant for the Qventus interview challenge.

## Implementation Prompt for AI Agent


# Pharmacy Refill AI Assistant - Implementation Instructions

You are helping implement a pharmacy refill AI assistant for a Qventus interview challenge. The project should demonstrate conversational AI with tool integration in healthcare.

## Project Context
- **Position**: Forward-Deployed AI Solution Architect at Qventus
- **Time Budget**: 4 hours total
- **Key Requirements**: Tool-based AI assistant, state machine conversation flow, real + mock API integrations
- **Existing Code**: Basic conversation manager and LLM setup already exist

## Implementation Order

### STEP 1: Update Project Structure (15 minutes)
First, update the project structure to support the new tool-based architecture:


rxflow-pharmacy-assistant/
├── README.md
├── pyproject.toml
├── app.py                          # Streamlit frontend
├── rxflow/
│   ├── __init__.py
│   ├── llm.py                     # Existing LLM management
│   ├── tools/                     # NEW directory
│   │   ├── __init__.py
│   │   ├── patient_history_tool.py
│   │   ├── rxnorm_tool.py
│   │   ├── pharmacy_tools.py     # Pharmacy inventory + location
│   │   ├── cost_tools.py         # GoodRx + insurance mocks
│   │   └── tool_manager.py       # Tool registration and management
│   ├── prompts/                   # NEW directory
│   │   ├── __init__.py
│   │   ├── prompt_manager.py
│   │   └── templates.py
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── state_machine.py      # NEW: Conversation state machine
│   │   ├── conversation_manager.py # UPDATE: Add tool integration
│   │   └── workflow_types.py      # NEW: Enums and types
│   ├── services/                  # Keep for non-tool logic
│   │   ├── __init__.py
│   │   └── mock_data.py          # Centralized mock data
│   ├── config/
│   │   └── settings.py
│   └── utils/
│       └── logger.py
├── docs/
│   ├── flow_diagram.md           # Mermaid state machine diagram
│   └── optimization_scalability.md
└── tests/
    └── test_tools/
```

### STEP 2: Create Mock Data Module (20 minutes)
Create a centralized mock data module that all tools can use:

File: `rxflow/services/mock_data.py`
- Patient medication histories
- Drug database (name, dosage, RxCUI)
- Pharmacy locations and inventory
- Insurance formulary data
- Price information

### STEP 3: Implement Core Tools (45 minutes)
Create the following tools in order:

1. **Patient History Tool** (`rxflow/tools/patient_history_tool.py`)
   - get_medication_history(patient_id, medication_name)
   - check_adherence(patient_id, medication_name)
   - get_allergies(patient_id)
   - Return structured JSON responses

2. **RxNorm Tool** (`rxflow/tools/rxnorm_tool.py`)
   - search_medication(medication_name) - Real API with fallback
   - get_interactions(rxcui)
   - verify_dosage(medication, dosage)
   - Include timeout handling and mock fallback

3. **Pharmacy Tools** (`rxflow/tools/pharmacy_tools.py`)
   - find_nearby_pharmacies(location, radius)
   - check_inventory(pharmacy_id, medication)
   - get_wait_times(pharmacy_id)

4. **Cost Tools** (`rxflow/tools/cost_tools.py`)
   - get_goodrx_prices(medication, dosage, quantity)
   - check_insurance_coverage(medication, plan_id)
   - calculate_savings(prices)

### STEP 4: Create Prompt Management System (30 minutes)
File: `rxflow/prompts/prompt_manager.py`

Create structured prompts for:
- Medication extraction
- Disambiguation queries
- Cost comparison explanations
- Prior authorization handling
- Order confirmation

Each prompt should have:
- System message
- User template
- Examples (few-shot)
- Version tracking

### STEP 5: Implement State Machine (30 minutes)
File: `rxflow/workflow/state_machine.py`

Define states:
- START
- IDENTIFY_MEDICATION
- CLARIFY_MEDICATION
- CONFIRM_DOSAGE
- CHECK_AUTHORIZATION
- SELECT_PHARMACY
- CONFIRM_ORDER
- ESCALATE_PA
- COMPLETE

Include:
- Valid transitions between states
- Trigger conditions
- Context storage
- State persistence

### STEP 6: Update Conversation Manager (45 minutes)
File: `rxflow/workflow/conversation_manager.py`

Integrate:
- LangChain agent with tools
- State machine for flow control
- Prompt manager for responses
- Explicit logging of AI usage
- Error handling and fallbacks

Key methods:
- handle_message(user_input, session_id)
- State-specific handlers (handle_identify_medication, etc.)
- Tool result processing
- Natural language response generation

### STEP 7: Create Flow Diagram (15 minutes)
File: `docs/flow_diagram.md`

Create a Mermaid state diagram showing:
- All states and transitions
- Decision points
- Tool usage annotations
- Happy path + escalation path

### STEP 8: Update Streamlit UI (30 minutes)
File: `app.py`

Enhance to show:
- Conversation history
- Current state (for demo purposes)
- Tool usage logs (collapsible)
- Cost savings achieved
- Session management

### STEP 9: Integration Testing (30 minutes)
Create test scenarios:
1. Happy path: Simple lisinopril refill
2. Disambiguation: "blood pressure medication"
3. Prior auth: Eliquis refill
4. Cost optimization: Brand vs generic
5. Error handling: Unknown medication

### STEP 10: Documentation & Polish (30 minutes)
1. Update README with setup instructions
2. Complete optimization_scalability.md
3. Add inline comments marking AI usage
4. Ensure all deliverables are ready

## Key Implementation Notes

1. **Tool Implementation Pattern**:
```python
from langchain.tools import Tool
from typing import Dict

class YourTool:
    def method_name(self, param: str) -> Dict:
        # Implementation
        return {"result": "data"}

your_tool = Tool(
    name="tool_name",
    description="Clear description for LLM to understand when to use",
    func=lambda x: YourTool().method_name(x)
)
```

2. **State Machine Pattern**:
```python
transitions = {
    State.START: {
        "medication_mentioned": State.IDENTIFY_MEDICATION
    }
}
```

3. **Explicit AI Usage Marking**:
```python
self.logger.info("[AI USAGE] Extracting medication from user input")
# LLM call here
self.logger.info("[AI USAGE] Generated response using GPT-4")
```

4. **Mock Data Structure**:
```python
MOCK_PATIENTS = {
    "12345": {
        "medications": [...],
        "allergies": [...],
        "insurance": "BlueCross"
    }
}
```

## Success Criteria
- Clean, modular architecture
- Clear separation of AI vs deterministic logic
- At least one real API integration (RxNorm)
- Complete refill workflow demonstration
- Proper error handling
- Well-documented code

## Time Management
- Steps 1-4: First 1.5 hours (Core infrastructure)
- Steps 5-6: Next 1.5 hours (Integration)
- Steps 7-10: Final 1 hour (Polish and documentation)

Start with Step 1 and proceed sequentially. Each step builds on the previous one.
```

## Supporting Code Structure

### Tool Module Initialization
File: `rxflow/tools/__init__.py`
```python
"""Tools for pharmacy refill assistant"""

from .patient_history_tool import patient_history_tool
from .rxnorm_tool import rxnorm_tool
from .pharmacy_tools import pharmacy_inventory_tool, pharmacy_location_tool
from .cost_tools import goodrx_tool, insurance_tool
from .tool_manager import ToolManager

__all__ = [
    "patient_history_tool",
    "rxnorm_tool", 
    "pharmacy_inventory_tool",
    "pharmacy_location_tool",
    "goodrx_tool",
    "insurance_tool",
    "ToolManager"
]
```

### Prompts Module Initialization
File: `rxflow/prompts/__init__.py`
```python
"""Prompt management for pharmacy assistant"""

from .prompt_manager import PromptManager
from .templates import PROMPT_TEMPLATES

__all__ = ["PromptManager", "PROMPT_TEMPLATES"]
```

### Workflow Types Definition
File: `rxflow/workflow/workflow_types.py`
```python
"""Shared types and enums for workflow management"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List

class RefillState(Enum):
    """States in the pharmacy refill workflow"""
    START = "start"
    IDENTIFY_MEDICATION = "identify_medication"
    CLARIFY_MEDICATION = "clarify_medication"
    CONFIRM_DOSAGE = "confirm_dosage"
    CHECK_AUTHORIZATION = "check_authorization"
    SELECT_PHARMACY = "select_pharmacy"
    CONFIRM_ORDER = "confirm_order"
    ESCALATE_PA = "escalate_pa"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class ConversationContext:
    """Holds conversation state and data"""
    session_id: str
    current_state: RefillState
    patient_id: str = "12345"  # Mock for demo
    medication: Optional[Dict] = None
    dosage: Optional[str] = None
    pharmacy: Optional[Dict] = None
    insurance_info: Optional[Dict] = None
    order_details: Optional[Dict] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "current_state": self.current_state.value,
            "patient_id": self.patient_id,
            "medication": self.medication,
            "dosage": self.dosage,
            "pharmacy": self.pharmacy,
            "insurance_info": self.insurance_info,
            "order_details": self.order_details,
            "error_message": self.error_message
        }

@dataclass
class ToolResult:
    """Standardized tool response format"""
    success: bool
    data: Optional[Dict] = None
    error: Optional[str] = None
    source: str = "unknown"  # "api", "mock", "cache"
```

### Tool Manager
File: `rxflow/tools/tool_manager.py`
```python
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
```

## Summary
This comprehensive prompt provides step-by-step instructions for implementing the pharmacy refill AI assistant. It includes:

1. Clear project structure and file organization
2. Detailed implementation steps with time estimates
3. Code patterns and examples
4. Success criteria and time management
5. Supporting code for key modules

The implementation focuses on:
- Tool-based architecture for scalability
- State machine for conversation flow
- Mix of real (RxNorm) and mock APIs
- Clear separation of AI vs deterministic logic
- Proper error handling and fallbacks

Follow these instructions sequentially to build a working prototype within the 4-hour timeframe.
