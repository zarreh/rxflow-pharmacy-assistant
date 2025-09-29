# Patient Tools API

The Patient Tools module provides comprehensive patient data management, medication history tracking, and safety validation capabilities.

## PatientHistoryTool

The `PatientHistoryTool` class provides comprehensive patient data management, medication history tracking, and safety validation capabilities.

```python
# Note: Full API documentation will be auto-generated when the module is available
# ::: rxflow.tools.patient_history_tool.PatientHistoryTool
```

## Safety Wrapper Functions

### Medication History Lookup

Safe wrapper function for medication history retrieval with comprehensive error handling.

```python
# ::: rxflow.tools.patient_history_tool.safe_medication_history
```

### Adherence Analysis  

Safe wrapper for medication adherence checking and analysis.

```python
# ::: rxflow.tools.patient_history_tool.safe_adherence_check
```

### Allergy Verification

Safe wrapper for patient allergy verification and conflict detection.

```python
# ::: rxflow.tools.patient_history_tool.safe_allergy_check
```

## Usage Examples

### Basic Medication History

```python
from rxflow.tools.patient_history_tool import PatientHistoryTool

# Initialize the tool
history_tool = PatientHistoryTool()

# Get patient medication history
history = history_tool.get_medication_history("omeprazole")

print(f"Found {history['total_medications']} medications")
for med in history['medications']:
    print(f"- {med['name']} ({med['strength']}) for {med['condition']}")
```

### Adherence Monitoring

```python
# Check medication adherence
adherence = history_tool.check_adherence("12345:lisinopril")

print(f"Adherence Score: {adherence['adherence_score']:.1f}%")
print(f"Level: {adherence['adherence_level']}")

if adherence['adherence_score'] < 80:
    print("Recommendations:")
    for rec in adherence['recommendations']:
        print(f"- {rec}")
```

### Safety Verification

```python
# Check patient allergies
allergies = history_tool.get_allergies("12345")

print(f"Patient has {allergies['allergy_count']} documented allergies")

# Check for high-risk allergies
if allergies['high_risk_allergies']:
    print("⚠️ HIGH RISK ALLERGIES:")
    for allergy in allergies['high_risk_allergies']:
        print(f"- {allergy}")
```

### Using Safety Wrappers

```python
from rxflow.tools.patient_history_tool import (
    safe_medication_history,
    safe_adherence_check, 
    safe_allergy_check
)

# Safe medication lookup with error handling
result = safe_medication_history("omeprazole")
if result.get("success"):
    medications = result["medications"]
else:
    print(f"Error: {result.get('error')}")

# Safe adherence check
adherence_result = safe_adherence_check({
    "patient_id": "12345",
    "medication": "lisinopril"
})

# Safe allergy verification
allergy_result = safe_allergy_check("12345")
```

## Clinical Applications

### Prescription Refill Workflow

```python
def prescription_refill_workflow(patient_id: str, medication_name: str):
    """Complete prescription refill safety workflow"""
    history_tool = PatientHistoryTool()
    
    # Step 1: Verify medication in history
    history = safe_medication_history(f"{patient_id}:{medication_name}")
    if not history.get("success"):
        return {"error": "Medication not found in patient history"}
    
    # Step 2: Check adherence patterns
    adherence = safe_adherence_check(f"{patient_id}:{medication_name}")
    if adherence["adherence_score"] < 50:
        return {"warning": "Poor adherence detected", "adherence": adherence}
    
    # Step 3: Verify no allergy conflicts
    allergies = safe_allergy_check(patient_id)
    medication_conflicts = []
    
    for allergy in allergies.get("allergies", []):
        if medication_name.lower() in allergy["allergen"].lower():
            medication_conflicts.append(allergy)
    
    if medication_conflicts:
        return {"error": "Allergy conflict detected", "conflicts": medication_conflicts}
    
    # All checks passed
    return {
        "success": True,
        "medication": history["medications"][0],
        "adherence": adherence,
        "safe_to_proceed": True
    }

# Usage
result = prescription_refill_workflow("12345", "omeprazole")
if result.get("success"):
    print("✅ Safe to proceed with refill")
else:
    print(f"⚠️ Issue detected: {result.get('error', result.get('warning'))}")
```

