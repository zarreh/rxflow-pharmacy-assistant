# 🛠️ RxFlow Pharmacy Assistant - Developer Guide

**Version 1.0** | **Last Updated:** September 27, 2025

This comprehensive guide provides developers with everything needed to understand, extend, and maintain the RxFlow Pharmacy Assistant system.

---

## 🎯 Architecture Overview

### System Design Philosophy
RxFlow is built on a **modular, tool-based architecture** that emphasizes:
- **Separation of Concerns**: Each component has a specific responsibility
- **Extensibility**: Easy to add new tools and capabilities
- **Testability**: Comprehensive testing at all levels
- **Maintainability**: Clear code structure and documentation
- **Scalability**: Designed to handle growth in users and features

### Core Components

```
RxFlow System Architecture
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                   │
├─────────────────────────────────────────────────────────┤
│              Conversation Manager                       │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │   State Machine │    │     LangChain Agent         │ │
│  │                 │    │                             │ │
│  │  ┌───────────┐  │    │  ┌─────────────────────────┐│ │
│  │  │ Workflow  │  │    │  │      Tool Manager       ││ │
│  │  │   Types   │  │    │  │                         ││ │
│  │  └───────────┘  │    │  │ ┌─────────────────────┐ ││ │
│  └─────────────────┘    │  │ │    15 Specialized   │ ││ │
│                         │  │ │       Tools         │ ││ │
├─────────────────────────┼──┼─┼─────────────────────┼┼─┤
│     Services Layer      │  │ └─────────────────────┘│ │
│  ┌─────────────────────┐│  └─────────────────────────┘ │
│  │   Mock Data APIs    ││                             │
│  │                     ││                             │
│  │ ┌─────────────────┐ ││                             │
│  │ │  Patient Data   │ ││                             │
│  │ │  Pharmacy APIs  │ ││                             │
│  │ │  Insurance APIs │ ││                             │
│  │ │  RxNorm APIs    │ ││                             │
│  │ └─────────────────┘ ││                             │
│  └─────────────────────┘│                             │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Code Structure Deep Dive

### Project Organization

```
rxflow_pharmacy_assistant/
├── rxflow/                          # Main package
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Application entry point
│   ├── llm.py                      # LLM configuration and management
│   │
│   ├── config/                     # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py             # Pydantic settings with env vars
│   │
│   ├── workflow/                   # Core conversation logic
│   │   ├── __init__.py
│   │   ├── conversation_manager.py # Main conversation orchestration
│   │   ├── state_machine.py       # State transition logic
│   │   ├── workflow_types.py      # Type definitions and enums
│   │   ├── simple_conversation.py # Basic conversation handling
│   │   └── refill_conversation.py # Specialized refill workflows
│   │
│   ├── tools/                      # Specialized healthcare tools
│   │   ├── __init__.py
│   │   ├── tool_manager.py        # Tool registration and management
│   │   ├── patient_history_tool.py # Patient data and adherence
│   │   ├── rxnorm_tool.py         # RxNorm API integration
│   │   ├── pharmacy_tools.py      # Pharmacy location and inventory
│   │   ├── cost_tools.py          # Pricing and insurance tools
│   │   └── order_tools.py         # Order submission and tracking
│   │
│   ├── prompts/                    # AI prompt management
│   │   ├── __init__.py
│   │   └── prompt_manager.py      # Prompt templates and formatting
│   │
│   ├── services/                   # Backend services
│   │   ├── __init__.py
│   │   └── mock_data.py           # Mock API responses and data
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── logger.py              # Logging configuration
│       └── helpers.py             # Common utility functions
│
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_integration.py        # Integration test scenarios
│   └── test_unit_components.py    # Unit tests for components
│
├── docs/                           # Documentation
│   ├── README.md                  # Documentation index
│   ├── USER_GUIDE.md             # End-user documentation
│   ├── DEVELOPER_GUIDE.md        # This file
│   ├── API_REFERENCE.md          # API documentation
│   └── [step summaries]          # Implementation documentation
│
├── data/                           # Mock data files
│   ├── mock_patients.json        # Patient test data
│   ├── mock_pharmacies.json      # Pharmacy information
│   ├── mock_insurance.json       # Insurance formularies
│   └── mock_drugs.json           # Medication database
│
├── app.py                         # Streamlit application
├── pyproject.toml                # Poetry dependencies
├── Makefile                      # Development commands
└── README.md                     # Project overview
```

### Key Design Patterns

#### 1. **Tool-Based Architecture**
```python
# Tool Pattern Implementation
from langchain.tools import Tool
from typing import Dict, Any

