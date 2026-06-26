from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.agents.base_agent import AgentValidationError


@pytest.fixture(autouse=True)
def mock_qwen_client():
    """Mock Qwen client to prevent real API calls during ALL tests."""
    with patch("src.agents.base_agent.get_qwen_client") as mock:
        client = MagicMock()
        client.get_cost_summary.return_value = {
            "total_cost": 0.0,
            "remaining_budget": 40.0,
            "call_count": 0,
            "calls_by_model": {},
        }
        client.get_remaining_budget.return_value = 40.0
        client.health_check = AsyncMock(return_value=True)
        mock.return_value = client
        yield


@pytest.fixture
def sample_budget_data() -> Dict[str, Any]:
    return {
        "budget_metadata": {
            "budget_number": "BUD-001",
            "date": "2024-01-15",
            "job_title": "Faucet Cartridge Replacement",
        },
        "cost_breakdown": {
            "parts_subtotal": 28.00,
            "labor": {"estimated_hours": 0.75, "hourly_rate": 100, "total": 75.00},
            "subtotal": 103.00,
            "margin_percentage": 25,
            "margin_amount": 25.75,
            "tax_percentage": 8,
            "tax_amount": 10.30,
            "total": 139.05,
            "total_rounded": 140.00,
        },
        "payment_terms": {"method": "cash", "due": "upon_completion", "deposit_required": False},
        "financial_health": {
            "profit_margin_percentage": 25,
            "effective_hourly_rate": 186.67,
            "risk_level": "low",
        },
        "client_info": {"name": "John Smith", "address": None, "contact": None},
        "job_description": {
            "summary": "Faucet Cartridge Replacement",
            "scope": [],
            "exclusions": [],
            "estimated_duration": "1 hour",
        },
        "warranty": {
            "parts_warranty": "Manufacturer warranty",
            "labor_warranty": "90 days",
            "void_conditions": [],
        },
        "client_friendly_total": "$140.00",
    }


@pytest.fixture
def sample_budget_data_minimal() -> Dict[str, Any]:
    """Budget data with only the 4 required keys - tests default filling."""
    return {
        "budget_metadata": {"budget_number": "BUD-001", "date": "2024-01-15", "job_title": "Test"},
        "cost_breakdown": {
            "parts_subtotal": 20.00,
            "labor": {"estimated_hours": 1.0, "hourly_rate": 80, "total": 80.00},
            "subtotal": 100.00,
            "margin_percentage": 20,
            "margin_amount": 20.00,
            "tax_percentage": 8,
            "tax_amount": 9.60,
            "total": 129.60,
        },
        "payment_terms": {"method": "card", "due": "upon_completion", "deposit_required": False},
        "financial_health": {
            "profit_margin_percentage": 20,
            "effective_hourly_rate": 100.00,
            "risk_level": "low",
        },
    }


@pytest.fixture
def sample_summary_data() -> Dict[str, Any]:
    return {
        "job_info": {"client": "John Smith", "job_title": "Faucet Repair", "date": "2024-01-15"},
        "profitability": {
            "gross_revenue": 160.00,
            "direct_costs": 50.00,
            "gross_profit": 110.00,
            "net_margin_percentage": 68.8,
            "effective_hourly_rate": 192.77,
            "profitability_grade": "A",
        },
        "chart_data": {"labels": ["Parts", "Labor", "Profit"], "values": [30, 20, 110]},
    }


@pytest.fixture
def sample_summary_data_minimal() -> Dict[str, Any]:
    """Summary data with only the 3 required keys - tests default filling."""
    return {
        "job_info": {"client": "Jane Doe", "job_title": "Thermostat Install", "date": "2024-02-01"},
        "profitability": {
            "gross_revenue": 200.00,
            "direct_costs": 60.00,
            "gross_profit": 140.00,
            "net_margin_percentage": 70.0,
            "effective_hourly_rate": 200.00,
            "profitability_grade": "A+",
        },
        "chart_data": {"labels": ["Parts", "Labor", "Profit"], "values": [40, 20, 140]},
    }


@pytest.fixture
def sample_plan_data() -> Dict[str, Any]:
    return {
        "request_analysis": {
            "surface_request": "This Moen is dripping",
            "actual_need": "Replace Moen 1225 cartridge",
            "urgency": "normal",
            "missing_context": [],
        },
        "tasks": [
            {
                "task_id": "T1",
                "agent": "JING-EYE",
                "objective": "Identify faucet model and issue",
                "inputs": {},
                "depends_on": [],
                "priority": "high",
                "success_criteria": "Identified cartridge type",
                "fallback": "skip_and_continue",
            },
            {
                "task_id": "T2",
                "agent": "JING-SCRIBE",
                "objective": "Find repair procedure",
                "inputs": {},
                "depends_on": ["T1"],
                "priority": "normal",
                "success_criteria": "Procedure found",
                "fallback": "simplify_diagnosis",
            },
            {
                "task_id": "T3",
                "agent": "JING-VOICE",
                "objective": "Provide final response",
                "inputs": {},
                "depends_on": ["T1", "T2"],
                "priority": "normal",
                "success_criteria": "Response delivered",
                "fallback": "send_text_to_screen",
            },
        ],
        "execution_strategy": {
            "parallel_groups": [["T1"], ["T2"], ["T3"]],
            "critical_path": ["T1", "T2", "T3"],
        },
        "consolidation": {
            "final_agent": "JING-VOICE",
            "output_format": "voice with text backup",
            "key_info_to_include": ["diagnosis", "procedure", "parts"],
        },
    }


@pytest.fixture
def sample_plan_data_no_voice_end() -> Dict[str, Any]:
    """Plan that does NOT end with JING-VOICE - should trigger auto-fix."""
    return {
        "request_analysis": {
            "surface_request": "Fridge not cooling",
            "actual_need": "Diagnose compressor issue",
            "urgency": "high",
            "missing_context": [],
        },
        "tasks": [
            {
                "task_id": "T1",
                "agent": "JING-EYE",
                "objective": "Inspect fridge components",
                "inputs": {},
                "depends_on": [],
                "priority": "critical",
                "success_criteria": "Identified failed component",
                "fallback": "simplify_diagnosis",
            },
            {
                "task_id": "T2",
                "agent": "JING-KIT",
                "objective": "List required parts",
                "inputs": {},
                "depends_on": ["T1"],
                "priority": "normal",
                "success_criteria": "Parts listed",
                "fallback": "skip_and_continue",
            },
        ],
        "execution_strategy": {
            "parallel_groups": [["T1"], ["T2"]],
            "critical_path": ["T1", "T2"],
        },
        "consolidation": {
            "final_agent": "JING-KIT",
            "output_format": "text",
            "key_info_to_include": ["parts"],
        },
    }


@pytest.fixture
def sample_client_data() -> Dict[str, Any]:
    return {"name": "Test Client", "phone": "555-0100", "trade": "plumber"}
