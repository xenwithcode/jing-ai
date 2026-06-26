import pytest
from pydantic import ValidationError

from src.models.eye_result import EyeAnalysis, ObjectIdentification, ProblemDetected
from src.models.kit_result import (
    KitList,
    ToolRequired,
    PartRequired,
    EstimatedTotalCost,
    ShoppingStrategy,
)
from src.models.plan import (
    Consolidation,
    ExecutionPlan,
    ExecutionStrategy,
    RequestAnalysis,
    Task,
)
from src.models.request import TechnicianRequest
from src.models.response import AgentResult, ConsolidatedResponse, ExecutionSummary, JingResponse
from src.models.scribe_result import ManualFound, RepairStep, ScribeProcedure


class TestTask:
    def test_valid_task(self):
        t = Task(
            task_id="T1",
            agent="JING-EYE",
            objective="Inspect the faucet",
            depends_on=[],
            priority="high",
            success_criteria="Identified the issue",
        )
        assert t.task_id == "T1"
        assert t.agent == "JING-EYE"
        assert t.priority == "high"
        assert t.inputs == {}
        assert t.fallback is None

    def test_invalid_agent_name(self):
        with pytest.raises(ValidationError):
            Task(
                task_id="T1",
                agent="JING-UNKNOWN",
                objective="test",
                depends_on=[],
                priority="normal",
                success_criteria="done",
            )

    def test_invalid_priority(self):
        with pytest.raises(ValidationError):
            Task(
                task_id="T1",
                agent="JING-EYE",
                objective="test",
                depends_on=[],
                priority="urgent",
                success_criteria="done",
            )

    def test_all_valid_agents(self):
        for agent in [
            "JING-EYE",
            "JING-SCRIBE",
            "JING-KIT",
            "JING-VOICE",
            "JING-STEWARD",
            "JING-REFEREE",
        ]:
            t = Task(
                task_id="T1",
                agent=agent,
                objective="test",
                depends_on=[],
                priority="normal",
                success_criteria="done",
            )
            assert t.agent == agent

    def test_all_priorities(self):
        for pri in ["critical", "high", "normal", "low"]:
            t = Task(
                task_id="T1",
                agent="JING-EYE",
                objective="test",
                depends_on=[],
                priority=pri,
                success_criteria="done",
            )
            assert t.priority == pri

    def test_default_fallback_is_none(self):
        t = Task(
            task_id="T1",
            agent="JING-EYE",
            objective="test",
            depends_on=[],
            priority="normal",
            success_criteria="done",
        )
        assert t.fallback is None

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            Task()

    def test_depends_on_defaults_to_empty(self):
        t = Task(
            task_id="T1",
            agent="JING-EYE",
            objective="test",
            priority="normal",
            success_criteria="done",
        )
        assert t.depends_on == []

    def test_inputs_defaults_to_empty_dict(self):
        t = Task(
            task_id="T1",
            agent="JING-EYE",
            objective="test",
            depends_on=[],
            priority="normal",
            success_criteria="done",
        )
        assert t.inputs == {}

    def test_with_fallback(self):
        t = Task(
            task_id="T1",
            agent="JING-EYE",
            objective="test",
            depends_on=[],
            priority="normal",
            success_criteria="done",
            fallback="skip_and_continue",
        )
        assert t.fallback == "skip_and_continue"


