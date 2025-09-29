# Conversation Manager API

The ConversationManager is the core orchestration layer for RxFlow, coordinating between LangChain agents, specialized pharmacy tools, and conversation state management.

## Overview

## ConversationManager

The `ConversationManager` class orchestrates different types of conversations and manages their lifecycles in the RxFlow system.

```python
# Note: Full API documentation will be auto-generated when the module is available
# ::: rxflow.workflow.conversation_manager.ConversationManager
```

## ConversationResponse

::: rxflow.workflow.conversation_manager.ConversationResponse
    options:
      show_root_heading: true
      show_source: true
      heading_level: 2

## Usage Examples

### Basic Conversation Processing

```python
from rxflow.workflow.conversation_manager import ConversationManager

# Initialize the conversation manager
manager = ConversationManager()

# Process a patient request
response = await manager.process_message(
    session_id="user_123",
    message="I need to refill my omeprazole"
)

print(f"AI Response: {response.message}")
print(f"Current State: {response.current_state}")

if response.error:
    print(f"Error occurred: {response.error}")
```

### Session Management

```python
# Create a new session
session_data = manager.create_session("new_user_456")
print(f"Created session: {session_data['session_id']}")

# Retrieve existing session
existing_session = manager.get_session("new_user_456")
if existing_session:
    print(f"Session state: {existing_session['state']}")

# Get conversation history
history = manager.get_conversation_history("new_user_456")
for message in history:
    print(f"{message['role']}: {message['content']}")

# Clear session when done
manager.clear_session("new_user_456")
```

### Advanced Workflow Management

```python
import asyncio
from rxflow.workflow.workflow_types import WorkflowState

async def process_medication_refill():
    """Complete medication refill workflow example"""
    manager = ConversationManager()
    session_id = "patient_workflow_001"
    
    # Step 1: Initial medication request
    response1 = await manager.process_message(
        session_id=session_id,
        message="I need to refill my blood pressure medication"
    )
    
    print(f"Step 1 - {response1.current_state}: {response1.message}")
    
    # Step 2: Confirm medication
    response2 = await manager.process_message(
        session_id=session_id,
        message="Yes, that's the correct medication"
    )
    
    print(f"Step 2 - {response2.current_state}: {response2.message}")
    
    # Step 3: Choose cost option
    response3 = await manager.process_message(
        session_id=session_id,
        message="I'll take the generic option"
    )
    
    print(f"Step 3 - {response3.current_state}: {response3.message}")
    
    # Continue until workflow completion
    return response3.current_state == WorkflowState.COMPLETED

# Run the workflow
result = asyncio.run(process_medication_refill())
print(f"Workflow completed successfully: {result}")
```

## Integration Patterns

### Tool Result Processing

```python
async def process_with_tool_monitoring():
    """Monitor tool execution during conversation processing"""
    manager = ConversationManager()
    
    response = await manager.process_message(
        session_id="monitoring_session",
        message="Find the cheapest omeprazole near me"
    )
    
    # Check what tools were executed
    if response.tool_results:
        print(f"Tools executed: {len(response.tool_results)}")
        for tool_result in response.tool_results:
            print(f"Tool: {tool_result.get('tool_name', 'unknown')}")
            print(f"Result: {tool_result.get('result', 'no result')}")
    
    return response
```

### Error Handling Patterns

```python
async def robust_conversation_processing():
    """Robust conversation processing with error handling"""
    manager = ConversationManager()
    
    try:
        response = await manager.process_message(
            session_id="error_handling_session",
            message="I need help with my prescription"
        )
        
        if response.error:
            # Handle application-level errors
            print(f"Application error: {response.error}")
            # Could implement retry logic or user notification
            
        elif response.current_state == WorkflowState.ESCALATED:
            # Handle escalation scenarios
            print(f"Escalated: {response.message}")
            # Notify pharmacist or physician
            
        else:
            # Normal processing
            print(f"Success: {response.message}")
            
    except Exception as e:
        # Handle system-level exceptions
        print(f"System error: {str(e)}")
        # Implement fallback behavior
```

### Batch Processing

```python
async def batch_process_messages():
    """Process multiple messages for analytics or testing"""
    manager = ConversationManager()
    
    test_messages = [
        "I need to refill omeprazole",
        "What pharmacies are nearby?", 
        "Check my insurance coverage",
        "Find the cheapest option"
    ]
    
    results = []
    session_id = "batch_session"
    
    for message in test_messages:
        response = await manager.process_message(session_id, message)
        results.append({
            'message': message,
            'response': response.message,
            'state': response.current_state,
            'success': not bool(response.error)
        })
        
        # Small delay between messages for realistic testing
        await asyncio.sleep(1)
    
    return results
```

