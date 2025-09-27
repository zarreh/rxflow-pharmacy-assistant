#!/usr/bin/env python3
"""
Integration Test Runner for RxFlow Pharmacy Assistant
Step 9: Execute comprehensive integration testing suite
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.test_integration import run_comprehensive_integration_tests
from rxflow.utils.logger import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)


def print_header():
    """Print test runner header"""
    print("\n" + "="*80)
    print("🧪 RXFLOW PHARMACY ASSISTANT - INTEGRATION TEST RUNNER")
    print("="*80)
    print("Step 9: Comprehensive Integration Testing")
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)


def print_test_scenario(scenario_name: str, description: str):
    """Print individual test scenario info"""
    print(f"\n🔬 {scenario_name}")
    print(f"   {description}")
    print("   " + "-" * 60)


async def run_individual_scenario_tests():
    """Run each test scenario individually with detailed logging"""
    
    from tests.test_integration import PharmacyWorkflowTests
    
    test_suite = PharmacyWorkflowTests()
    
    scenarios = [
        {
            "name": "Test 1: Happy Path",
            "description": "Simple lisinopril refill workflow",
            "method": test_suite.test_1_happy_path_lisinopril_refill,
            "expected_tools": ["patient_medication_history", "rxnorm_medication_lookup", "find_nearby_pharmacies", "submit_refill_order"],
            "expected_states": 4
        },
        {
            "name": "Test 2: Disambiguation",
            "description": "Generic 'blood pressure medication' identification",
            "method": test_suite.test_2_disambiguation_blood_pressure_medication,
            "expected_tools": ["patient_medication_history", "rxnorm_medication_lookup"],
            "expected_states": 5
        },
        {
            "name": "Test 3: Prior Authorization",
            "description": "Eliquis refill requiring insurance approval",
            "method": test_suite.test_3_prior_authorization_eliquis,
            "expected_tools": ["rxnorm_medication_lookup", "insurance_formulary_check", "prior_auth_check"],
            "expected_states": 3
        },
        {
            "name": "Test 4: Cost Optimization",
            "description": "Brand vs generic comparison (Lipitor)",
            "method": test_suite.test_4_cost_optimization_brand_vs_generic,
            "expected_tools": ["rxnorm_medication_lookup", "goodrx_price_lookup", "brand_generic_alternatives"],
            "expected_states": 6
        },
        {
            "name": "Test 5: Error Handling",
            "description": "Unknown medication recovery workflow",
            "method": test_suite.test_5_error_handling_unknown_medication,
            "expected_tools": ["patient_medication_history", "rxnorm_medication_lookup"],
            "expected_states": 3
        }
    ]
    
    individual_results = []
    
    for scenario in scenarios:
        print_test_scenario(scenario["name"], scenario["description"])
        
        try:
            logger.info(f"[TEST RUNNER] Executing {scenario['name']}")
            
            # Run the test
            result = await scenario["method"]()
            
            # Validate results
            validation = validate_test_result(result, scenario)
            result["validation"] = validation
            
            # Print results
            print(f"   ✅ Status: {'PASSED' if result['success'] else 'FAILED'}")
            print(f"   📊 Messages: {result.get('total_messages', 0)}")
            print(f"   🔧 Tools Used: {result.get('total_tools_used', 0)}")
            print(f"   🎯 State Accuracy: {result.get('state_accuracy', 0):.1%}")
            
            if validation["warnings"]:
                print(f"   ⚠️  Warnings: {len(validation['warnings'])}")
                for warning in validation["warnings"]:
                    print(f"      - {warning}")
            
            if not result["success"]:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            
            individual_results.append(result)
            
        except Exception as e:
            logger.error(f"[TEST RUNNER] {scenario['name']} execution failed: {e}")
            individual_results.append({
                "test_name": scenario["name"],
                "success": False,
                "error": str(e),
                "execution_time": datetime.now().isoformat()
            })
    
    return individual_results


def validate_test_result(result: dict, scenario: dict) -> dict:
    """Validate test result against expected outcomes"""
    warnings = []
    
    # Check if minimum tools were used
    tools_used = result.get("total_tools_used", 0)
    if tools_used == 0:
        warnings.append("No tools were used - check tool integration")
    
    # Check state accuracy
    state_accuracy = result.get("state_accuracy", 0)
    if state_accuracy < 0.8:
        warnings.append(f"Low state accuracy ({state_accuracy:.1%}) - review state transitions")
    
    # Check conversation flow
    messages = result.get("total_messages", 0)
    expected_states = scenario.get("expected_states", 0)
    if messages != expected_states:
        warnings.append(f"Message count ({messages}) doesn't match expected states ({expected_states})")
    
    return {
        "warnings": warnings,
        "validation_passed": len(warnings) == 0
    }


def generate_final_report(comprehensive_results: dict, individual_results: list):
    """Generate and display final test report"""
    print("\n" + "="*80)
    print("📋 FINAL INTEGRATION TEST REPORT")
    print("="*80)
    
    summary = comprehensive_results["summary"]
    
    print(f"📊 Test Summary:")
    print(f"   Total Tests: {summary['total_tests']}")
    print(f"   Successful: {summary['successful_tests']} ✅")
    print(f"   Failed: {summary['failed_tests']} ❌")
    print(f"   Success Rate: {summary['success_rate']:.1%}")
    print(f"   Total Tools Used: {summary['total_tools_used']}")
    print(f"   Average State Accuracy: {summary['average_state_accuracy']:.1%}")
    
    print(f"\n🔧 Tool Integration Analysis:")
    tool_counts = {}
    for result in individual_results:
        for log in result.get("tool_usage_log", []):
            tool_name = log["tool"]
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
    
    if tool_counts:
        for tool, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   - {tool}: {count} calls")
    else:
        print("   ⚠️  No tool usage detected")
    
    print(f"\n🎯 State Machine Analysis:")
    total_transitions = sum(len(result.get("state_transitions", [])) for result in individual_results)
    successful_transitions = sum(
        sum(1 for t in result.get("state_transitions", []) if t.get("match", False))
        for result in individual_results
    )
    
    print(f"   Total State Transitions: {total_transitions}")
    print(f"   Successful Transitions: {successful_transitions}")
    print(f"   Transition Accuracy: {successful_transitions/total_transitions:.1%}" if total_transitions > 0 else "   No transitions recorded")
    
    print(f"\n💡 Recommendations:")
    for rec in comprehensive_results["recommendations"]:
        print(f"   - {rec}")
    
    # Overall assessment
    overall_health = "EXCELLENT" if summary['success_rate'] >= 0.9 else \
                    "GOOD" if summary['success_rate'] >= 0.7 else \
                    "NEEDS IMPROVEMENT"
    
    print(f"\n🏥 Overall System Health: {overall_health}")
    print("="*80)
    
    return {
        "overall_health": overall_health,
        "summary": summary,
        "tool_counts": tool_counts,
        "total_transitions": total_transitions,
        "successful_transitions": successful_transitions
    }


def save_detailed_report(comprehensive_results: dict, individual_results: list, final_assessment: dict):
    """Save detailed test report to file"""
    report_data = {
        "test_execution": {
            "timestamp": datetime.now().isoformat(),
            "step": "Step 9: Integration Testing",
            "overall_health": final_assessment["overall_health"]
        },
        "comprehensive_results": comprehensive_results,
        "individual_results": individual_results,
        "final_assessment": final_assessment
    }
    
    # Save to tests directory
    report_file = "tests/integration_test_detailed_report.json"
    with open(report_file, "w") as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    return report_file


async def main():
    """Main test runner execution"""
    print_header()
    
    try:
        # Run individual scenario tests with detailed logging
        print("\n🔬 EXECUTING INDIVIDUAL TEST SCENARIOS")
        individual_results = await run_individual_scenario_tests()
        
        # Run comprehensive test suite
        print("\n\n🧪 EXECUTING COMPREHENSIVE TEST SUITE")
        print("   Running all scenarios together...")
        comprehensive_results = await run_comprehensive_integration_tests()
        
        # Generate final analysis and report
        final_assessment = generate_final_report(comprehensive_results, individual_results)
        
        # Save detailed report
        report_file = save_detailed_report(comprehensive_results, individual_results, final_assessment)
        
        print(f"\n🎉 Integration testing completed!")
        print(f"   System Health: {final_assessment['overall_health']}")
        print(f"   Success Rate: {comprehensive_results['summary']['success_rate']:.1%}")
        
        return comprehensive_results['summary']['success_rate'] >= 0.7
        
    except Exception as e:
        logger.error(f"[TEST RUNNER] Critical error: {e}")
        print(f"\n❌ Test runner failed: {e}")
        return False


if __name__ == "__main__":
    # Run the integration test suite
    success = asyncio.run(main())
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)