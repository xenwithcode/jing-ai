from unittest.mock import MagicMock, patch

import pytest

from src.agents.base_agent import AgentValidationError
from src.agents.foreman import ForemanAgent
from src.agents.master import MasterAgent
from src.agents.steward import StewardAgent


class TestStewardAgentValidateBudget:
    def test_valid_budget(self, sample_budget_data):
        steward = StewardAgent()
        result = steward._validate_budget(sample_budget_data)
        assert result["cost_breakdown"]["total_rounded"] == 140.00
        assert result["client_friendly_total"] == "$140.00"

    def test_missing_required_keys(self):
        steward = StewardAgent()
        with pytest.raises(AgentValidationError, match="Budget missing required key"):
            steward._validate_budget({"incomplete": True})

    def test_missing_cost_breakdown_keys(self):
        steward = StewardAgent()
        data = {
            "budget_metadata": {"budget_number": "B-001", "date": "today", "job_title": "Test"},
            "cost_breakdown": {"parts_subtotal": 10.00},
            "payment_terms": {"method": "cash", "due": "now", "deposit_required": False},
            "financial_health": {
                "profit_margin_percentage": 10,
                "effective_hourly_rate": 50,
                "risk_level": "low",
            },
        }
        result = steward._validate_budget(data)
        assert "total_rounded" in result["cost_breakdown"]

    def test_budget_fills_defaults(self, sample_budget_data_minimal):
        steward = StewardAgent()
        result = steward._validate_budget(sample_budget_data_minimal)
        assert "client_info" in result
        assert result["client_info"]["name"] == "New Client"
        assert "job_description" in result
        assert "warranty" in result
        assert "client_friendly_total" in result

    def test_budget_with_missing_total_rounded(self):
        steward = StewardAgent()
        data = {
            "budget_metadata": {"budget_number": "B-001", "date": "today", "job_title": "Test"},
            "cost_breakdown": {"total": 130.00},
            "payment_terms": {"method": "cash", "due": "now", "deposit_required": False},
            "financial_health": {
                "profit_margin_percentage": 25,
                "effective_hourly_rate": 100,
                "risk_level": "low",
            },
        }
        result = steward._validate_budget(data)
        assert result["cost_breakdown"]["total_rounded"] == 130

    def test_low_margin_does_not_raise(self, sample_budget_data):
        steward = StewardAgent()
        data = sample_budget_data.copy()
        data["cost_breakdown"]["margin_percentage"] = 10
        result = steward._validate_budget(data)
        assert result["cost_breakdown"]["margin_percentage"] == 10


class TestStewardAgentValidateSummary:
    def test_valid_summary(self, sample_summary_data):
        steward = StewardAgent()
        result = steward._validate_summary(sample_summary_data)
        assert result["profitability"]["profitability_grade"] == "A"

    def test_missing_required_keys(self):
        steward = StewardAgent()
        with pytest.raises(AgentValidationError, match="Summary missing required key"):
            steward._validate_summary({"bad": "data"})

    def test_summary_fills_defaults(self, sample_summary_data_minimal):
        steward = StewardAgent()
        result = steward._validate_summary(sample_summary_data_minimal)
        assert "comparison" in result
        assert result["comparison"]["budgeted_total"] == 0
        assert "cost_analysis" in result
        assert "performance_metrics" in result
        assert result["performance_metrics"]["overall_score"] == 75
        assert "insights" in result
        assert "celebration_message" in result

    def test_default_celebration_empty(self, sample_summary_data):
        steward = StewardAgent()
        result = steward._validate_summary(sample_summary_data)
        assert result["celebration_message"] == ""

    def test_default_performance_metrics(self, sample_summary_data):
        steward = StewardAgent()
        data = sample_summary_data.copy()
        data.pop("chart_data", None)
        with pytest.raises(AgentValidationError):
            steward._validate_summary(data)