class SpecializedTool:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def execute_function(self, query: str) -> Dict[str, Any]:
        """Core tool functionality"""
        try:
            # Business logic implementation
            result = self._process_query(query)
            return {"success": True, "data": result}
        except Exception as e:
            self.logger.error(f"Tool execution failed: {e}")
            return {"success": False, "error": str(e)}

# LangChain Tool Registration
tool = Tool(
    name="descriptive_tool_name",
    description="Clear description for LLM agent selection",
    func=SpecializedTool().execute_function
)
```

#### 2. **State Machine Pattern**
```python
# State Management Implementation
@dataclass
class StateTransition:
    from_state: RefillState
    to_state: RefillState
    trigger: str
    condition: Callable[[ConversationContext], bool]
    
class RefillStateMachine:
    def __init__(self):
        self.transitions = self._initialize_transitions()
        self.sessions = {}
    
    def transition(self, session_id: str, trigger: str, **kwargs):
        """Handle state transitions with validation"""
        # Implementation handles validation, logging, and context updates
```

#### 3. **Safe Wrapper Pattern**
```python
# Robust Parameter Handling
def safe_tool_wrapper(query: Union[str, Dict, None]) -> Dict:
    """Safe wrapper for tool parameter handling"""
    try:
        if query is None or query == {} or query == "":
            return {"success": False, "error": "No input provided", "source": "validation"}
        elif isinstance(query, dict):
            query = str(query.get("key", ""))
        elif not isinstance(query, str):
            query = str(query)
        return actual_tool_function(query)
    except Exception as e:
        return {"success": False, "error": f"Tool execution failed: {str(e)}", "source": "error"}
```

---

## 🔧 Development Setup

### Prerequisites
- **Python 3.12+** (required for latest type hinting features)
- **Poetry** (dependency management)
- **Git** (version control)
- **VS Code** (recommended IDE with Python extensions)

### Environment Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd rxflow_pharmacy_assistant

# 2. Install dependencies with Poetry
poetry install

# 3. Activate virtual environment
poetry shell

# 4. Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Verify installation
make test

# 6. Start development server
make run
```

### Development Commands

```bash
# Core development
make run          # Start Streamlit app
make test         # Run full test suite
make test-unit    # Run unit tests only
make test-integration  # Run integration tests
make lint         # Code quality checks
make format       # Format code with black

# Advanced development
make debug        # Run with debug logging
make watch        # Watch for changes and restart
make clean        # Clean cache and temp files

# Documentation
make docs         # Generate documentation (future)
make docs-serve   # Serve docs locally (future)
```

### Configuration Management

```python
# settings.py - Pydantic Configuration
from pydantic_settings import BaseSettings
from typing import Optional

class RxFlowSettings(BaseSettings):
    # LLM Configuration
    llm_provider: str = "ollama"
    llm_model: str = "llama3.2"
    openai_api_key: Optional[str] = None
    
    # API Configuration  
    rxnorm_api_key: Optional[str] = None
    goodrx_api_key: Optional[str] = None
    
    # Application Settings
    debug_mode: bool = False
    log_level: str = "INFO"
    session_timeout: int = 3600
    
    class Config:
        env_file = ".env"
        env_prefix = "RXFLOW_"

# Usage throughout application
from rxflow.config.settings import get_settings
settings = get_settings()
```

---

## 🏗️ Core Components

### 1. Conversation Manager

The `AdvancedConversationManager` is the central orchestrator:

```python
class AdvancedConversationManager:
    """
    Core conversation orchestration with:
    - LangChain agent integration
    - State machine management  
    - Tool coordination
    - Context persistence
    """
    
    def __init__(self):
        self.llm = get_conversational_llm()
        self.state_machine = RefillStateMachine()
        self.tools = self._register_tools()
        self.agent = self._setup_agent()
    
    async def handle_message(self, user_input: str, session_id: str) -> ConversationResponse:
        """Main message processing entry point"""
        # 1. Get or create conversation context
        # 2. Route to state-specific handler
        # 3. Execute agent with appropriate tools
        # 4. Update state machine
        # 5. Return structured response
```