## Configuration and Customization

### Custom Tool Registration

```python
from rxflow.workflow.conversation_manager import ConversationManager
from langchain.tools import Tool

class CustomConversationManager(ConversationManager):
    """Extended conversation manager with custom tools"""
    
    def _register_tools(self) -> None:
        # Call parent method to get standard tools
        super()._register_tools()
        
        # Add custom tool
        custom_tool = Tool(
            name="CustomPharmacyTool",
            description="Custom pharmacy integration",
            func=self._custom_pharmacy_function
        )
        
        self.tools.append(custom_tool)
        print(f"Registered {len(self.tools)} tools (including custom)")
    
    def _custom_pharmacy_function(self, query: str) -> str:
        """Custom pharmacy integration logic"""
        return f"Custom pharmacy result for: {query}"

# Use custom manager
custom_manager = CustomConversationManager()
```

### Session Persistence

```python
import json
from pathlib import Path

class PersistentConversationManager(ConversationManager):
    """Conversation manager with session persistence"""
    
    def __init__(self, session_file: str = "sessions.json"):
        super().__init__()
        self.session_file = Path(session_file)
        self._load_sessions()
    
    def _load_sessions(self):
        """Load sessions from file"""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                self.sessions = json.load(f)
    
    def _save_sessions(self):
        """Save sessions to file"""
        with open(self.session_file, 'w') as f:
            json.dump(self.sessions, f, indent=2, default=str)
    
    def create_session(self, session_id: str):
        """Override to add persistence"""
        result = super().create_session(session_id)
        self._save_sessions()
        return result
    
    def clear_session(self, session_id: str) -> bool:
        """Override to add persistence"""
        result = super().clear_session(session_id)
        if result:
            self._save_sessions()
        return result

# Use persistent manager
persistent_manager = PersistentConversationManager("my_sessions.json")
```

## Performance Considerations

### Async Best Practices

```python
import asyncio
from typing import List

async def concurrent_session_processing():
    """Handle multiple concurrent sessions efficiently"""
    manager = ConversationManager()
    
    # Process multiple sessions concurrently
    tasks = []
    for i in range(5):
        task = manager.process_message(
            session_id=f"concurrent_session_{i}",
            message="I need medication help"
        )
        tasks.append(task)
    
    # Wait for all sessions to complete
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    successful = [r for r in responses if not isinstance(r, Exception)]
    errors = [r for r in responses if isinstance(r, Exception)]
    
    print(f"Processed {len(successful)} sessions successfully")
    if errors:
        print(f"Encountered {len(errors)} errors")
    
    return successful
```

### Memory Management

```python
class OptimizedConversationManager(ConversationManager):
    """Memory-optimized conversation manager"""
    
    def __init__(self, max_sessions: int = 100):
        super().__init__()
        self.max_sessions = max_sessions
    
    def create_session(self, session_id: str):
        """Override with session limit enforcement"""
        # Clean up old sessions if at limit
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest sessions
            oldest_sessions = sorted(
                self.sessions.items(),
                key=lambda x: x[1].get('created_at', 0)
            )
            
            for old_session_id, _ in oldest_sessions[:10]:
                self.clear_session(old_session_id)
        
        return super().create_session(session_id)

# Use optimized manager for high-traffic scenarios
optimized_manager = OptimizedConversationManager(max_sessions=50)
```

## Testing and Debugging

### Unit Testing Pattern

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_conversation_manager():
    """Test conversation manager functionality"""
    manager = ConversationManager()
    
    # Test session creation
    session = manager.create_session("test_session")
    assert session['session_id'] == "test_session"
    
    # Test message processing
    with patch.object(manager, 'agent_executor') as mock_agent:
        mock_agent.ainvoke = AsyncMock(return_value={'output': 'Test response'})
        
        response = await manager.process_message(
            session_id="test_session",
            message="Test message"
        )
        
        assert response.message == "Test response"
        assert response.session_id == "test_session"
    
    # Test session cleanup
    result = manager.clear_session("test_session")
    assert result is True
```

### Debug Information

```python
async def debug_conversation_flow():
    """Enable detailed debugging for conversation flow"""
    import logging
    
    # Enable debug logging
    logging.getLogger('rxflow').setLevel(logging.DEBUG)
    
    manager = ConversationManager()
    
    response = await manager.process_message(
        session_id="debug_session",
        message="Debug test message"
    )
    
    # Access debug information
    session = manager.get_session("debug_session")
    print(f"Session data: {session}")
    print(f"Tool count: {len(manager.tools)}")
    print(f"LLM model: {manager.llm.model_name}")
    
    return response
```