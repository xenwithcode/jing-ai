"""
JING-MASTER: The Strategic Planner

JING-MASTER is the brain of the JING system. It analyzes technician requests
and creates structured execution plans that JING-FOREMAN then executes.

Key responsibilities:
- Deep analysis of what the technician REALLY needs
- Task decomposition into atomic, delegatable units
- Dependency management between tasks
- Fallback strategy planning
- Safety-first prioritization

Usage:
    >>> from src.agents.master import MasterAgent
    >>> master = MasterAgent()
    >>> plan = await master.plan(
    ...     image_url="https://example.com/faucet.jpg",
    ...     voice_text="This Moen is dripping"
    ... )
    >>> print(plan["tasks"])
"""

import json
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent, AgentExecutionError, AgentValidationError
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MasterAgent(BaseAgent):
    """
    JING-MASTER: Strategic planner for the multi-agent system.

    This agent does NOT execute tasks. It ONLY plans them.
    It uses Qwen-Max (the most powerful model) because planning
    requires deep reasoning and understanding of complex scenarios.
    """

    def __init__(self):
        """Initialize JING-MASTER with qwen-max model."""
        super().__init__(name="JING-MASTER")
        logger.info("JING-MASTER initialized (strategic planner)")

    def _get_default_model(self) -> str:
        """MASTER uses the most powerful model for planning."""
        return settings.QWEN_MAX_MODEL

    async def plan(
        self,
        image_url: Optional[str] = None,
        voice_text: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create an execution plan for a technician request.

        Args:
            image_url: URL or path to the image (if any)
            voice_text: Transcribed voice description from technician
            additional_context: Any extra context (location, time, history)

        Returns:
            Structured execution plan as a dictionary with:
            - request_analysis
            - tasks
            - execution_strategy
            - consolidation

        Raises:
            AgentValidationError: If inputs are invalid
            AgentExecutionError: If planning fails
        """
        # ═══════════════════════════════════════════════════════════
        # VALIDATE INPUTS
        # ═══════════════════════════════════════════════════════════

        if not image_url and not voice_text:
            raise AgentValidationError("At least one of image_url or voice_text must be provided")

        logger.info(
            f"JING-MASTER planning request: "
            f"image={'yes' if image_url else 'no'}, "
            f"voice={'yes' if voice_text else 'no'}"
        )

        # ═══════════════════════════════════════════════════════════
        # BUILD THE PROMPT
        # ═══════════════════════════════════════════════════════════

        user_message = self._build_planning_prompt(
            image_url=image_url,
            voice_text=voice_text,
            additional_context=additional_context,
        )

        # ═══════════════════════════════════════════════════════════
        # CALL QWEN WITH RETRY LOGIC
        # ═══════════════════════════════════════════════════════════

        try:
            plan = await self.call_qwen_json(
                user_message=user_message,
                temperature=0.2,  # Low temperature for structured output
                max_tokens=2000,  # Plans can be long
            )
        except json.JSONDecodeError as e:
            logger.error(f"JING-MASTER returned invalid JSON: {e}")
            raise AgentExecutionError(f"Invalid JSON from MASTER: {e}") from e
        except Exception as e:
            logger.error(f"JING-MASTER planning failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Planning failed: {e}") from e

        # ═══════════════════════════════════════════════════════════
        # VALIDATE THE PLAN STRUCTURE
        # ═══════════════════════════════════════════════════════════

        validated_plan = self._validate_plan(plan)

        logger.info(f"JING-MASTER created plan with {len(validated_plan['tasks'])} tasks")

        return validated_plan

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method required by BaseAgent.

        Delegates to plan() method.
        """
        return await self.plan(
            image_url=task_input.get("image_url"),
            voice_text=task_input.get("voice_text"),
            additional_context=task_input.get("additional_context"),
        )

    def _build_planning_prompt(
        self,
        image_url: Optional[str],
        voice_text: Optional[str],
        additional_context: Optional[Dict[str, Any]],
    ) -> str:
        """Build the user prompt for planning."""
        parts = ["══════ TECHNICIAN REQUEST ══════\n"]

        if image_url:
            parts.append(f"📸 IMAGE: {image_url}")
        else:
            parts.append("📸 IMAGE: (none provided)")

        if voice_text:
            parts.append(f"🎤 VOICE DESCRIPTION: {voice_text}")
        else:
            parts.append("🎤 VOICE DESCRIPTION: (none provided)")

        if additional_context:
            parts.append(f"\n📋 ADDITIONAL CONTEXT:")
            for key, value in additional_context.items():
                parts.append(f"  - {key}: {value}")

        parts.append("\n═══════════════════════════════")
        parts.append("\nCreate a structured execution plan in JSON format.")

        return "\n".join(parts)

    def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the plan has the required structure.

        This is a safety net: if Qwen returns malformed JSON,
        we catch it here instead of failing later in execution.

        Args:
            plan: The raw plan dictionary from Qwen

        Returns:
            The validated plan (same structure, but verified)

        Raises:
            AgentValidationError: If the plan is missing required fields
        """
        # Check top-level keys
        required_keys = ["request_analysis", "tasks", "execution_strategy", "consolidation"]
        for key in required_keys:
            if key not in plan:
                raise AgentValidationError(f"Plan missing required key: {key}")

        # Validate request_analysis
        ra = plan["request_analysis"]
        if not isinstance(ra, dict):
            raise AgentValidationError("request_analysis must be a dictionary")

        for key in ["surface_request", "actual_need", "urgency"]:
            if key not in ra:
                raise AgentValidationError(f"request_analysis missing: {key}")

        if ra.get("urgency") not in ["critical", "high", "normal", "low"]:
            raise AgentValidationError(f"Invalid urgency: {ra.get('urgency')}")

        # Validate tasks
        tasks = plan["tasks"]
        if not isinstance(tasks, list) or len(tasks) == 0:
            raise AgentValidationError("tasks must be a non-empty list")

        task_ids = set()
        valid_agents = {
            "JING-EYE",
            "JING-SCRIBE",
            "JING-KIT",
            "JING-VOICE",
            "JING-STEWARD",
            "JING-REFEREE",
        }

        for i, task in enumerate(tasks):
            if not isinstance(task, dict):
                raise AgentValidationError(f"Task {i} must be a dictionary")

            required_task_keys = ["task_id", "agent", "objective", "depends_on", "priority"]
            for key in required_task_keys:
                if key not in task:
                    raise AgentValidationError(f"Task {i} missing: {key}")

            if task["agent"] not in valid_agents:
                raise AgentValidationError(
                    f"Task {task['task_id']} has invalid agent: {task['agent']}. "
                    f"Must be one of: {valid_agents}"
                )

            if task["priority"] not in ["critical", "high", "normal", "low"]:
                raise AgentValidationError(
                    f"Task {task['task_id']} has invalid priority: {task['priority']}"
                )

            if task["task_id"] in task_ids:
                raise AgentValidationError(f"Duplicate task_id: {task['task_id']}")
            task_ids.add(task["task_id"])

        # Validate dependencies reference existing tasks
        for task in tasks:
            for dep in task.get("depends_on", []):
                if dep not in task_ids:
                    raise AgentValidationError(
                        f"Task {task['task_id']} depends on non-existent task: {dep}"
                    )

        # Validate execution_strategy
        es = plan["execution_strategy"]
        if not isinstance(es, dict):
            raise AgentValidationError("execution_strategy must be a dictionary")

        if "parallel_groups" not in es:
            raise AgentValidationError("execution_strategy missing parallel_groups")

        # Check that all tasks appear in parallel_groups
        all_tasks_in_groups = set()
        for group in es["parallel_groups"]:
            for task_id in group:
                if task_id not in task_ids:
                    raise AgentValidationError(
                        f"parallel_groups references non-existent task: {task_id}"
                    )
                all_tasks_in_groups.add(task_id)

        missing_from_groups = task_ids - all_tasks_in_groups
        if missing_from_groups:
            raise AgentValidationError(f"Tasks not in parallel_groups: {missing_from_groups}")

        # Ensure JING-VOICE is the final task
        last_group = es["parallel_groups"][-1]
        voice_tasks = [
            tid
            for tid in last_group
            if any(t["task_id"] == tid and t["agent"] == "JING-VOICE" for t in tasks)
        ]

        if not voice_tasks:
            logger.warning("Plan does not end with JING-VOICE task. Adding a default voice task.")
            new_task_id = f"T{len(tasks) + 1}"
            tasks.append(
                {
                    "task_id": new_task_id,
                    "agent": "JING-VOICE",
                    "objective": "Vocalize consolidated response to technician",
                    "inputs": {"summary": "consolidated_from_previous_tasks"},
                    "depends_on": [t["task_id"] for t in tasks if t["agent"] != "JING-VOICE"],
                    "priority": "normal",
                    "success_criteria": "Response under 30 seconds",
                    "fallback": "Send text to phone screen",
                }
            )
            es["parallel_groups"].append([new_task_id])
            task_ids.add(new_task_id)

        logger.debug(f"Plan validated successfully: {len(tasks)} tasks")

        return plan


# ═══════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════


async def _demo():
    """Demo JING-MASTER with a realistic scenario."""
    master = MasterAgent()

    print("\n" + "=" * 70)
    print("JING-MASTER Planning Demo")
    print("=" * 70)

    print("\n📋 Scenario: HVAC technician with a broken thermostat")
    print("   Image: (simulated) honeywell_thermostat.jpg")
    print("   Voice: 'This Honeywell T9 won't power on, customer is freezing'")

    try:
        plan = await master.plan(
            image_url="data/images/honeywell_thermostat.jpg",
            voice_text="This Honeywell T9 won't power on, customer is freezing",
            additional_context={
                "technician_experience": "5 years HVAC",
                "customer_urgency": "high - elderly person, winter",
            },
        )

        print("\n✅ Plan created successfully!")
        print(f"\n📊 Request Analysis:")
        print(f"   Surface: {plan['request_analysis']['surface_request']}")
        print(f"   Actual need: {plan['request_analysis']['actual_need']}")
        print(f"   Urgency: {plan['request_analysis']['urgency']}")

        print(f"\n📝 Tasks ({len(plan['tasks'])}):")
        for task in plan["tasks"]:
            deps = ", ".join(task["depends_on"]) if task["depends_on"] else "none"
            print(f"   • {task['task_id']} [{task['agent']}] {task['priority'].upper()}")
            print(f"     Objective: {task['objective']}")
            print(f"     Depends on: {deps}")

        print(f"\n⚡ Execution Strategy:")
        for i, group in enumerate(plan["execution_strategy"]["parallel_groups"]):
            print(f"   Wave {i + 1}: {', '.join(group)}")

        print(f"\n🎯 Critical Path: {' → '.join(plan['execution_strategy']['critical_path'])}")

        print(f"\n🔊 Final Output:")
        print(f"   Agent: {plan['consolidation']['final_agent']}")
        print(f"   Key info: {', '.join(plan['consolidation']['key_info_to_include'])}")

        from src.services.qwen_client import get_qwen_client

        client = get_qwen_client()
        summary = client.get_cost_summary()
        print(f"\n💰 Cost of this plan: ${summary['total_cost']:.4f}")
        print(f"   Remaining budget: ${summary['remaining_budget']:.2f}")

    except Exception as e:
        print(f"\n❌ Planning failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import asyncio

    asyncio.run(_demo())