**Key Methods:**
- `handle_message()`: Main entry point for all user interactions
- `_handle_identify_medication()`: Medication identification logic
- `_handle_confirm_dosage()`: Dosage verification and safety checks
- `_handle_select_pharmacy()`: Pharmacy selection and comparison
- `_handle_confirm_order()`: Final order processing

### 2. State Machine

The `RefillStateMachine` manages conversation flow:

```python
class RefillStateMachine:
    """
    Manages conversation states and transitions with:
    - Conditional transition logic
    - Session persistence
    - Context validation
    - Error handling
    """
    
    def transition(self, session_id: str, trigger: str, **context_updates):
        """Execute state transition with validation"""
        # 1. Validate current state and trigger
        # 2. Check transition conditions
        # 3. Update conversation context
        # 4. Log transition for debugging
        # 5. Return success/failure with new context
```

**Supported States:**
- `START`: Initial conversation state
- `IDENTIFY_MEDICATION`: Medication name extraction
- `CLARIFY_MEDICATION`: Disambiguation handling
- `CONFIRM_DOSAGE`: Dosage verification and safety
- `CHECK_AUTHORIZATION`: Insurance and PA verification
- `SELECT_PHARMACY`: Pharmacy selection and comparison
- `CONFIRM_ORDER`: Final order confirmation
- `ESCALATE_PA`: Prior authorization handling
- `COMPLETE`: Successful completion
- `ERROR`: Error handling and recovery

### 3. Tool System

#### Tool Registration Pattern
```python
# tools/tool_manager.py
class ToolManager:
    def __init__(self):
        self.tools = {}
        
    def register_tool(self, tool: Tool):
        """Register tool with validation"""
        self.tools[tool.name] = tool
        
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Retrieve tools by functional category"""
        # Implementation for categorized tool retrieval

# Automatic tool registration in __init__.py
from .patient_history_tool import patient_history_tool, adherence_tool
from .rxnorm_tool import rxnorm_tool, dosage_verification_tool
# ... all tool imports

AVAILABLE_TOOLS = [
    patient_history_tool, adherence_tool, allergy_tool,
    rxnorm_tool, dosage_verification_tool, interaction_tool,
    # ... all 15 tools
]
```

#### Tool Categories
1. **Patient History Tools** (3 tools)
   - Patient medication history retrieval
   - Adherence checking and analysis
   - Allergy and safety verification

2. **RxNorm Integration Tools** (3 tools)
   - Medication lookup and verification
   - Dosage validation
   - Drug interaction screening

3. **Pharmacy Service Tools** (4 tools)
   - Location finding and mapping
   - Inventory checking
   - Wait time estimation
   - Detailed pharmacy information

4. **Cost Optimization Tools** (4 tools)
   - GoodRx price lookup
   - Insurance formulary checking
   - Brand vs generic comparison
   - Prior authorization lookup

5. **Order Management Tools** (3 tools)
   - Refill order submission
   - Order tracking and status
   - Order cancellation

---

## 🧪 Testing Framework

### Test Structure

```python
# Integration Tests - Complete workflow validation
class PharmacyWorkflowTests(IntegrationTestSuite):
    async def test_happy_path_lisinopril_refill(self):
        """Test complete successful refill workflow"""
        messages = [
            "I need to refill my lisinopril",
            "Yes, it's 10mg once daily", 
            "CVS Pharmacy on Main Street is fine",
            "Yes, please place the order"
        ]
        
        expected_states = [
            RefillState.IDENTIFY_MEDICATION,
            RefillState.CONFIRM_DOSAGE,
            RefillState.SELECT_PHARMACY,
            RefillState.COMPLETE
        ]
        
        result = await self.run_conversation_flow(messages, expected_states)
        assert result["success"]

# Unit Tests - Individual component validation  
class TestConversationManagerUnit:
    def test_medication_identification(self):
        """Test medication identification logic"""
        # Test individual methods in isolation
        
    def test_state_transitions(self):
        """Test state machine behavior"""
        # Test transition logic and validation
```

### Testing Best Practices

#### 1. **Mock External Dependencies**
```python
@patch.object(ConversationManager, 'agent_executor')
async def test_with_mocked_agent(mock_executor):
    """Test with mocked LLM responses"""
    mock_executor.invoke.return_value = {'output': 'Test response'}
    # Test implementation
```

