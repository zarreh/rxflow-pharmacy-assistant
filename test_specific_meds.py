#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from rxflow.tools.patient_history_tool import PatientHistoryTool

def test_specific_medications():
    print("🔍 Testing Specific Medication Queries")
    print("=" * 50)
    
    tool = PatientHistoryTool()
    
    # Test specific medication queries
    test_queries = ["omeprazole", "lisinopril", "metformin", "nonexistent", "o", ""]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        result = tool.get_medication_history(query)
        print(f"  Success: {result.get('success')}")
        print(f"  Medications count: {len(result.get('medications', []))}")
        
        medications = result.get('medications', [])
        if medications:
            med_names = [med.get('name') for med in medications]
            print(f"  Found medications: {med_names}")
        else:
            print(f"  No medications found")

if __name__ == "__main__":
    test_specific_medications()