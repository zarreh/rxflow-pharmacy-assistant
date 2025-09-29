# User Guide

## Getting Started

RxFlow Pharmacy Assistant is designed to streamline pharmacy operations and provide intelligent assistance for medication management. This guide will walk you through the main features and workflows.

## Overview

The RxFlow system provides:

- **AI-Powered Conversations**: Natural language interaction for pharmacy tasks
- **Patient Management**: Comprehensive medication history and safety checking
- **Pharmacy Operations**: Inventory management, pricing, and availability
- **Safety Systems**: Drug interaction checking, allergy verification, and clinical decision support
- **Workflow Automation**: Streamlined processes for common pharmacy tasks

## Main Features

### 1. Conversational Interface

#### Starting a Conversation

```python
from rxflow.workflow.conversation_manager import ConversationManager

# Initialize the conversation system
conversation = ConversationManager()

# Start with a simple greeting
response = conversation.process_message("Hello, I need help with a prescription refill")
print(response.message)
```

The system supports natural language queries like:
- "Can you help me refill my blood pressure medication?"
- "What's the cost of omeprazole at nearby pharmacies?"
- "Check if I have any drug allergies that would conflict with this prescription"
- "When did I last fill my diabetes medication?"

#### Conversation Types

**Simple Conversation**: Basic question-and-answer interactions
```python
from rxflow.workflow.simple_conversation import SimpleConversation

simple = SimpleConversation()
response = simple.process("What are the side effects of lisinopril?")
```

**Refill Conversation**: Specialized workflow for prescription refills
```python
from rxflow.workflow.refill_conversation import RefillConversation

refill = RefillConversation()
response = refill.process("I need to refill my omeprazole prescription")
```

### 2. Patient Management

#### Medication History Lookup

Access comprehensive patient medication records:

```python
from rxflow.tools.patient_history_tool import PatientHistoryTool

history_tool = PatientHistoryTool()

# Get patient's medication history
history = history_tool.get_medication_history("patient_id:lisinopril")

print(f"Patient has {history['total_medications']} medications on record")
for med in history['medications']:
    print(f"- {med['name']} ({med['strength']}) - Last filled: {med['last_filled']}")
```

#### Adherence Monitoring

Track and improve medication adherence:

```python
# Check adherence for a specific medication
adherence = history_tool.check_adherence("patient_id:metformin")

print(f"Adherence Score: {adherence['adherence_score']}%")
print(f"Level: {adherence['adherence_level']}")

if adherence['adherence_score'] < 80:
    print("Improvement recommendations:")
    for rec in adherence['recommendations']:
        print(f"- {rec}")
```

#### Allergy and Safety Checks

Verify patient safety before dispensing:

```python
# Check patient allergies
allergies = history_tool.get_allergies("patient_id")

if allergies['high_risk_allergies']:
    print("⚠️ HIGH RISK ALLERGIES DETECTED:")
    for allergy in allergies['high_risk_allergies']:
        print(f"- {allergy['allergen']}: {allergy['reaction']} ({allergy['severity']})")
```

### 3. Pharmacy Operations

#### Finding Nearby Pharmacies

Locate pharmacies and check services:

```python
from rxflow.tools.pharmacy_tools import PharmacyTool

pharmacy_tool = PharmacyTool()

# Find pharmacies by ZIP code
pharmacies = pharmacy_tool.find_nearby_pharmacies("90210")

for pharmacy in pharmacies['pharmacies'][:3]:  # Show top 3
    print(f"{pharmacy['name']}")
    print(f"  Address: {pharmacy['address']}")
    print(f"  Distance: {pharmacy['distance']} miles")
    print(f"  Rating: {pharmacy['rating']}/5")
    print(f"  Services: {', '.join(pharmacy['services'])}")
```

#### Medication Availability

Check stock levels and pickup times:

