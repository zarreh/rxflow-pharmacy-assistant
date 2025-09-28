# Escalation Scenarios Guide

## Overview

This guide documents the comprehensive escalation system implemented in the RxFlow Pharmacy Assistant. The system intelligently routes patients to appropriate medical professionals (doctors or pharmacists) when prescription refill requests cannot be processed automatically.

## Escalation Types

### 🔴 Doctor Escalation Scenarios

#### 1. No Refills Remaining
- **Trigger**: Patient requests refill for medication with `refills_remaining: 0`
- **System Response**: Recommends contacting doctor for prescription renewal
- **Test Medications**: `metformin`, `lisinopril`, `lorazepam`
- **Example Message**: "Since the prescription has expired, we may need to contact your doctor for a renewal."

#### 2. Controlled Substances
- **Trigger**: Medication marked as `controlled_substance: true`
- **System Response**: Requires doctor consultation regardless of refill status
- **Test Medications**: `lorazepam` (Schedule IV)
- **Example Message**: "Since lorazepam is a controlled substance, you'll need to reach out to your healthcare provider to discuss your need for a refill."

#### 3. Expired Prescriptions
- **Trigger**: Medication with `prescription_expired: true`
- **System Response**: Requires new prescription from doctor
- **Test Medications**: `lisinopril`
- **Example Message**: "Your prescription has expired and requires renewal by your doctor."

#### 4. Early Refill Requests (Future Enhancement)
- **Trigger**: Refill requested before allowable refill date
- **System Response**: Doctor approval required for early refills
- **Implementation**: Date-based logic comparing last fill date with refill eligibility

### 🔵 Pharmacist Consultation Scenarios

#### 1. Medication Not Found
- **Trigger**: Requested medication not in patient's medication history
- **System Response**: Pharmacist consultation to verify prescription details
- **Test Medications**: `hydrocodone`, `gabapentin` (any unlisted medication)
- **Example Message**: "This medication is not listed in your current medication history. Would you like to discuss this medication with your doctor to see if it can be prescribed?"

#### 2. Drug Interaction Checks (Future Enhancement)
- **Trigger**: New medication conflicts with existing prescriptions
- **System Response**: Pharmacist review required before dispensing

### ✅ Normal Processing (No Escalation)

#### Standard Refill Processing
- **Requirements**: 
  - Medication exists in patient history
  - `refills_remaining > 0`
  - Not a controlled substance
  - Prescription not expired
- **Test Medications**: `omeprazole` (5 refills), `meloxicam` (3 refills), `famotidine` (2 refills)

## Test Data Configuration

### Enhanced Mock Patient Data (Patient ID: 12345)

```python
# Medications with escalation scenarios
medications = [
    # Doctor Escalation - No Refills
    {
        'name': 'metformin',
        'refills_remaining': 0,  # Triggers doctor consultation
        'last_filled': '2023-12-10'
    },
    {
        'name': 'lisinopril', 
        'refills_remaining': 0,
        'prescription_expired': True,  # Double trigger
        'last_prescription_date': '2024-01-05'
    },
    
    # Doctor Escalation - Controlled Substance
    {
        'name': 'lorazepam',
        'refills_remaining': 0,
        'controlled_substance': True,
        'schedule': 'IV',
        'requires_doctor_consultation': True
    },
    
    # Normal Processing - Available Refills
    {
        'name': 'omeprazole',
        'refills_remaining': 5  # Can be refilled normally
    },
    {
        'name': 'meloxicam',
        'refills_remaining': 3  # Can be refilled normally  
    }
]
```

## Testing Framework

### Automated Test Scenarios

The system includes comprehensive test scenarios in `test_escalation_scenarios.py`:

1. **test_no_refills_scenario()** - Tests metformin (0 refills)
2. **test_controlled_substance_scenario()** - Tests lorazepam (Schedule IV)
3. **test_expired_prescription_scenario()** - Tests lisinopril (expired)
4. **test_medication_not_found_scenario()** - Tests hydrocodone (unlisted)
5. **test_early_refill_scenario()** - Tests premature refill requests

### Manual Testing Commands

```bash
# Test metformin (no refills)
python -c "
import asyncio
from rxflow.workflow.conversation_manager import ConversationManager
async def test():
    manager = ConversationManager()
    response = await manager.handle_message('I need a refill for my metformin', session_id='test_metformin')
    print(response.message)
asyncio.run(test())
"

# Test lorazepam (controlled substance)
python -c "
import asyncio
from rxflow.workflow.conversation_manager import ConversationManager
async def test():
    manager = ConversationManager()
    response = await manager.handle_message('I need to refill my lorazepam prescription', session_id='test_lorazepam')
    print(response.message)
asyncio.run(test())
"

# Test hydrocodone (not found)
python -c "
import asyncio
from rxflow.workflow.conversation_manager import ConversationManager
async def test():
    manager = ConversationManager()
    response = await manager.handle_message('I need to refill my hydrocodone', session_id='test_hydrocodone')
    print(response.message)
asyncio.run(test())
"
```

## Implementation Details

### Escalation Tool Architecture

The escalation system is implemented through:

1. **EscalationTool Class** (`rxflow/tools/escalation_tools.py`)
   - `check_escalation_needed()` - Core escalation logic
   - `_generate_escalation_response()` - Response generation
   - Integration with patient medication history

2. **Conversation Manager Integration** (`rxflow/workflow/conversation_manager.py`)
   - `escalation_check_tool` added to agent tools
   - Automatic escalation checking during conversation flow

3. **Enhanced Mock Data** (`rxflow/services/mock_data.py`)
   - Realistic escalation scenarios
   - Controlled substance markings
   - Expiration date tracking

### Success Indicators

When testing escalation scenarios, look for these response indicators:

#### Doctor Escalation Success:
- Contains keywords: "doctor", "prescription", "contact your doctor", "consultation"
- Explains specific reason (no refills, controlled substance, expired)
- Provides clear next steps

#### Pharmacist Consultation Success:
- Contains keywords: "pharmacist", "not found", "verify", "medication history"
- Lists available medications
- Suggests alternative actions

#### Normal Processing Success:
- Proceeds with refill process
- Checks pharmacy availability
- Provides pickup/delivery options

## Future Enhancements

### Planned Escalation Features

1. **Date-Based Early Refill Detection**
   - Calculate days since last fill
   - Apply insurance refill rules (typically 75-80% used)
   - Require doctor approval for early requests

2. **Drug Interaction Screening**
   - Cross-reference new medications with existing prescriptions
   - Flag potential interactions for pharmacist review
   - Integration with drug interaction databases

3. **Insurance Authorization Requirements**
   - Detect medications requiring prior authorization
   - Route to appropriate approval workflows
   - Track authorization status

4. **Quantity Limit Escalations**
   - Monitor unusual quantity requests
   - Flag requests exceeding normal limits
   - Require additional verification

## Monitoring and Analytics

### Escalation Metrics to Track

- **Escalation Rate**: Percentage of requests requiring escalation
- **Escalation Type Distribution**: Doctor vs. Pharmacist consultations
- **Resolution Time**: Time from escalation to resolution
- **Patient Satisfaction**: Feedback on escalation process

### Logging and Audit Trail

All escalation decisions are logged with:
- Patient ID and medication details
- Escalation reason and type
- Timestamp and session information
- Response generated and actions taken

This ensures compliance and enables continuous improvement of the escalation system.