### Adherence Improvement Program

```python
def generate_adherence_report(patient_id: str) -> dict:
    """Generate comprehensive adherence report for patient"""
    history_tool = PatientHistoryTool()
    
    # Get all patient medications
    all_meds = safe_medication_history(f"{patient_id}:all")
    
    adherence_report = {
        "patient_id": patient_id,
        "medications": [],
        "overall_score": 0,
        "recommendations": []
    }
    
    total_score = 0
    medication_count = 0
    
    for med in all_meds.get("medications", []):
        adherence = safe_adherence_check(f"{patient_id}:{med['name']}")
        
        med_report = {
            "medication": med["name"],
            "condition": med["condition"],
            "adherence_score": adherence["adherence_score"],
            "level": adherence["adherence_level"],
            "recommendations": adherence.get("recommendations", [])
        }
        
        adherence_report["medications"].append(med_report)
        total_score += adherence["adherence_score"]
        medication_count += 1
    
    # Calculate overall score
    adherence_report["overall_score"] = total_score / medication_count if medication_count > 0 else 0
    
    # Generate global recommendations
    if adherence_report["overall_score"] < 70:
        adherence_report["recommendations"].extend([
            "Consider medication synchronization program",
            "Set up automatic refill reminders",
            "Schedule medication therapy management consultation"
        ])
    
    return adherence_report

# Generate report
report = generate_adherence_report("12345")
print(f"Overall Adherence: {report['overall_score']:.1f}%")
```

## Data Models

### Medication Record Structure

```python
medication_record = {
    "name": "omeprazole",
    "generic_name": "omeprazole", 
    "brand_names": ["Prilosec", "Losec"],
    "strength": "20mg",
    "condition": "GERD",
    "prescriber": "Dr. Smith",
    "last_filled": "2025-09-15",
    "days_supply": 90,
    "quantity": 90,
    "status": "active",
    "refills_remaining": 2
}
```

### Adherence Analysis Structure

```python
adherence_analysis = {
    "patient_id": "12345",
    "medication": "lisinopril", 
    "adherence_score": 87.5,
    "adherence_level": "Good",
    "days_since_last_fill": 28,
    "refill_pattern": "Consistent",
    "recommendations": [
        "Continue current adherence pattern",
        "Set reminder for next refill in 62 days"
    ],
    "risk_factors": []
}
```

### Allergy Profile Structure

```python
allergy_profile = {
    "patient_id": "12345",
    "allergies": [
        {
            "allergen": "penicillin",
            "reaction": "rash", 
            "severity": "Moderate",
            "date_reported": "2023-03-15",
            "verified": True
        }
    ],
    "allergy_count": 1,
    "high_risk_allergies": [],
    "contraindications": ["amoxicillin", "ampicillin"]
}
```

## Integration Patterns

### LangChain Tool Integration

```python
from langchain.tools import Tool
from rxflow.tools.patient_history_tool import safe_medication_history

# Create LangChain tool wrapper
patient_history_tool = Tool(
    name="patient_medication_history",
    description="Retrieve patient medication history and details",
    func=safe_medication_history
)

# Use in LangChain agent
from langchain.agents import create_openai_tools_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
tools = [patient_history_tool]

agent = create_openai_tools_agent(llm, tools, prompt_template)
```

### Error Handling Patterns

```python
def robust_patient_lookup(query: str) -> dict:
    """Robust patient data lookup with comprehensive error handling"""
    try:
        # Primary lookup
        result = safe_medication_history(query)
        
        if result.get("success"):
            return result
        
        # Fallback strategies
        if "not found" in result.get("error", "").lower():
            # Try alternative spellings or generic names
            alternative_queries = generate_alternative_queries(query)
            for alt_query in alternative_queries:
                alt_result = safe_medication_history(alt_query)
                if alt_result.get("success"):
                    return alt_result
        
        # Final fallback - return informative error
        return {
            "success": False,
            "error": "Medication not found in patient history",
            "suggestions": [
                "Check spelling of medication name",
                "Try using generic name instead of brand name",
                "Verify patient ID is correct"
            ]
        }
        
    except Exception as e:
        return {
            "success": False, 
            "error": f"System error: {str(e)}",
            "contact_support": True
        }
```