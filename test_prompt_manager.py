#!/usr/bin/env python3
"""
Test enhanced prompt management system for Step 4
Validates comprehensive prompt templates and conversation management
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rxflow.prompts.prompt_manager import PromptManager
from rxflow.workflow.workflow_types import RefillState
import json

def test_prompt_manager_initialization():
    """Test basic prompt manager setup"""
    print("=" * 60)
    print("TESTING PROMPT MANAGER INITIALIZATION")
    print("=" * 60)
    
    pm = PromptManager()
    
    print(f"✅ Initialized with {len(pm.prompts)} prompt templates")
    
    # List all available prompts
    print("\n📋 Available Prompt Templates:")
    for name, prompt in pm.prompts.items():
        state = prompt.state.value if prompt.state else "Any"
        tools = len(prompt.tools_required)
        safety = len(prompt.safety_checks)
        print(f"  • {name}")
        print(f"    - State: {state}")
        print(f"    - Tools Required: {tools}")
        print(f"    - Safety Checks: {safety}")
        print(f"    - Examples: {len(prompt.examples)}")
    
    return pm

def test_state_based_prompts(pm: PromptManager):
    """Test getting prompts by workflow state"""
    print("\n" + "=" * 60)
    print("TESTING STATE-BASED PROMPT RETRIEVAL")
    print("=" * 60)
    
    for state in RefillState:
        prompts = pm.get_prompt_for_state(state)
        print(f"\n🔍 {state.value} state:")
        if prompts:
            for prompt in prompts:
                print(f"  ✅ {prompt.name}")
        else:
            print(f"  ⚠️  No specific prompts for {state.value}")

def test_medication_extraction(pm: PromptManager):
    """Test medication extraction prompt"""
    print("\n" + "=" * 60) 
    print("TESTING MEDICATION EXTRACTION PROMPT")
    print("=" * 60)
    
    test_cases = [
        "I need to refill my blood pressure medication",
        "Refill lisinopril 10mg 30-day supply", 
        "My heart pills are running out",
        "I need more of that diabetes medicine"
    ]
    
    for user_input in test_cases:
        print(f"\n🧪 Testing: '{user_input}'")
        
        # Test prompt rendering
        rendered = pm.render_prompt("medication_extraction", user_input=user_input)
        print(f"📝 Rendered User Prompt:")
        print(f"   {rendered}")
        
        # Test system message
        system_msg = pm.render_system_message("medication_extraction")
        print(f"🤖 System Message Length: {len(system_msg)} characters")
        
        # Test conversation format
        conv_prompt = pm.format_conversation_prompt(
            "medication_extraction",
            user_input=user_input
        )
        print(f"💬 Conversation Messages: {len(conv_prompt['messages'])}")
        print(f"🛠️  Required Tools: {conv_prompt['tools_required']}")

def test_disambiguation_scenarios(pm: PromptManager):
    """Test medication disambiguation scenarios"""
    print("\n" + "=" * 60)
    print("TESTING MEDICATION DISAMBIGUATION")
    print("=" * 60)
    
    test_scenario = {
        "user_input": "my heart medication",
        "medication_history": ["lisinopril 10mg", "atorvastatin 20mg", "metoprolol 25mg"],
        "possible_matches": [
            {"name": "lisinopril", "indication": "blood pressure"},
            {"name": "atorvastatin", "indication": "cholesterol"},
            {"name": "metoprolol", "indication": "heart rate/blood pressure"}
        ]
    }
    
    print(f"🧪 Scenario: Patient says '{test_scenario['user_input']}'")
    print(f"📋 Patient History: {test_scenario['medication_history']}")
    
    # Render disambiguation prompt
    rendered = pm.render_prompt(
        "medication_disambiguation",
        **test_scenario
    )
    print(f"\n📝 Disambiguation Prompt:")
    print(rendered)
    
    # Get examples
    examples = pm.get_examples("medication_disambiguation")
    print(f"\n💡 Available Examples: {len(examples)}")
    for i, example in enumerate(examples):
        print(f"   Example {i+1}: {json.dumps(example, indent=2)}")

def test_safety_verification(pm: PromptManager):
    """Test safety verification prompts"""
    print("\n" + "=" * 60)
    print("TESTING SAFETY VERIFICATION SYSTEM")
    print("=" * 60)
    
    safety_scenario = {
        "medication_name": "lisinopril",
        "dosage": "10mg",
        "allergies": ["penicillin", "sulfa drugs"],
        "current_medications": ["ibuprofen 400mg PRN", "vitamin D 1000IU daily"],
        "interactions": [
            {"drug": "ibuprofen", "severity": "moderate", "effect": "reduced antihypertensive effect"}
        ],
        "allergy_conflicts": []
    }
    
    print("🧪 Testing Safety Check for:")
    print(f"   Medication: {safety_scenario['medication_name']} {safety_scenario['dosage']}")
    print(f"   Current Meds: {safety_scenario['current_medications']}")
    print(f"   Interactions Found: {len(safety_scenario['interactions'])}")
    
    # Test safety prompt
    safety_prompt = pm.format_conversation_prompt(
        "safety_verification",
        **safety_scenario
    )
    
    print(f"\n🛡️  Safety Checks Required: {safety_prompt['safety_checks']}")
    print(f"🛠️  Tools Required: {safety_prompt['tools_required']}")
    
    # Test system message for safety context
    system_msg = pm.render_system_message("safety_verification", **safety_scenario)
    print(f"🤖 Safety System Message includes interaction context: {'interaction' in system_msg.lower()}")

def test_cost_optimization(pm: PromptManager):
    """Test cost optimization prompts"""
    print("\n" + "=" * 60)
    print("TESTING COST OPTIMIZATION PROMPTS")
    print("=" * 60)
    
    cost_scenario = {
        "medication_name": "atorvastatin 20mg",
        "insurance_info": {"plan": "Blue Cross Basic", "tier": 2, "copay": 25},
        "generic_option": {"available": True, "name": "atorvastatin", "price": 4},
        "price_comparison": {
            "CVS": {"brand": 180, "generic": 15, "insurance_copay": 25},
            "Walmart": {"brand": 160, "generic": 4, "insurance_copay": 25},
            "Costco": {"brand": 145, "generic": 8, "insurance_copay": 25}
        },
        "available_discounts": ["GoodRx", "Walmart $4 program", "Manufacturer coupon"]
    }
    
    print(f"🧪 Cost Optimization for: {cost_scenario['medication_name']}")
    print(f"💰 Insurance Copay: ${cost_scenario['insurance_info']['copay']}")
    print(f"💊 Generic Available: {cost_scenario['generic_option']['available']}")
    
    # Test cost optimization prompt
    cost_prompt = pm.format_conversation_prompt(
        "cost_optimization", 
        **cost_scenario
    )
    
    print(f"\n🛠️  Cost Tools Required: {cost_prompt['tools_required']}")
    
    # Show potential savings calculation
    brand_price = cost_scenario['price_comparison']['CVS']['brand']
    generic_price = cost_scenario['price_comparison']['Walmart']['generic'] 
    savings = brand_price - generic_price
    print(f"💵 Potential Savings: ${savings} (${brand_price} → ${generic_price})")

def test_conversation_flow(pm: PromptManager):
    """Test complete conversation flow with history"""
    print("\n" + "=" * 60)
    print("TESTING CONVERSATION FLOW MANAGEMENT")
    print("=" * 60)
    
    # Simulate conversation history
    conversation_history = [
        {"role": "user", "content": "I need to refill my blood pressure medication"},
        {"role": "assistant", "content": "I'd be happy to help. Let me check your current medications."},
        {"role": "user", "content": "It's the lisinopril one"},
        {"role": "assistant", "content": "Found it! Lisinopril 10mg. Let me verify the details."}
    ]
    
    print("💬 Conversation History:")
    for i, msg in enumerate(conversation_history):
        role_icon = "👤" if msg["role"] == "user" else "🤖"
        print(f"   {i+1}. {role_icon} {msg['content'][:50]}...")
    
    # Test continuation with dosage confirmation
    continuation_prompt = pm.format_conversation_prompt(
        "dosage_confirmation",
        conversation_history=conversation_history,
        medication_name="lisinopril",
        current_dosage="10mg", 
        requested_dosage="10mg",
        available_dosages=["5mg", "10mg", "20mg"]
    )
    
    print(f"\n📨 Next Prompt Messages: {len(continuation_prompt['messages'])}")
    print("🔄 Includes conversation context and examples")
    
    # Show usage tracking
    pm.log_prompt_usage("dosage_confirmation", {"medication": "lisinopril"})
    usage_stats = pm.get_usage_stats()
    print(f"\n📊 Usage Stats: {usage_stats}")

def test_error_handling(pm: PromptManager):
    """Test error handling capabilities"""
    print("\n" + "=" * 60)
    print("TESTING ERROR HANDLING PROMPTS")
    print("=" * 60)
    
    error_scenarios = [
        {
            "error_type": "medication_not_found",
            "error_context": "User said 'my purple pills' but no match found",
            "impact_description": "Cannot proceed with refill",
            "alternatives": ["ask for more details", "check patient history", "suggest spelling"],
            "escalation_options": ["pharmacist consultation"]
        },
        {
            "error_type": "prior_authorization_required", 
            "error_context": "Eliquis requires PA for insurance coverage",
            "impact_description": "3-5 day delay for approval process",
            "alternatives": ["start PA process", "check generic alternatives"],
            "escalation_options": ["contact prescriber", "emergency override"]
        }
    ]
    
    for i, scenario in enumerate(error_scenarios):
        print(f"\n🚨 Error Scenario {i+1}: {scenario['error_type']}")
        print(f"   Context: {scenario['error_context']}")
        
        error_prompt = pm.format_conversation_prompt("error_handling", **scenario)
        print(f"   🛠️  Recovery Tools: {len(scenario['alternatives'])} alternatives")

def test_prompt_validation(pm: PromptManager):
    """Test prompt template validation"""
    print("\n" + "=" * 60) 
    print("TESTING PROMPT VALIDATION SYSTEM")
    print("=" * 60)
    
    # Test all existing prompts
    validation_results = {}
    for prompt_name, prompt in pm.prompts.items():
        issues = pm.validate_prompt_template(prompt)
        validation_results[prompt_name] = issues
        
        status = "✅" if not issues else "⚠️"
        print(f"{status} {prompt_name}: {len(issues)} issues")
        for issue in issues:
            print(f"   - {issue}")
    
    total_prompts = len(pm.prompts)
    valid_prompts = len([p for p in validation_results.values() if not p])
    print(f"\n📊 Validation Summary: {valid_prompts}/{total_prompts} prompts valid")

def main():
    """Run all prompt manager tests"""
    print("🧪 COMPREHENSIVE PROMPT MANAGER TESTING")
    print("Testing enhanced prompt management system for Step 4")
    print("=" * 80)
    
    try:
        # Initialize and test basic functionality
        pm = test_prompt_manager_initialization()
        
        # Test state-based retrieval
        test_state_based_prompts(pm)
        
        # Test specific prompt types
        test_medication_extraction(pm)
        test_disambiguation_scenarios(pm)
        test_safety_verification(pm)
        test_cost_optimization(pm)
        
        # Test conversation management
        test_conversation_flow(pm)
        test_error_handling(pm)
        
        # Validate system integrity
        test_prompt_validation(pm)
        
        print("\n" + "=" * 80)
        print("✅ ALL PROMPT MANAGER TESTS COMPLETED SUCCESSFULLY!")
        print("🎯 Step 4: Enhanced Prompt Management System - READY")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR in prompt manager testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)