```python
# Check if medication is available
availability = pharmacy_tool.check_medication_availability({
    "pharmacy_id": "CVS001",
    "medication": "lisinopril 10mg", 
    "quantity": 90
})

if availability['in_stock']:
    print(f"✅ Available: {availability['available_quantity']} units")
    print(f"📅 Ready for pickup: {availability['pickup_time']}")
else:
    print(f"❌ Out of stock")
    if availability.get('expected_date'):
        print(f"📅 Expected: {availability['expected_date']}")
```

#### Price Comparison

Compare costs across pharmacies and insurance plans:

```python
# Compare prices across multiple pharmacies
price_comparison = pharmacy_tool.compare_prices({
    "medication": "omeprazole 20mg",
    "quantity": 30,
    "insurance": "Aetna PPO"
})

print("💰 Price Comparison:")
for price in sorted(price_comparison['prices'], key=lambda x: x['copay']):
    savings = f"(Save ${price_comparison['prices'][0]['copay'] - price['copay']:.2f})" if price['copay'] < price_comparison['prices'][0]['copay'] else ""
    print(f"  {price['pharmacy']}: ${price['copay']} {savings}")
```

### 4. Clinical Safety Features

#### Drug Interaction Checking

Verify safety of medication combinations:

```python
from rxflow.tools.rxnorm_tool import RxNormTool

rxnorm_tool = RxNormTool()

# Check for drug interactions
interactions = rxnorm_tool.check_drug_interactions([
    "lisinopril", "metformin", "omeprazole"
])

if interactions['high_severity']:
    print("⚠️ HIGH SEVERITY INTERACTIONS:")
    for interaction in interactions['high_severity']:
        print(f"- {interaction['drugs']}: {interaction['description']}")
```

#### Clinical Decision Support

Get evidence-based recommendations:

```python
# Get clinical information for a medication
clinical_info = rxnorm_tool.get_clinical_info("lisinopril")

print(f"Medication: {clinical_info['name']}")
print(f"Class: {clinical_info['therapeutic_class']}")
print(f"Indications: {', '.join(clinical_info['indications'])}")

if clinical_info['contraindications']:
    print("⚠️ Contraindications:")
    for contraindication in clinical_info['contraindications']:
        print(f"- {contraindication}")
```

### 5. Workflow Automation

#### Prescription Refill Workflow

Complete automated refill processing:

```python
def automated_refill_workflow(patient_id: str, medication_name: str):
    """Complete prescription refill with safety checks"""
    
    # Step 1: Verify patient medication history
    history = history_tool.get_medication_history(f"{patient_id}:{medication_name}")
    if not history.get('medications'):
        return {"error": "Medication not found in patient history"}
    
    # Step 2: Check medication adherence
    adherence = history_tool.check_adherence(f"{patient_id}:{medication_name}")
    if adherence['adherence_score'] < 50:
        return {
            "warning": "Poor adherence detected", 
            "recommendations": adherence['recommendations']
        }
    
    # Step 3: Verify no allergy conflicts
    allergies = history_tool.get_allergies(patient_id)
    for allergy in allergies.get('allergies', []):
        if medication_name.lower() in allergy['allergen'].lower():
            return {"error": f"Allergy conflict: {allergy['allergen']}"}
    
    # Step 4: Find available pharmacies
    patient_zip = "90210"  # Would get from patient record
    pharmacies = pharmacy_tool.find_nearby_pharmacies(patient_zip)
    
    # Step 5: Check availability and pricing
    best_option = None
    best_score = 0
    
    for pharmacy in pharmacies['pharmacies'][:3]:
        availability = pharmacy_tool.check_medication_availability({
            "pharmacy_id": pharmacy['id'],
            "medication": medication_name,
            "quantity": 90
        })
        
        if availability['in_stock']:
            pricing = pharmacy_tool.get_pricing({
                "pharmacy_id": pharmacy['id'],
                "medication": medication_name,
                "insurance": "patient_insurance_here"
            })
            
            # Calculate convenience score
            score = (5 - pharmacy['distance']) * 10 + (5 - pricing['copay']/10)
            
            if score > best_score:
                best_score = score
                best_option = {
                    "pharmacy": pharmacy,
                    "availability": availability,
                    "pricing": pricing
                }
    
    if not best_option:
        return {"error": "Medication not available at nearby pharmacies"}
    
    return {
        "success": True,
        "recommendation": best_option,
        "safety_verified": True,
        "ready_for_processing": True
    }

# Usage
result = automated_refill_workflow("12345", "lisinopril 10mg")
if result.get("success"):
    rec = result["recommendation"]
    print(f"✅ Refill approved at {rec['pharmacy']['name']}")
    print(f"💰 Cost: ${rec['pricing']['copay']}")
    print(f"📅 Ready: {rec['availability']['pickup_time']}")
```