#### 2. **Comprehensive Scenario Coverage**
- **Happy Path**: Standard successful workflows
- **Error Handling**: Invalid inputs and system failures  
- **Edge Cases**: Unusual but valid scenarios
- **Integration**: End-to-end workflow validation

#### 3. **Performance Testing**
```python
def test_conversation_performance():
    """Validate response times meet requirements"""
    start_time = time.time()
    # Execute test scenario
    duration = time.time() - start_time
    assert duration < 5.0  # Response within 5 seconds
```

---

## 🔌 Extension Guidelines

### Adding New Tools

#### 1. **Create Tool Module**
```python
# tools/new_custom_tool.py
from langchain.tools import Tool
from typing import Dict
from ..utils.logger import get_logger

class NewCustomTool:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def execute_function(self, query: str) -> Dict:
        """Implement your tool logic here"""
        try:
            # Your implementation
            result = self._process_query(query)
            return {
                "success": True,
                "data": result,
                "source": "new_tool"
            }
        except Exception as e:
            self.logger.error(f"Tool error: {e}")
            return {
                "success": False,
                "error": str(e),
                "source": "new_tool"
            }

# Create LangChain tool
new_custom_tool = Tool(
    name="new_custom_tool",
    description="Clear description for LLM understanding",
    func=NewCustomTool().execute_function
)
```

#### 2. **Register Tool**
```python
# tools/__init__.py
from .new_custom_tool import new_custom_tool

AVAILABLE_TOOLS = [
    # ... existing tools
    new_custom_tool,
]
```

#### 3. **Add Tests**
```python
# tests/test_new_tool.py
def test_new_custom_tool():
    """Test new tool functionality"""
    result = new_custom_tool("test input")
    assert result["success"]
    assert "data" in result
```

### Adding New States

#### 1. **Define State Enum**
```python
# workflow/workflow_types.py
class RefillState(Enum):
    # ... existing states
    NEW_CUSTOM_STATE = "new_custom_state"
```

#### 2. **Add State Handler**
```python
# workflow/conversation_manager.py
def _handle_new_custom_state(self, user_input: str, context: ConversationContext, history: List) -> ConversationResponse:
    """Handle new custom state logic"""
    # Your implementation
    return ConversationResponse(
        message="Response for new state",
        session_id=context.session_id,
        current_state=context.current_state
    )
```

#### 3. **Define Transitions**
```python
# workflow/state_machine.py
StateTransition(
    RefillState.EXISTING_STATE, 
    RefillState.NEW_CUSTOM_STATE,
    trigger="custom_trigger",
    condition=lambda ctx: your_condition(ctx),
    description="Transition to new custom state"
)
```

### Extending Mock Data

#### 1. **Add Data Structures**
```python
# services/mock_data.py
NEW_DATA_CATEGORY = {
    "item_1": {
        "property": "value",
        "nested": {
            "data": "structure"
        }
    }
}
```

#### 2. **Create Access Functions**
```python
def get_new_data(identifier: str) -> Dict:
    """Retrieve new data by identifier"""
    return NEW_DATA_CATEGORY.get(identifier, {})
```

---

## 🚀 Deployment Guide

### Production Configuration

#### 1. **Environment Variables**
```bash
# .env.production
RXFLOW_ENV=production
RXFLOW_DEBUG_MODE=false
RXFLOW_LOG_LEVEL=INFO

# LLM Configuration
RXFLOW_LLM_PROVIDER=openai
OPENAI_API_KEY=your_production_key

# API Keys
RXFLOW_RXNORM_API_KEY=your_rxnorm_key
RXFLOW_GOODRX_API_KEY=your_goodrx_key

# Security
RXFLOW_SESSION_TIMEOUT=1800
RXFLOW_ENABLE_ANALYTICS=true
```

#### 2. **Docker Deployment**
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 3. **Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'
services:
  rxflow:
    build: .
    ports:
      - "8501:8501"
    environment:
      - RXFLOW_ENV=production
    env_file:
      - .env.production
    volumes:
      - ./data:/app/data:ro
    restart: unless-stopped
```

### Monitoring and Logging

#### 1. **Production Logging**
```python
# utils/logger.py - Production configuration
import logging
import structlog

