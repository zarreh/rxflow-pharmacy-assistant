"""
Test the conversation chains implementation
"""

import asyncio
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rxflow.workflow.chains import (CostOptimizationChain, EscalationChain,
                                    MedicationConfirmationChain,
                                    OrderConfirmationChain,
                                    PharmacySelectionChain)
from rxflow.workflow.chains.prompts import RxFlowPrompts


async def test_medication_confirmation():
    """Test medication confirmation chain"""
    print("🧪 Testing Medication Confirmation Chain...")

    chain = MedicationConfirmationChain()

    # Test case 1: Complete medication info
    context1 = {
        "medication_name": "lisinopril",
        "medication_strength": "10mg",
        "quantity": 30,
    }

    response1 = await chain.invoke(context1)
    print("✅ Test 1 (Complete info):")
    print(f"Response: {response1}\n")

    # Test case 2: Missing strength
    context2 = {"medication_name": "metformin", "quantity": 30}

    response2 = await chain.invoke(context2)
    print("✅ Test 2 (Missing strength):")
    print(f"Response: {response2}\n")

    return True


async def test_pharmacy_selection():
    """Test pharmacy selection chain"""
    print("🧪 Testing Pharmacy Selection Chain...")

    chain = PharmacySelectionChain()

    # Test with multiple pharmacy options
    context = {
        "medication_name": "lisinopril",
        "available_pharmacies": [
            {
                "name": "CVS Pharmacy #12345",
                "distance_miles": 0.5,
                "wait_time_hours": 0.5,
                "price": 15.00,
            },
            {
                "name": "Walmart Pharmacy #98765",
                "distance_miles": 3.0,
                "wait_time_hours": 1.0,
                "price": 4.00,
            },
            {
                "name": "H-E-B Pharmacy #77777",
                "distance_miles": 1.2,
                "wait_time_hours": 0.5,
                "price": 8.00,
            },
        ],
    }

    response = await chain.invoke(context)
    print("✅ Pharmacy Selection Test:")
    print(f"Response: {response}\n")

    return True


async def test_cost_optimization():
    """Test cost optimization chain"""
    print("🧪 Testing Cost Optimization Chain...")

    chain = CostOptimizationChain()

    context = {
        "medication_name": "Lipitor",
        "brand_price": 320.00,
        "generic_price": 15.00,
        "generic_name": "atorvastatin",
        "insurance_copay": 10.00,
    }

    response = await chain.invoke(context)
    print("✅ Cost Optimization Test:")
    print(f"Response: {response}\n")

    return True


async def test_escalation_scenarios():
    """Test different escalation scenarios"""
    print("🧪 Testing Escalation Chains...")

    chain = EscalationChain()

    # Test no refills scenario
    context1 = {
        "escalation_type": "no_refills",
        "medication_name": "lisinopril",
        "prescriber_name": "Dr. Sarah Johnson",
    }

    response1 = await chain.invoke(context1)
    print("✅ No Refills Escalation:")
    print(f"Response: {response1}\n")

    # Test prior authorization scenario
    context2 = {
        "escalation_type": "prior_auth",
        "medication_name": "Eliquis",
        "prescriber_name": "Dr. Michael Brown",
    }

    response2 = await chain.invoke(context2)
    print("✅ Prior Auth Escalation:")
    print(f"Response: {response2}\n")

    return True


async def test_order_confirmation():
    """Test order confirmation chain"""
    print("🧪 Testing Order Confirmation Chain...")

    chain = OrderConfirmationChain()

    context = {
        "medication_name": "Lisinopril 10mg",
        "pharmacy_name": "CVS Pharmacy #12345",
        "pickup_time": "after 2:00 PM today",
        "confirmation_number": "RX123456",
        "estimated_savings": 11.50,
    }

    response = await chain.invoke(context)
    print("✅ Order Confirmation Test:")
    print(f"Response: {response}\n")

    return True


def test_prompts():
    """Test prompt templates"""
    print("🧪 Testing Prompt Templates...")

    # Test simple prompts
    greeting = RxFlowPrompts.get_prompt("greeting", patient_name=" John")
    print("✅ Greeting Prompt:")
    print(f"Response: {greeting}\n")

    clarification = RxFlowPrompts.get_prompt(
        "clarification", unclear_input="my heart medication"
    )
    print("✅ Clarification Prompt:")
    print(f"Response: {clarification}\n")

    # Test chat prompt retrieval
    try:
        confirmation_prompt = RxFlowPrompts.get_chat_prompt("medication_confirmation")
        print("✅ Chat Prompt Retrieved Successfully\n")
    except Exception as e:
        print(f"❌ Chat Prompt Error: {e}\n")
        return False

    return True


async def main():
    """Run all conversation chain tests"""
    print("🚀 Starting Conversation Chain Tests\n")

    try:
        # Run all tests
        await test_medication_confirmation()
        await test_pharmacy_selection()
        await test_cost_optimization()
        await test_escalation_scenarios()
        await test_order_confirmation()

        print("✅ All conversation chain tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