#### Medication Synchronization

Coordinate multiple refills for patient convenience:

```python
def synchronize_medications(patient_id: str) -> dict:
    """Synchronize all patient medications to same refill date"""
    
    # Get all patient medications
    all_meds = history_tool.get_medication_history(f"{patient_id}:all")
    
    sync_plan = {
        "patient_id": patient_id,
        "medications": [],
        "target_sync_date": None,
        "estimated_savings": 0
    }
    
    # Analyze current refill patterns
    for med in all_meds['medications']:
        days_supply = med.get('days_supply', 30)
        last_filled = med.get('last_filled')
        
        # Calculate next refill date
        next_refill = calculate_next_refill_date(last_filled, days_supply)
        
        med_sync = {
            "medication": med['name'],
            "current_next_refill": next_refill,
            "days_supply": days_supply,
            "early_refill_needed": False,
            "cost_impact": 0
        }
        
        sync_plan["medications"].append(med_sync)
    
    # Find optimal sync date (most common refill date)
    refill_dates = [med["current_next_refill"] for med in sync_plan["medications"]]
    target_date = max(set(refill_dates), key=refill_dates.count)
    sync_plan["target_sync_date"] = target_date
    
    # Calculate adjustments needed
    for med_sync in sync_plan["medications"]:
        if med_sync["current_next_refill"] != target_date:
            med_sync["early_refill_needed"] = True
            # Calculate partial fill or early refill cost
    
    return sync_plan

# Usage
sync_plan = synchronize_medications("12345")
print(f"🔄 Medication Synchronization Plan")
print(f"Target Date: {sync_plan['target_sync_date']}")

early_refills = [med for med in sync_plan['medications'] if med['early_refill_needed']]
print(f"Medications needing adjustment: {len(early_refills)}")
```

## Best Practices

### 1. Safety First

Always perform safety checks before processing prescriptions:

```python
def safety_checklist(patient_id: str, medication: str) -> dict:
    """Comprehensive safety verification"""
    checks = {
        "allergy_check": False,
        "interaction_check": False,
        "adherence_check": False,
        "duplicate_therapy_check": False,
        "all_clear": False
    }
    
    # Check allergies
    allergies = history_tool.get_allergies(patient_id)
    checks["allergy_check"] = not any(
        medication.lower() in allergy['allergen'].lower() 
        for allergy in allergies.get('allergies', [])
    )
    
    # Check drug interactions with current medications
    current_meds = history_tool.get_medication_history(f"{patient_id}:all")
    medication_list = [med['name'] for med in current_meds.get('medications', [])]
    medication_list.append(medication)
    
    interactions = rxnorm_tool.check_drug_interactions(medication_list)
    checks["interaction_check"] = len(interactions.get('high_severity', [])) == 0
    
    # Check adherence history
    adherence = history_tool.check_adherence(f"{patient_id}:{medication}")
    checks["adherence_check"] = adherence.get('adherence_score', 0) > 60
    
    # All checks must pass
    checks["all_clear"] = all([
        checks["allergy_check"],
        checks["interaction_check"], 
        checks["adherence_check"]
    ])
    
    return checks
```

### 2. Error Handling