def configure_production_logging():
    """Configure structured logging for production"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )
```

#### 2. **Health Checks**
```python
# health.py - Health check endpoint
async def health_check():
    """System health validation"""
    checks = {
        "database": await check_database_connection(),
        "llm": await check_llm_connectivity(), 
        "memory": check_memory_usage(),
        "disk": check_disk_space()
    }
    
    healthy = all(checks.values())
    status_code = 200 if healthy else 503
    
    return {"status": "healthy" if healthy else "unhealthy", "checks": checks}
```

---

## 🐛 Debugging & Troubleshooting

### Common Issues

#### 1. **LLM Connection Issues**
```python
# Debug LLM connectivity
from rxflow.llm import get_conversational_llm

try:
    llm = get_conversational_llm()
    response = llm.invoke("test message")
    print(f"LLM Response: {response}")
except Exception as e:
    print(f"LLM Error: {e}")
    # Check configuration, API keys, network connectivity
```

#### 2. **State Machine Issues**
```python
# Debug state transitions
def debug_state_machine(session_id: str):
    """Debug state machine for session"""
    sm = RefillStateMachine()
    context = sm.get_session(session_id)
    
    print(f"Current State: {context.current_state}")
    print(f"Valid Triggers: {sm.get_valid_triggers(session_id)}")
    print(f"Session History: {sm.get_session_history(session_id)}")
```

#### 3. **Tool Execution Issues**
```python
# Debug tool execution
def debug_tool_execution(tool_name: str, input_data: str):
    """Debug individual tool execution"""
    from rxflow.tools import get_tool_by_name
    
    tool = get_tool_by_name(tool_name)
    try:
        result = tool.run(input_data)
        print(f"Tool Success: {result}")
    except Exception as e:
        print(f"Tool Error: {e}")
        import traceback
        traceback.print_exc()
```

### Performance Debugging

#### 1. **Response Time Analysis**
```python
import time
from functools import wraps

def measure_performance(func):
    """Decorator to measure function performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start_time
        
        logger.info(f"Function {func.__name__} took {duration:.2f}s")
        return result
    return wrapper

# Usage
@measure_performance
async def handle_message(self, user_input: str):
    # Implementation
```

#### 2. **Memory Usage Monitoring**
```python
import psutil
import tracemalloc

def monitor_memory_usage():
    """Monitor application memory usage"""
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"RSS Memory: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS Memory: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Track memory allocations
    tracemalloc.start()
    # ... your code here
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    
    for stat in top_stats[:10]:
        print(stat)
```

---

## 📊 Performance Optimization

### Response Time Optimization

#### 1. **Async Processing**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_tool_execution(tools_and_inputs):
    """Execute multiple tools in parallel"""
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor() as executor:
        tasks = [
            loop.run_in_executor(executor, tool.run, input_data)
            for tool, input_data in tools_and_inputs
        ]
        
        results = await asyncio.gather(*tasks)
        return results
```

#### 2. **Caching Strategy**
```python
from functools import lru_cache
import redis

# In-memory caching for frequent lookups
@lru_cache(maxsize=1000)
def get_medication_info(medication_name: str):
    """Cache medication information"""
    return expensive_medication_lookup(medication_name)

# Redis caching for session data
class SessionCache:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
    
    def get_session(self, session_id: str):
        """Retrieve cached session data"""
        data = self.redis.get(f"session:{session_id}")
        return json.loads(data) if data else None
    
    def set_session(self, session_id: str, data: dict, ttl: int = 3600):
        """Cache session data with TTL"""
        self.redis.setex(
            f"session:{session_id}", 
            ttl, 
            json.dumps(data)
        )
```

### Memory Optimization

#### 1. **Efficient Data Structures**
```python
from typing import NamedTuple
import sys

# Use NamedTuple for immutable data structures
class PatientRecord(NamedTuple):
    patient_id: str
    name: str
    medications: list
    
# Memory-efficient data loading
def load_large_dataset_efficiently(file_path: str):
    """Load large datasets using generators"""
    with open(file_path, 'r') as f:
        for line in f:
            yield json.loads(line)  # Process one record at a time
```

#### 2. **Resource Cleanup**
```python
import weakref
from contextlib import contextmanager

@contextmanager
def managed_llm_connection():
    """Ensure proper cleanup of LLM connections"""
    llm = None
    try:
        llm = get_conversational_llm()
        yield llm
    finally:
        if llm and hasattr(llm, 'cleanup'):
            llm.cleanup()
```

