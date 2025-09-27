#!/usr/bin/env python3
"""
Comprehensive integration tests for Step 3: Core Tools Implementation
Tests all tools with enhanced mock data and validates complete workflow scenarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rxflow.tools import (
    # Patient history tools
    patient_history_tool, adherence_tool, allergy_tool,
    # RxNorm tools  
    rxnorm_tool, dosage_verification_tool, interaction_tool,
    # Pharmacy tools
    pharmacy_location_tool, pharmacy_inventory_tool, pharmacy_wait_times_tool, pharmacy_details_tool,
    # Cost tools
    goodrx_tool, brand_generic_tool, insurance_tool, prior_auth_tool,
    # Order tools
    order_submission_tool, order_tracking_tool, order_cancellation_tool
)

def test_patient_history_tools():
    """Test patient history and adherence tools"""
    print("🧪 Testing Patient History Tools...")
    
    # Test patient history
    history_result = patient_history_tool.func("lisinopril")
    assert history_result["success"], f"Patient history failed: {history_result.get('error')}"
    assert len(history_result["medications"]) > 0, "No medications found in history"
    print(f"✅ Patient history: Found {len(history_result['medications'])} medications")
    
    # Test adherence checking
    adherence_result = adherence_tool.func("lisinopril")
    assert adherence_result["success"], f"Adherence check failed: {adherence_result.get('error')}"
    assert "adherence_rate" in adherence_result, "Adherence rate not returned"
    print(f"✅ Adherence check: {adherence_result['adherence_rate']} rate ({adherence_result['adherence_status']})")
    
    # Test allergy checking
    allergy_result = allergy_tool.func("12345")
    assert allergy_result["success"], f"Allergy check failed: {allergy_result.get('error')}"
    print(f"✅ Allergy check: {len(allergy_result['allergies'])} allergies found")

def test_rxnorm_tools():
    """Test RxNorm medication lookup and verification tools"""
    print("\n🧪 Testing RxNorm Tools...")
    
    # Test medication lookup
    rxnorm_result = rxnorm_tool.func("lisinopril")
    assert rxnorm_result["success"], f"RxNorm lookup failed: {rxnorm_result.get('error')}"
    assert len(rxnorm_result["medications"]) > 0, "No medications found in RxNorm"
    medication = rxnorm_result["medications"][0]
    assert "rxcui" in medication, "RxCUI not returned"
    print(f"✅ RxNorm lookup: Found {medication['name']} (RxCUI: {medication['rxcui']})")
    
    # Test dosage verification
    dosage_result = dosage_verification_tool.func("lisinopril:10mg")
    assert dosage_result["success"], f"Dosage verification failed: {dosage_result.get('error')}"
    print(f"✅ Dosage verification: 10mg is {'valid' if dosage_result['is_valid_dosage'] else 'invalid'}")
    
    # Test interaction checking
    interaction_result = interaction_tool.func("lisinopril")
    assert interaction_result["success"], f"Interaction check failed: {interaction_result.get('error')}"
    interaction_count = interaction_result["interaction_summary"]["total_count"]
    print(f"✅ Interaction check: {interaction_count} interactions found")
    if interaction_count > 0:
        print(f"   Highest severity: {interaction_result['highest_severity']}")

def test_pharmacy_tools():
    """Test pharmacy location, inventory, and service tools"""
    print("\n🧪 Testing Pharmacy Tools...")
    
    # Test pharmacy location finder
    location_result = pharmacy_location_tool.func("default")
    assert location_result["success"], f"Pharmacy location failed: {location_result.get('error')}"
    assert location_result["count"] > 0, "No pharmacies found"
    print(f"✅ Pharmacy locations: Found {location_result['count']} pharmacies")
    
    # Test inventory checking
    inventory_result = pharmacy_inventory_tool.func("lisinopril")
    assert inventory_result["success"], f"Inventory check failed: {inventory_result.get('error')}"
    pharmacies_with_stock = inventory_result["pharmacies_with_stock"]
    print(f"✅ Inventory check: {pharmacies_with_stock} pharmacies have lisinopril in stock")
    
    # Test wait times
    wait_result = pharmacy_wait_times_tool.func("all")
    assert wait_result["success"], f"Wait times failed: {wait_result.get('error')}"
    fastest = wait_result["fastest_pharmacy"]
    print(f"✅ Wait times: Fastest is {fastest['pharmacy_name']} ({fastest['wait_time_min']} min)")
    
    # Test pharmacy details
    details_result = pharmacy_details_tool.func("cvs_main")
    assert details_result["success"], f"Pharmacy details failed: {details_result.get('error')}"
    pharmacy = details_result["pharmacy"]
    print(f"✅ Pharmacy details: {pharmacy['name']} - {pharmacy['phone']}")

def test_cost_tools():
    """Test cost comparison and insurance tools"""
    print("\n🧪 Testing Cost Tools...")
    
    # Test GoodRx pricing
    goodrx_result = goodrx_tool.func("lisinopril:10mg:30")
    assert goodrx_result["success"], f"GoodRx pricing failed: {goodrx_result.get('error')}"
    pharmacy_count = len(goodrx_result["pharmacy_prices"])
    lowest_price = goodrx_result["summary"]["lowest_cash_price"]
    print(f"✅ GoodRx pricing: {pharmacy_count} pharmacies, lowest price: ${lowest_price}")
    
    # Test brand vs generic comparison
    brand_result = brand_generic_tool.func("atorvastatin")
    assert brand_result["success"], f"Brand comparison failed: {brand_result.get('error')}"
    savings = brand_result["savings_with_generic"]
    print(f"✅ Brand vs generic: Save ${savings} with generic ({brand_result['percent_savings']}%)")
    
    # Test insurance coverage
    insurance_result = insurance_tool.func("lisinopril:BlueCross Shield")
    assert insurance_result["success"], f"Insurance check failed: {insurance_result.get('error')}"
    tier = insurance_result["tier"]
    copay = insurance_result["copay"]
    print(f"✅ Insurance coverage: Tier {tier}, ${copay} copay")
    
    # Test prior authorization lookup
    pa_result = prior_auth_tool.func("eliquis")
    assert pa_result["success"], f"PA lookup failed: {pa_result.get('error')}"
    pa_required = pa_result["prior_authorization_required"]
    print(f"✅ Prior authorization: {'Required' if pa_required else 'Not required'} for Eliquis")

def test_order_tools():
    """Test order submission, tracking, and cancellation"""
    print("\n🧪 Testing Order Tools...")
    
    # Test order submission
    order_result = order_submission_tool.func("lisinopril:10mg:30:walmart_plaza:12345")
    assert order_result["success"], f"Order submission failed: {order_result.get('error')}"
    order_id = order_result["order_id"]
    pharmacy_name = order_result["pharmacy_details"]["name"]
    pickup_time = order_result["pickup_details"]["estimated_time"]
    print(f"✅ Order submission: Order {order_id} at {pharmacy_name}, pickup at {pickup_time}")
    
    # Test order tracking
    track_result = order_tracking_tool.func(order_id)
    assert track_result["success"], f"Order tracking failed: {track_result.get('error')}"
    status = track_result["status"]
    print(f"✅ Order tracking: Order {order_id} status is '{status}'")
    
    # Test order cancellation
    cancel_result = order_cancellation_tool.func(order_id)
    assert cancel_result["success"], f"Order cancellation failed: {cancel_result.get('error')}"
    print(f"✅ Order cancellation: Order {order_id} cancelled successfully")

def test_workflow_scenarios():
    """Test complete workflow scenarios"""
    print("\n🧪 Testing Complete Workflow Scenarios...")
    
    # Scenario 1: Happy path refill
    print("Scenario 1: Happy Path Refill")
    
    # 1. Check patient history
    history = patient_history_tool.func("lisinopril")
    assert history["success"] and len(history["medications"]) > 0
    
    # 2. Verify medication and dosage
    rxnorm = rxnorm_tool.func("lisinopril")
    assert rxnorm["success"]
    dosage_check = dosage_verification_tool.func("lisinopril:10mg")
    assert dosage_check["success"] and dosage_check["is_valid_dosage"]
    
    # 3. Check for interactions
    interactions = interaction_tool.func("lisinopril")
    assert interactions["success"]
    
    # 4. Check insurance coverage
    insurance = insurance_tool.func("lisinopril:BlueCross Shield")
    assert insurance["success"] and insurance["covered"]
    
    # 5. Find pharmacies and check inventory
    pharmacies = pharmacy_location_tool.func("default")
    assert pharmacies["success"]
    inventory = pharmacy_inventory_tool.func("lisinopril")
    assert inventory["success"] and inventory["pharmacies_with_stock"] > 0
    
    # 6. Get pricing
    pricing = goodrx_tool.func("lisinopril:10mg:30")
    assert pricing["success"]
    
    # 7. Submit order
    order = order_submission_tool.func("lisinopril:10mg:30:walmart_plaza:12345")
    assert order["success"]
    
    print("✅ Scenario 1 completed successfully!")
    
    # Scenario 2: Prior authorization required
    print("Scenario 2: Prior Authorization Required")
    
    # Check Eliquis (requires PA)
    pa_check = prior_auth_tool.func("eliquis")
    assert pa_check["success"] and pa_check["prior_authorization_required"]
    
    insurance_eliquis = insurance_tool.func("eliquis:BlueCross Shield")
    assert insurance_eliquis["success"] and insurance_eliquis["prior_authorization_required"]
    
    print("✅ Scenario 2 completed successfully!")

def test_error_handling():
    """Test error handling and edge cases"""
    print("\n🧪 Testing Error Handling...")
    
    # Test unknown medication
    unknown_med = rxnorm_tool.func("unknownmedication123")
    assert not unknown_med["success"], "Should fail for unknown medication"
    print("✅ Unknown medication handled correctly")
    
    # Test invalid dosage format
    invalid_dosage = dosage_verification_tool.func("invalid_format")
    assert not invalid_dosage["success"], "Should fail for invalid format"
    print("✅ Invalid dosage format handled correctly")
    
    # Test pharmacy out of stock
    out_of_stock = order_submission_tool.func("eliquis:5mg:30:cvs_main:12345")
    assert not out_of_stock["success"], "Should fail when medication out of stock"
    assert "alternative_pharmacies" in out_of_stock, "Should provide alternatives"
    print("✅ Out of stock scenario handled correctly")
    
    # Test invalid pharmacy
    invalid_pharmacy = pharmacy_details_tool.func("nonexistent_pharmacy")
    assert not invalid_pharmacy["success"], "Should fail for nonexistent pharmacy"
    print("✅ Invalid pharmacy handled correctly")

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Step 3 Core Tools Integration Tests")
    print("=" * 60)
    
    try:
        test_patient_history_tools()
        test_rxnorm_tools() 
        test_pharmacy_tools()
        test_cost_tools()
        test_order_tools()
        test_workflow_scenarios()
        test_error_handling()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! Step 3 implementation is complete and working.")
        print("✅ All 15 tools implemented and tested successfully")
        print("✅ Complete workflow scenarios validated")
        print("✅ Error handling verified")
        print("✅ Enhanced mock data integration confirmed")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()