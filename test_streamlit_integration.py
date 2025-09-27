#!/usr/bin/env python3
"""
Test Streamlit Integration with Conversation Chains
Quick validation that chains work in the app context
"""

import asyncio
import json

from rxflow.workflow.chains.conversation_chains import (
    CostOptimizationChain, EscalationChain, MedicationConfirmationChain,
    OrderConfirmationChain, PharmacySelectionChain)


async def test_full_conversation_flow():
    """Test a complete conversation flow similar to Streamlit app"""
    print("🧪 Testing Full Conversation Flow (Streamlit-style)\n")

    # Initialize chains (same as in Streamlit)
    chains = {
        "medication_confirmation": MedicationConfirmationChain(),
        "pharmacy_selection": PharmacySelectionChain(),
        "cost_optimization": CostOptimizationChain(),
        "escalation": EscalationChain(),
        "order_confirmation": OrderConfirmationChain(),
    }

    # Simulate conversation context (same as Streamlit session state)
    context = {}

    print("👤 User: I need to refill my lisinopril 10mg")

    # Step 1: Medication Confirmation
    context.update(
        {
            "user_input": "I need to refill my lisinopril 10mg",
            "medication_name": "Lisinopril",
            "strength": "10mg",
            "quantity": "30",
        }
    )

    response1 = await chains["medication_confirmation"].invoke(context)
    print(f"🤖 Assistant: {response1}\n")

    # Step 2: Pharmacy Selection
    print("👤 User: Yes, show me pharmacy options")

    context["available_pharmacies"] = [
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
    ]

    response2 = await chains["pharmacy_selection"].invoke(context)
    print(f"🤖 Assistant: {response2}\n")

    # Step 3: Pharmacy Choice & Cost Optimization
    print("👤 User: I'll choose option 2 (Walmart)")

    context["selected_pharmacy"] = context["available_pharmacies"][1]
    context.update(
        {
            "brand_price": 45.00,
            "generic_price": 4.00,
            "generic_name": "lisinopril",
            "insurance_copay": 10.00,
        }
    )

    response3 = await chains["cost_optimization"].invoke(context)
    print(f"🤖 Assistant: {response3}\n")

    # Step 4: Order Confirmation
    print("👤 User: Yes, proceed with the generic version")

    context.update(
        {
            "pharmacy_name": context["selected_pharmacy"]["name"],
            "pickup_time": "after 2:00 PM today",
            "confirmation_number": "RX123456",
            "estimated_savings": context["brand_price"] - context["generic_price"],
        }
    )

    response4 = await chains["order_confirmation"].invoke(context)
    print(f"🤖 Assistant: {response4}\n")

    print("✅ Full conversation flow completed successfully!")
    return True


async def test_escalation_flow():
    """Test escalation scenario"""
    print("\n🧪 Testing Escalation Flow\n")

    chain = EscalationChain()

    print("👤 User: I have no refills remaining for my prescription")

    context = {
        "user_input": "I have no refills remaining for my prescription",
        "escalation_type": "no_refills",
        "medication_name": "lisinopril",
        "prescriber_name": "Dr. Sarah Johnson",
    }

    response = await chain.invoke(context)
    print(f"🤖 Assistant: {response}\n")

    print("✅ Escalation flow completed successfully!")
    return True


async def main():
    """Run integration tests"""
    print("🚀 Starting Streamlit Integration Tests\n")

    try:
        await test_full_conversation_flow()
        await test_escalation_flow()

        print("🎉 All integration tests passed!")
        print("💡 The conversation chains are ready for Streamlit app!")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