---

## 🔒 Security Considerations

### Input Validation

```python
import re
from typing import Any, Dict

def validate_medication_name(name: str) -> bool:
    """Validate medication name input"""
    if not isinstance(name, str):
        return False
    
    # Allow letters, numbers, spaces, hyphens
    pattern = r'^[a-zA-Z0-9\s\-]{1,100}$'
    return bool(re.match(pattern, name.strip()))

def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input for safety"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>\"\'&]', '', user_input)
    return sanitized.strip()[:1000]  # Limit length

def validate_tool_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate tool parameters before execution"""
    validated = {}
    for key, value in params.items():
        if isinstance(value, str):
            validated[key] = sanitize_user_input(value)
        elif isinstance(value, (int, float)):
            validated[key] = value
        # Add more validation as needed
    return validated
```

### Session Security

```python
import secrets
import jwt
from datetime import datetime, timedelta

class SecureSessionManager:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
    
    def create_session(self, patient_id: str) -> str:
        """Create secure session token"""
        payload = {
            'patient_id': patient_id,
            'session_id': secrets.token_urlsafe(32),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=1)).isoformat()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def validate_session(self, token: str) -> Dict[str, Any]:
        """Validate and decode session token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload['expires_at'])
            if datetime.utcnow() > expires_at:
                raise ValueError("Session expired")
            
            return payload
        except jwt.InvalidTokenError:
            raise ValueError("Invalid session token")
```

---

## 📈 Scaling Strategies

### Horizontal Scaling

#### 1. **Stateless Application Design**
```python
# Store session data externally
class ExternalSessionStore:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
    
    def store_context(self, session_id: str, context: ConversationContext):
        """Store conversation context externally"""
        data = {
            'current_state': context.current_state.value,
            'patient_id': context.patient_id,
            'medication': context.medication,
            'last_updated': datetime.utcnow().isoformat()
        }
        self.redis.setex(f"context:{session_id}", 3600, json.dumps(data))
```

#### 2. **Load Balancing**
```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  rxflow:
    build: .
    deploy:
      replicas: 3
    environment:
      - RXFLOW_REDIS_URL=redis://redis:6379
  
  redis:
    image: redis:alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

volumes:
  redis_data:
```

### Performance Monitoring

#### 1. **Metrics Collection**
```python
import time
from collections import defaultdict, deque
from threading import Lock

class PerformanceMetrics:
    def __init__(self):
        self.metrics = defaultdict(deque)
        self.lock = Lock()
    
    def record_response_time(self, operation: str, duration: float):
        """Record operation response time"""
        with self.lock:
            self.metrics[f"{operation}_response_time"].append({
                'timestamp': time.time(),
                'duration': duration
            })
            
            # Keep only last 1000 entries
            if len(self.metrics[f"{operation}_response_time"]) > 1000:
                self.metrics[f"{operation}_response_time"].popleft()
    
    def get_average_response_time(self, operation: str, window_seconds: int = 300):
        """Get average response time for operation in time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        with self.lock:
            recent_metrics = [
                m for m in self.metrics[f"{operation}_response_time"]
                if m['timestamp'] > cutoff_time
            ]
            
            if not recent_metrics:
                return 0
            
            return sum(m['duration'] for m in recent_metrics) / len(recent_metrics)
```

---

## 🎓 Best Practices

### Code Quality

#### 1. **Type Hints and Documentation**
```python
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass

@dataclass
class ConversationResponse:
    """
    Standardized response from conversation processing.
    
    Attributes:
        message: The AI-generated response message
        session_id: Unique session identifier
        current_state: Current workflow state
        tool_results: Results from tool executions
        next_steps: Optional guidance for user
        error: Error message if processing failed
    """
    message: str
    session_id: str
    current_state: RefillState
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    next_steps: Optional[str] = None
    error: Optional[str] = None

def process_medication_request(
    user_input: str,
    session_context: ConversationContext,
    available_tools: List[Tool]
) -> ConversationResponse:
    """
    Process user medication request with full context.
    
    Args:
        user_input: Raw user message
        session_context: Current conversation context
        available_tools: Tools available for processing
        
    Returns:
        Structured conversation response
        
    Raises:
        ValidationError: If input validation fails
        ProcessingError: If conversation processing fails
    """
```