class TestExecutionPlan:
    def test_valid_plan(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        assert len(plan.tasks) == 3
        assert plan.get_task_by_id("T1") is not None
        assert plan.get_task_by_id("NONEXISTENT") is None

    def test_min_length_tasks(self, sample_plan_data):
        sample_plan_data["tasks"] = []
        with pytest.raises(ValidationError):
            ExecutionPlan(**sample_plan_data)

    def test_get_task_by_id(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        t = plan.get_task_by_id("T2")
        assert t is not None
        assert t.agent == "JING-SCRIBE"

    def test_get_tasks_by_agent(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        tasks = plan.get_tasks_by_agent("JING-EYE")
        assert len(tasks) == 1
        assert tasks[0].task_id == "T1"

    def test_get_tasks_by_agent_none(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        assert plan.get_tasks_by_agent("JING-KIT") == []

    def test_get_wave(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        wave0 = plan.get_wave(0)
        assert len(wave0) == 1
        assert wave0[0].task_id == "T1"

    def test_get_wave_out_of_range(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        assert plan.get_wave(99) == []


class TestRequestAnalysis:
    def test_valid_request_analysis(self):
        ra = RequestAnalysis(
            surface_request="Faucet dripping",
            actual_need="Replace cartridge",
            urgency="normal",
        )
        assert ra.surface_request == "Faucet dripping"
        assert ra.urgency == "normal"

    def test_invalid_urgency(self):
        with pytest.raises(ValidationError):
            RequestAnalysis(
                surface_request="test",
                actual_need="test",
                urgency="super_critical",
            )

    def test_missing_context_default(self):
        ra = RequestAnalysis(
            surface_request="test",
            actual_need="test",
            urgency="normal",
        )
        assert ra.missing_context == []


class TestExecutionStrategy:
    def test_valid_strategy(self):
        es = ExecutionStrategy(
            parallel_groups=[["T1"], ["T2", "T3"]],
            critical_path=["T1", "T2"],
        )
        assert len(es.parallel_groups) == 2


class TestConsolidation:
    def test_valid_consolidation(self):
        c = Consolidation(
            output_format="voice",
            key_info_to_include=["diagnosis"],
        )
        assert c.final_agent == "JING-VOICE"

    def test_custom_final_agent(self):
        c = Consolidation(
            final_agent="JING-KIT",
            output_format="text",
            key_info_to_include=["parts"],
        )
        assert c.final_agent == "JING-KIT"


class TestTechnicianRequest:
    def test_with_image_only(self):
        req = TechnicianRequest(image_source="http://example.com/img.jpg")
        assert req.has_image()
        assert not req.has_voice()

    def test_with_voice_only(self):
        req = TechnicianRequest(voice_text="This is broken")
        assert req.has_voice()
        assert not req.has_image()

    def test_with_both(self):
        req = TechnicianRequest(image_source="img.jpg", voice_text="broken")
        assert req.has_image()
        assert req.has_voice()

    def test_neither_raises(self):
        with pytest.raises(ValueError):
            TechnicianRequest()

    def test_additional_context_default(self):
        req = TechnicianRequest(voice_text="broken")
        assert req.additional_context == {}

    def test_image_source_as_path(self):
        from pathlib import Path

        req = TechnicianRequest(image_source=Path("/tmp/test.jpg"))
        assert req.has_image()


class TestEyeAnalysis:
    def test_valid_eye_analysis(self):
        analysis = EyeAnalysis(
            object_identification={
                "object": "Faucet",
                "brand": "Moen",
                "type": "faucet",
                "condition": "worn",
            },
            problem_detected={
                "description": "Cartridge leaking",
                "location": "handle assembly",
                "type": "leak",
                "severity_visible": "moderate",
            },
            overall_severity="moderate",
            probable_cause="Worn cartridge seal",
            confidence={
                "level": "high",
                "score": 0.85,
                "reasoning": "Clear visual indicators",
            },
        )
        assert analysis.object_identification.brand == "Moen"
        assert analysis.overall_severity == "moderate"

    def test_invalid_condition(self):
        with pytest.raises(ValidationError):
            EyeAnalysis(
                object_identification={
                    "object": "Faucet",
                    "type": "faucet",
                    "condition": "mint",
                },
                problem_detected={
                    "description": "x",
                    "location": "x",
                    "type": "leak",
                    "severity_visible": "moderate",
                },
                overall_severity="moderate",
                probable_cause="x",
                confidence={
                    "level": "high",
                    "score": 0.85,
                    "reasoning": "x",
                },
            )

    def test_confidence_score_range(self):
        with pytest.raises(ValidationError):
            EyeAnalysis(
                object_identification={
                    "object": "Faucet",
                    "type": "faucet",
                    "condition": "good",
                },
                problem_detected={
                    "description": "x",
                    "location": "x",
                    "type": "leak",
                    "severity_visible": "moderate",
                },
                overall_severity="moderate",
                probable_cause="x",
                confidence={
                    "level": "high",
                    "score": 1.5,
                    "reasoning": "x",
                },
            )

    def test_optional_fields_default(self):
        analysis = EyeAnalysis(
            object_identification={
                "object": "Faucet",
                "type": "faucet",
                "condition": "good",
            },
            problem_detected={
                "description": "x",
                "location": "x",
                "type": "leak",
                "severity_visible": "moderate",
            },
            overall_severity="minor",
            probable_cause="x",
            confidence={
                "level": "medium",
                "score": 0.5,
                "reasoning": "x",
            },
        )
        assert analysis.alternative_causes == []
        assert analysis.safety_warnings == []
        assert analysis.limitations == []
        assert analysis.recommendations == []


class TestScribeProcedure:
    def test_valid_scribe_procedure(self):
        proc = ScribeProcedure(
            manual_found={
                "found": True,
                "title": "Moen Faucet Manual",
                "source": "official_manual",
                "confidence": "high",
            },
            repair_procedure=[
                RepairStep(step_number=1, action="Turn off water supply"),
            ],
            estimated_time="30 minutes",
            difficulty_level="beginner",
            knowledge_disclosure="Based on official Moen manual",
        )
        assert proc.manual_found.title == "Moen Faucet Manual"
        assert len(proc.repair_procedure) == 1

    def test_empty_repair_procedure(self):
        with pytest.raises(ValidationError):
            ScribeProcedure(
                manual_found={
                    "found": True,
                    "source": "official_manual",
                    "confidence": "high",
                },
                repair_procedure=[],
                estimated_time="1 hour",
                difficulty_level="beginner",
                knowledge_disclosure="test",
            )

    def test_invalid_difficulty(self):
        with pytest.raises(ValidationError):
            ScribeProcedure(
                manual_found={
                    "found": True,
                    "source": "official_manual",
                    "confidence": "high",
                },
                repair_procedure=[RepairStep(step_number=1, action="test")],
                estimated_time="1 hour",
                difficulty_level="expert",
                knowledge_disclosure="test",
            )

    def test_defaults(self):
        proc = ScribeProcedure(
            manual_found={
                "found": False,
                "source": "internal_knowledge",
                "confidence": "low",
            },
            repair_procedure=[RepairStep(step_number=1, action="test")],
            estimated_time="1 hour",
            difficulty_level="intermediate",
            knowledge_disclosure="test",
        )
        assert proc.special_tools == []
        assert proc.common_mistakes == []
        assert proc.relevant_section is None


class TestKitList:
    def test_valid_kit_list(self):
        kit = KitList(
            tools_required=[
                ToolRequired(
                    tool_name="Allen wrench",
                    specification="3/32",
                    purpose="Remove cartridge",
                )
            ],
            estimated_total_cost=EstimatedTotalCost(total="$45.00"),
            shopping_strategy=ShoppingStrategy(recommended_store="Home Depot"),
        )
        assert len(kit.tools_required) == 1
        assert kit.get_specialized_tools() == []
        assert kit.get_total_cost_range() == "$45.00"

    def test_empty_tools_required(self):
        with pytest.raises(ValidationError):
            KitList(
                tools_required=[],
                estimated_total_cost=EstimatedTotalCost(total="$0"),
                shopping_strategy=ShoppingStrategy(recommended_store="Store"),
            )

    def test_specialized_tools_filter(self):
        kit = KitList(
            tools_required=[
                ToolRequired(
                    tool_name="Regular wrench",
                    specification="10mm",
                    purpose="General",
                ),
                ToolRequired(
                    tool_name="Special tool",
                    specification="S-100",
                    purpose="Special",
                    is_specialized=True,
                ),
            ],
            estimated_total_cost=EstimatedTotalCost(total="$100.00"),
            shopping_strategy=ShoppingStrategy(recommended_store="Tool Store"),
        )
        specialized = kit.get_specialized_tools()
        assert len(specialized) == 1
        assert specialized[0].tool_name == "Special tool"


class TestJingResponse:
    def test_valid_response(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        resp = JingResponse(
            execution_summary=ExecutionSummary(
                total_duration_ms=1000.0,
                planning_duration_ms=200.0,
                execution_duration_ms=800.0,
                total_cost_usd=0.05,
                remaining_budget_usd=39.95,
                total_tasks=3,
                successful_tasks=3,
                failed_tasks=0,
            ),
            plan=plan,
            consolidated_response=ConsolidatedResponse(
                diagnosis="Cartridge failure",
                severity="moderate",
                procedure_summary="Replace cartridge",
                estimated_cost="$140.00",
                estimated_time="1 hour",
            ),
        )
        assert resp.is_success()
        assert resp.get_spoken_text() is None

    def test_failed_response(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        resp = JingResponse(
            execution_summary=ExecutionSummary(
                total_duration_ms=1000.0,
                planning_duration_ms=200.0,
                execution_duration_ms=800.0,
                total_cost_usd=0.05,
                remaining_budget_usd=39.95,
                total_tasks=3,
                successful_tasks=2,
                failed_tasks=1,
            ),
            plan=plan,
            consolidated_response=ConsolidatedResponse(
                diagnosis="x",
                severity="high",
                procedure_summary="x",
                estimated_cost="$0",
                estimated_time="0",
            ),
        )
        assert not resp.is_success()

    def test_agent_results_default(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        resp = JingResponse(
            execution_summary=ExecutionSummary(
                total_duration_ms=1,
                planning_duration_ms=1,
                execution_duration_ms=1,
                total_cost_usd=0,
                remaining_budget_usd=40,
                total_tasks=1,
                successful_tasks=1,
                failed_tasks=0,
            ),
            plan=plan,
            consolidated_response=ConsolidatedResponse(
                diagnosis="x",
                severity="low",
                procedure_summary="x",
                estimated_cost="$0",
                estimated_time="0",
            ),
        )
        assert resp.agent_results == {}

    def test_get_spoken_text_success(self, sample_plan_data):
        plan = ExecutionPlan(**sample_plan_data)
        resp = JingResponse(
            execution_summary=ExecutionSummary(
                total_duration_ms=1,
                planning_duration_ms=1,
                execution_duration_ms=1,
                total_cost_usd=0,
                remaining_budget_usd=40,
                total_tasks=1,
                successful_tasks=1,
                failed_tasks=0,
            ),
            plan=plan,
            consolidated_response=ConsolidatedResponse(
                diagnosis="x",
                severity="low",
                procedure_summary="x",
                estimated_cost="$0",
                estimated_time="0",
            ),
            voice_response={
                "status": "success",
                "data": {"spoken_response": "Replace the cartridge"},
            },
        )
        assert resp.get_spoken_text() == "Replace the cartridge"


class TestExecutionSummary:
    def test_all_fields_required(self):
        with pytest.raises(ValidationError):
            ExecutionSummary()

    def test_valid_summary(self):
        s = ExecutionSummary(
            total_duration_ms=100.0,
            planning_duration_ms=20.0,
            execution_duration_ms=80.0,
            total_cost_usd=0.01,
            remaining_budget_usd=39.99,
            total_tasks=2,
            successful_tasks=2,
            failed_tasks=0,
        )
        assert s.total_tasks == 2


class TestAgentResult:
    def test_valid_agent_result(self):
        ar = AgentResult(status="success", data={"key": "value"})
        assert ar.status == "success"
        assert ar.error is None

    def test_failed_agent_result(self):
        ar = AgentResult(status="failed", error="Something went wrong")
        assert ar.error == "Something went wrong"

    def test_optional_fields_default(self):
        ar = AgentResult(status="success")
        assert ar.data is None
        assert ar.error is None
        assert ar.duration_ms is None
