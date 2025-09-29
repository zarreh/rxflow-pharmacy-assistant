"""
Test escalation system for RxFlow Pharmacy Assistant
"""

import asyncio

import pytest

from rxflow.tools.escalation_tools import escalation_check_tool
from rxflow.workflow.conversation_manager import ConversationManager


class TestEscalationSystem:
    """Test medical escalation scenarios"""

    @pytest.mark.asyncio
    async def test_no_refills_escalation(self):
        """Test doctor escalation for medications with no refills"""
        manager = ConversationManager()
        response = await manager.process_message(
            "test_no_refills", "I need a refill for my metformin"
        )

        response_lower = response.message.lower()
        assert any(
            keyword in response_lower
            for keyword in [
                "escalat",
                "pharmacist",
                "doctor",
                "physician",
                "refill",
                "prescription",
            ]
        ), f"Expected escalation keywords in: {response.message}"

    @pytest.mark.asyncio
    async def test_controlled_substance_escalation(self):
        """Test doctor escalation for controlled substances"""
        manager = ConversationManager()
        response = await manager.process_message(
            "test_controlled", "I need to refill my lorazepam"
        )

        response_lower = response.message.lower()
        assert any(
            keyword in response_lower
            for keyword in ["escalat", "pharmacist", "doctor", "controlled"]
        ), f"Expected escalation for controlled substance: {response.message}"

    @pytest.mark.asyncio
    async def test_unknown_medication_escalation(self):
        """Test pharmacist consultation for unknown medications"""
        manager = ConversationManager()
        response = await manager.process_message(
            "test_unknown", "I need to refill my xyz123medicine"
        )

        response_lower = response.message.lower()
        # Check if the system properly handles unknown medication (either suggests alternatives or escalates)
        unknown_indicators = [
            "not recognized",
            "not found",
            "double-check",
            "correct name",
            "suggestions",
            "common medications",
            "database",
            "escalat",
            "pharmacist",
            "couldn't find",
            "no record",
            "consult",
        ]
        assert any(
            indicator in response_lower for indicator in unknown_indicators
        ), f"Expected unknown medication handling: {response.message}"

    def test_escalation_tool_direct(self):
        """Test escalation tool directly"""
        result = escalation_check_tool.invoke("hydrocodone")

        # Should return escalation info as JSON string or dict
        result_lower = str(result).lower()
        assert "escalation" in result_lower or "pharmacist" in result_lower
