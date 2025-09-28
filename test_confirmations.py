#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from rxflow.tools.patient_history_tool import PatientHistoryTool

def test_confirmation_queries():
    print("🔍 Testing Confirmation Query Handling")
    print("=" * 50)
    
    tool = PatientHistoryTool()
    
    # Test confirmation-like queries that should return all medications
    test_queries = ["yes", "no", "ok", "sure", "maybe"]
    
    for query in test_queries:
        print(f"\nTesting query: '{query}'")
        result = tool.get_medication_history(query)
        print(f"  Success: {result.get('success')}")
        print(f"  Medications count: {len(result.get('medications', []))}")
        
        if result.get('medications'):
            print(f"  ✅ Returns all medications (expected)")
        else:
            print(f"  ❌ No medications returned")

if __name__ == "__main__":
    test_confirmation_queries()