class TestMasterAgentValidatePlan:
    def test_valid_plan(self, sample_plan_data):
        master = MasterAgent()
        result = master._validate_plan(sample_plan_data)
        assert len(result["tasks"]) == 3

    def test_missing_top_level_key(self, sample_plan_data):
        master = MasterAgent()
        del sample_plan_data["tasks"]
        with pytest.raises(AgentValidationError, match="Plan missing required key"):
            master._validate_plan(sample_plan_data)

    def test_invalid_urgency(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["request_analysis"]["urgency"] = "invalid"
        with pytest.raises(AgentValidationError, match="Invalid urgency"):
            master._validate_plan(sample_plan_data)

    def test_empty_tasks(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["tasks"] = []
        with pytest.raises(AgentValidationError, match="tasks must be a non-empty list"):
            master._validate_plan(sample_plan_data)

    def test_invalid_agent(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["tasks"][0]["agent"] = "JING-HACKER"
        with pytest.raises(AgentValidationError, match="invalid agent"):
            master._validate_plan(sample_plan_data)

    def test_duplicate_task_id(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["tasks"].append(sample_plan_data["tasks"][0].copy())
        with pytest.raises(AgentValidationError, match="Duplicate task_id"):
            master._validate_plan(sample_plan_data)

    def test_nonexistent_dependency(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["tasks"][1]["depends_on"] = ["T99"]
        with pytest.raises(AgentValidationError, match="non-existent task"):
            master._validate_plan(sample_plan_data)

    def test_missing_parallel_groups(self, sample_plan_data):
        master = MasterAgent()
        del sample_plan_data["execution_strategy"]["parallel_groups"]
        with pytest.raises(AgentValidationError, match="missing parallel_groups"):
            master._validate_plan(sample_plan_data)

    def test_task_not_in_parallel_groups(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["execution_strategy"]["parallel_groups"] = [["T1"]]
        with pytest.raises(AgentValidationError, match="not in parallel_groups"):
            master._validate_plan(sample_plan_data)

    def test_parallel_groups_refers_nonexistent_task(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["execution_strategy"]["parallel_groups"].append(["T99"])
        with pytest.raises(AgentValidationError, match="non-existent task"):
            master._validate_plan(sample_plan_data)

    def test_no_voice_task_added_automatically(self, sample_plan_data_no_voice_end):
        master = MasterAgent()
        result = master._validate_plan(sample_plan_data_no_voice_end)
        tasks = result["tasks"]
        assert any(t["agent"] == "JING-VOICE" for t in tasks)
        last_group = result["execution_strategy"]["parallel_groups"][-1]
        voice_in_last_group = any(
            t["task_id"] in last_group and t["agent"] == "JING-VOICE" for t in tasks
        )
        assert voice_in_last_group

    def test_missing_task_id(self, sample_plan_data):
        master = MasterAgent()
        del sample_plan_data["tasks"][0]["task_id"]
        with pytest.raises(AgentValidationError, match="missing"):
            master._validate_plan(sample_plan_data)

    def test_invalid_priority_in_task(self, sample_plan_data):
        master = MasterAgent()
        sample_plan_data["tasks"][0]["priority"] = "emergency"
        with pytest.raises(AgentValidationError, match="invalid priority"):
            master._validate_plan(sample_plan_data)

    def test_missing_request_analysis_fields(self, sample_plan_data):
        master = MasterAgent()
        del sample_plan_data["request_analysis"]["surface_request"]
        with pytest.raises(AgentValidationError, match="request_analysis missing"):
            master._validate_plan(sample_plan_data)


class TestForemanAgent:
    def test_parse_duration_to_hours_minutes(self):
        foreman = ForemanAgent()
        assert foreman._parse_duration_to_hours("30 minutes") == 0.5

    def test_parse_duration_to_hours_range_minutes(self):
        foreman = ForemanAgent()
        result = foreman._parse_duration_to_hours("30-45 minutes")
        assert result == 0.625  # (30 + 45) / 2 / 60

    def test_parse_duration_to_hours_hours(self):
        foreman = ForemanAgent()
        result = foreman._parse_duration_to_hours("2 hours")
        assert result == 2.0

    def test_parse_duration_to_hours_range_hours(self):
        foreman = ForemanAgent()
        # re.findall(r"\d+", "1.5-2 hours") => ["1", "5", "2"], avg=2.67, contains "hour" => 2.67
        result = foreman._parse_duration_to_hours("1.5-2 hours")
        assert result == pytest.approx(2.67, rel=0.01)

    def test_parse_duration_to_hours_minimum_floor(self):
        foreman = ForemanAgent()
        result = foreman._parse_duration_to_hours("5 minutes")
        assert result == 0.25  # max(0.25, 5/60)

    def test_parse_duration_to_hours_empty_string(self):
        foreman = ForemanAgent()
        assert foreman._parse_duration_to_hours("") == 1.0

    def test_parse_duration_to_hours_no_numbers(self):
        foreman = ForemanAgent()
        assert foreman._parse_duration_to_hours("unknown duration") == 1.0

    def test_calculate_total_cost(self):
        foreman = ForemanAgent()
        with patch("src.services.qwen_client.get_qwen_client") as mock_get:
            mock_client = MagicMock()
            mock_client.get_cost_summary.return_value = {"total_cost": 0.05}
            mock_get.return_value = mock_client

            cost = foreman._calculate_total_cost()
            assert cost == 0.05
