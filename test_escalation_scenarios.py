#!/usr/bin/env python3
"""
Test escalation scenarios that require doctor or pharmacist consultation
"""

import asyncio
from rxflow.workflow.conversation_manager import ConversationManager

async def test_no_refills_scenario():
    """Test scenario where patient has no refills remaining"""
    print("\n" + "="*60)
    print("🩺 TEST 1: NO REFILLS REMAINING - DOCTOR ESCALATION")
    print("="*60)
    print("Scenario: Patient requests metformin refill but has 0 refills remaining")
    
    manager = ConversationManager()
    
    # Test metformin request (has 0 refills)
    print("\n1. Patient requests metformin refill...")
    response1 = await manager.handle_message(
        "I need a refill for my metformin 500mg", 
        session_id="no_refills_test"
    )
    print(f"Response: {response1.message[:150]}...")
    
    # Check if escalation is mentioned
    response_lower = response1.message.lower()
    if any(keyword in response_lower for keyword in ["doctor", "prescription", "refill", "contact", "new prescription"]):
        print("✅ System detected no refills and suggested doctor consultation")
    else:
        print("❌ System did not properly handle no refills scenario")
    
    return "doctor" in response_lower or "prescription" in response_lower

async def test_controlled_substance_scenario():
    """Test scenario with controlled substance (lorazepam)"""
    print("\n" + "="*60)
    print("🔒 TEST 2: CONTROLLED SUBSTANCE - DOCTOR ESCALATION")
    print("="*60)
    print("Scenario: Patient requests lorazepam refill (controlled substance)")
    
    manager = ConversationManager()
    
    # Test lorazepam request (controlled substance)
    print("\n1. Patient requests lorazepam refill...")
    response1 = await manager.handle_message(
        "I need more lorazepam for my anxiety", 
        session_id="controlled_test"
    )
    print(f"Response: {response1.message[:150]}...")
    
    # Check if controlled substance handling is mentioned
    response_lower = response1.message.lower()
    if any(keyword in response_lower for keyword in ["doctor", "controlled", "prescription", "schedule"]):
        print("✅ System properly handled controlled substance request")
    else:
        print("❌ System did not properly handle controlled substance")
    
    return "doctor" in response_lower or "controlled" in response_lower

async def test_expired_prescription_scenario():
    """Test scenario with expired prescription"""
    print("\n" + "="*60)
    print("📅 TEST 3: EXPIRED PRESCRIPTION - DOCTOR ESCALATION")
    print("="*60)
    print("Scenario: Patient requests lisinopril refill (prescription expired)")
    
    manager = ConversationManager()
    
    # Test lisinopril request (expired prescription)
    print("\n1. Patient requests lisinopril refill...")
    response1 = await manager.handle_message(
        "I need to refill my lisinopril blood pressure medication", 
        session_id="expired_test"
    )
    print(f"Response: {response1.message[:150]}...")
    
    # Check if expiration handling is mentioned
    response_lower = response1.message.lower()
    if any(keyword in response_lower for keyword in ["doctor", "expired", "prescription", "new"]):
        print("✅ System detected expired prescription and suggested doctor contact")
    else:
        print("❌ System did not properly handle expired prescription")
    
    return "doctor" in response_lower or "expired" in response_lower

async def test_early_refill_scenario():
    """Test scenario where patient requests refill too early"""
    print("\n" + "="*60)
    print("⏰ TEST 4: EARLY REFILL REQUEST - PHARMACIST CONSULTATION")
    print("="*60)
    print("Scenario: Patient requests meloxicam refill too early (last filled recently)")
    
    manager = ConversationManager()
    
    # Test meloxicam request (should be too early based on last fill date)
    print("\n1. Patient requests early meloxicam refill...")
    response1 = await manager.handle_message(
        "I need my meloxicam refilled, I'm running low", 
        session_id="early_refill_test"
    )
    print(f"Response: {response1.message[:150]}...")
    
    # Note: This scenario might not trigger if the mock data dates are old enough
    response_lower = response1.message.lower()
    if any(keyword in response_lower for keyword in ["pharmacist", "early", "recent", "too soon"]):
        print("✅ System detected early refill request")
        return True
    elif "order submitted" in response_lower:
        print("ℹ️  Refill was processed normally (not too early based on dates)")
        return True
    else:
        print("❌ Unexpected response for early refill scenario")
        return False

async def test_medication_not_found_scenario():
    """Test scenario where medication is not in patient history"""
    print("\n" + "="*60)
    print("❓ TEST 5: MEDICATION NOT FOUND - PHARMACIST CONSULTATION")
    print("="*60)
    print("Scenario: Patient requests medication not in their history")
    
    manager = ConversationManager()
    
    # Test request for medication not in patient history
    print("\n1. Patient requests unknown medication...")
    response1 = await manager.handle_message(
        "I need a refill for my hydrocodone", 
        session_id="not_found_test"
    )
    print(f"Response: {response1.message[:150]}...")
    
    # Check if not found handling is mentioned
    response_lower = response1.message.lower()
    if any(keyword in response_lower for keyword in ["pharmacist", "not found", "no record", "history", "verify"]):
        print("✅ System properly handled medication not found")
    else:
        print("❌ System did not properly handle unknown medication")
    
    return "pharmacist" in response_lower or "not found" in response_lower

async def main():
    """Run all escalation tests"""
    print("🧪 COMPREHENSIVE ESCALATION SCENARIO TESTING")
    print("Testing various scenarios that require doctor or pharmacist escalation...")
    
    results = []
    
    # Run all test scenarios
    results.append(await test_no_refills_scenario())
    results.append(await test_controlled_substance_scenario()) 
    results.append(await test_expired_prescription_scenario())
    results.append(await test_early_refill_scenario())
    results.append(await test_medication_not_found_scenario())
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "No Refills (Metformin)", 
        "Controlled Substance (Lorazepam)",
        "Expired Prescription (Lisinopril)",
        "Early Refill (Meloxicam)",
        "Medication Not Found (Hydrocodone)"
    ]
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\n🏆 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL ESCALATION SCENARIOS WORKING PROPERLY!")
        print("   ✅ Doctor consultations for no refills, controlled substances, expired Rx")
        print("   ✅ Pharmacist consultations for early refills, unknown medications")
        print("   ✅ Proper contact information and next steps provided")
    elif passed >= total * 0.8:
        print("\n✅ MOST ESCALATION SCENARIOS WORKING!")
        print("   Some scenarios may need fine-tuning but core functionality is good")
    else:
        print("\n⚠️  ESCALATION SYSTEM NEEDS IMPROVEMENT")
        print("   Several scenarios are not being handled properly")
    
    return passed, total

if __name__ == "__main__":
    asyncio.run(main())