Implement robust error handling for all operations:

```python
from rxflow.tools.patient_history_tool import safe_medication_history
from rxflow.tools.pharmacy_tools import safe_pharmacy_lookup

def robust_medication_lookup(query: str) -> dict:
    """Medication lookup with comprehensive error handling"""
    try:
        result = safe_medication_history(query)
        
        if result.get("success"):
            return result
            
        # Try alternative approaches
        if "not found" in result.get("error", "").lower():
            # Try generic name lookup
            generic_result = safe_medication_history(f"{query}:generic")
            if generic_result.get("success"):
                return generic_result
        
        return {
            "success": False,
            "error": result.get("error", "Unknown error"),
            "suggestions": [
                "Verify medication spelling",
                "Try using generic name",
                "Check patient ID format"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"System error: {str(e)}",
            "contact_support": True
        }
```

### 3. Performance Optimization

Use efficient patterns for multiple lookups:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def parallel_pharmacy_check(medication: str, zip_code: str) -> dict:
    """Check multiple pharmacies simultaneously"""
    
    # Get list of pharmacies
    pharmacies_result = safe_pharmacy_lookup(zip_code)
    if not pharmacies_result.get("success"):
        return {"error": "No pharmacies found"}
    
    pharmacies = pharmacies_result["pharmacies"][:5]  # Top 5
    
    # Check availability at all pharmacies in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        
        for pharmacy in pharmacies:
            future = executor.submit(
                safe_medication_availability,
                {
                    "pharmacy_id": pharmacy["id"],
                    "medication": medication,
                    "quantity": 90
                }
            )
            futures.append((pharmacy, future))
        
        results = []
        for pharmacy, future in futures:
            try:
                availability = future.result(timeout=10)  # 10 second timeout
                results.append({
                    "pharmacy": pharmacy,
                    "availability": availability
                })
            except Exception as e:
                print(f"Error checking {pharmacy['name']}: {e}")
        
        return {"pharmacies": results}

# Usage
# results = asyncio.run(parallel_pharmacy_check("lisinopril 10mg", "90210"))
```

### 4. Logging and Monitoring

Implement comprehensive logging for audit trails:

```python
from rxflow.utils.logger import get_logger

logger = get_logger(__name__)

def log_medication_lookup(patient_id: str, medication: str, result: dict):
    """Log medication lookup for audit trail"""
    
    log_data = {
        "action": "medication_lookup",
        "patient_id": patient_id,
        "medication": medication,
        "success": result.get("success", False),
        "timestamp": "2025-01-15T12:00:00Z"
    }
    
    if result.get("success"):
        logger.info("Medication lookup successful", extra=log_data)
    else:
        log_data["error"] = result.get("error")
        logger.warning("Medication lookup failed", extra=log_data)

# Use in workflow
def logged_medication_history(patient_id: str, medication: str):
    """Get medication history with logging"""
    result = safe_medication_history(f"{patient_id}:{medication}")
    log_medication_lookup(patient_id, medication, result)
    return result
```

## Troubleshooting

### Common Issues

1. **"Medication not found"**
   - Verify spelling of medication name
   - Try using generic name instead of brand name
   - Check if patient ID is correct format

2. **"No pharmacies found"**
   - Verify ZIP code format (5 digits)
   - Expand search radius
   - Check if area is served by supported pharmacy chains

3. **"API timeout"**
   - Implement retry logic with exponential backoff
   - Check network connectivity
   - Verify API credentials and rate limits

4. **"Insurance not accepted"**
   - Verify insurance plan name spelling
   - Check if pharmacy participates in plan
   - Look for alternative pharmacies

### Getting Help

If you encounter issues:

1. Check the logs for detailed error messages
2. Verify your configuration in `rxflow/config/settings.py`
3. Test individual components using the safety wrapper functions
4. Review the API documentation for parameter formats
5. Contact support with specific error messages and steps to reproduce

For more detailed technical information, see the [API Reference](../api/) section.