#### 2. **Error Handling Patterns**
```python
from enum import Enum
from typing import Optional

class ErrorType(Enum):
    VALIDATION_ERROR = "validation_error"
    TOOL_EXECUTION_ERROR = "tool_execution_error"
    LLM_ERROR = "llm_error"
    SYSTEM_ERROR = "system_error"

class RxFlowException(Exception):
    """Base exception for RxFlow system"""
    def __init__(self, message: str, error_type: ErrorType, details: Optional[Dict] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}

def safe_execution_wrapper(func):
    """Decorator for safe function execution with logging"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except RxFlowException:
            raise  # Re-raise known exceptions
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
            raise RxFlowException(
                message=f"System error in {func.__name__}",
                error_type=ErrorType.SYSTEM_ERROR,
                details={'original_error': str(e)}
            )
    return wrapper
```

#### 3. **Testing Standards**
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

class TestConversationManager:
    """Comprehensive test suite for conversation management"""
    
    @pytest.fixture
    def conversation_manager(self):
        """Provide clean conversation manager instance"""
        return ConversationManager()
    
    @pytest.fixture
    def mock_llm_response(self):
        """Provide standardized mock LLM response"""
        return {
            'output': 'I can help you refill your medication.'
        }
    
    @pytest.mark.asyncio
    async def test_medication_identification_success(
        self, 
        conversation_manager,
        mock_llm_response
    ):
        """Test successful medication identification workflow"""
        # Arrange
        user_input = "I need to refill my lisinopril"
        session_id = "test_session"
        
        with patch.object(conversation_manager, 'agent_executor') as mock_executor:
            mock_executor.invoke.return_value = mock_llm_response
            
            # Act
            result = await conversation_manager.handle_message(user_input, session_id)
            
            # Assert
            assert result.session_id == session_id
            assert result.message is not None
            assert result.current_state in [RefillState.IDENTIFY_MEDICATION, RefillState.CONFIRM_DOSAGE]
            
    @pytest.mark.parametrize("invalid_input", [
        "",
        None,
        " " * 1000,  # Too long
        "<script>alert('test')</script>",  # Potentially malicious
    ])
    async def test_input_validation(self, conversation_manager, invalid_input):
        """Test input validation handles edge cases"""
        with pytest.raises(ValidationError):
            await conversation_manager.handle_message(invalid_input, "test_session")
```

---

## 📚 Resources & References

### Documentation
- **LangChain Documentation**: https://python.langchain.com/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **Pydantic Documentation**: https://pydantic-docs.helpmanual.io/
- **Poetry Documentation**: https://python-poetry.org/docs/

### Healthcare APIs
- **RxNorm API**: https://rxnav.nlm.nih.gov/
- **FDA Drug Database**: https://open.fda.gov/
- **National Drug Code Directory**: https://www.fda.gov/drugs/drug-approvals-and-databases/national-drug-code-directory

### Development Tools
- **VS Code**: Recommended IDE with Python extensions
- **Black**: Code formatting
- **MyPy**: Static type checking
- **Pytest**: Testing framework
- **Pre-commit**: Git hooks for code quality

### Monitoring & Observability
- **Prometheus**: Metrics collection
- **Grafana**: Metrics visualization
- **Sentry**: Error tracking
- **Structlog**: Structured logging

---

## 🤝 Contributing

### Development Workflow

1. **Fork Repository**
   ```bash
   git fork <repository-url>
   cd rxflow_pharmacy_assistant
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow coding standards
   - Add comprehensive tests
   - Update documentation

4. **Run Quality Checks**
   ```bash
   make lint        # Code quality
   make test        # All tests
   make format      # Code formatting
   ```

5. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: descriptive commit message"
   ```

6. **Submit Pull Request**
   - Clear description of changes
   - Reference related issues
   - Include test results

### Code Review Guidelines

- **Code Quality**: Follows established patterns and standards
- **Testing**: Comprehensive test coverage for new features
- **Documentation**: Updated documentation for changes
- **Security**: No security vulnerabilities introduced
- **Performance**: No significant performance regressions

---

**Need Help?** 
- Check the [User Guide](USER_GUIDE.md) for usage questions
- Review the [API Reference](API_REFERENCE.md) for technical details
- Contact the development team for architecture questions
- Submit issues on GitHub for bug reports and feature requests

---

*This developer guide is maintained by the RxFlow development team. Please keep it updated as the system evolves.*