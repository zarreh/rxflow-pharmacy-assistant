#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from rxflow.services.mock_data import MOCK_PATIENTS
from rxflow.tools.patient_history_tool import PatientHistoryTool

def test_patient_data():
    print("🔍 Testing Patient Data Access")
    print("=" * 50)
    
    # Test 1: Check MOCK_PATIENTS data
    print(f"MOCK_PATIENTS keys: {list(MOCK_PATIENTS.keys())}")
    
    if "12345" in MOCK_PATIENTS:
        patient = MOCK_PATIENTS["12345"]
        print(f"Patient 12345 found:")
        print(f"  Name: {patient.get('name')}")
        print(f"  Medications count: {len(patient.get('medications', []))}")
        
        for i, med in enumerate(patient.get('medications', [])[:3]):  # Show first 3
            print(f"  Medication {i+1}: {med.get('name')} - {med.get('dosage')}")
    else:
        print("❌ Patient 12345 not found in MOCK_PATIENTS")
    
    # Test 2: Check PatientHistoryTool
    print("\n" + "-" * 50)
    tool = PatientHistoryTool()
    
    # Test with different query formats
    test_queries = ["", "all", "unknown"]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        result = tool.get_medication_history(query)
        print(f"  Success: {result.get('success')}")
        print(f"  Patient ID: {result.get('patient_id')}")
        print(f"  Medications count: {len(result.get('medications', []))}")
        
        if result.get('medications'):
            print(f"  First medication: {result['medications'][0].get('name')}")

if __name__ == "__main__":
    test_patient_data()