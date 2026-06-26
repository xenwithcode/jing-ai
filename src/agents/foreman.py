"""
JING-FOREMAN: The Execution Coordinator

JING-FOREMAN receives execution plans from JING-MASTER and coordinates
the specialist agents to complete the work. It:
- Executes tasks in waves (parallel/serial)
- Handles dependencies between tasks
- Manages errors and fallbacks
- Consolidates results from all agents
- Prepares final response for JING-VOICE

Usage:
    >>> from src.agents.foreman import ForemanAgent
    >>> foreman = ForemanAgent()
    >>> result = await foreman.execute_plan(
    ...     plan=master_plan,
    ...     image_url="data/images/faucet.jpg",
    ...     voice_text="This Moen is dripping"
    ... )
    >>> print(result["consolidated_response"])
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Set

from src.agents.base_agent import BaseAgent, AgentExecutionError
from src.agents.eye import EyeAgent
from src.agents.scribe import ScribeAgent
from src.agents.kit import KitAgent
from src.agents.voice import VoiceAgent
from src.agents.steward import StewardAgent
from src.agents.referee import RefereeAgent
from src.utils.config import settings
from src.utils.logger import get_logger, log_agent_execution

logger = get_logger(__name__)


class ForemanAgent(BaseAgent):
    """
    JING-FOREMAN: Execution coordinator for the multi-agent system.

    This agent doesn't do specialized work itself. It coordinates
    the specialist agents (EYE, SCRIBE, KIT, VOICE) to execute
    the plan created by JING-MASTER.
    """

    def __init__(self):
        """Initialize JING-FOREMAN and instantiate all worker agents."""
        super().__init__(name="JING-FOREMAN")

        # Instantiate worker agents
        self.workers = {
            "JING-EYE": EyeAgent(),
            "JING-SCRIBE": ScribeAgent(),
            "JING-KIT": KitAgent(),
            "JING-VOICE": VoiceAgent(),
            "JING-STEWARD": StewardAgent(),
            "JING-REFEREE": RefereeAgent(),
        }

        self.fallback_handlers = {
            "use_alternative_source": self._fallback_alternative_source,
            "simplify_diagnosis": self._fallback_simplify_diagnosis,
            "send_text_to_screen": self._fallback_text_to_screen,
            "skip_and_continue": self._fallback_skip_and_continue,
        }

        logger.info("JING-FOREMAN initialized with all worker agents (including STEWARD & REFEREE)")

    def _get_default_model(self) -> str:
        """FOREMAN uses qwen-plus for coordination logic."""
        return settings.QWEN_PLUS_MODEL

    async def execute_plan(
        self,
        plan: Dict[str, Any],
        image_url: Optional[str] = None,
        voice_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute the plan created by JING-MASTER.

        Args:
            plan: The execution plan from JING-MASTER
            image_url: URL or path to the image (if any)
            voice_text: Original voice description from technician

        Returns:
            Consolidated response with results from all agents

        Raises:
            AgentExecutionError: If critical tasks fail
        """
        logger.info(f"JING-FOREMAN executing plan with {len(plan['tasks'])} tasks")

        start_time = time.time()
        task_results = {}
        errors = []
        debate_result = None

        # ═══════════════════════════════════════════════════════════
        # EXECUTE BY WAVES WITH SELF-REFLECTION
        # ═══════════════════════════════════════════════════════════

        parallel_groups = plan["execution_strategy"]["parallel_groups"]

        for wave_num, wave in enumerate(parallel_groups, 1):
            logger.info(f"Executing wave {wave_num}/{len(parallel_groups)}: {wave}")

            # Get tasks for this wave
            wave_tasks = [t for t in plan["tasks"] if t["task_id"] in wave]

            # Execute all tasks in this wave IN PARALLEL
            wave_results = await asyncio.gather(
                *[
                    self._execute_task(task, task_results, image_url, voice_text)
                    for task in wave_tasks
                ],
                return_exceptions=True,
            )

            # Collect results and handle errors
            for task, result in zip(wave_tasks, wave_results):
                task_id = task["task_id"]

                if isinstance(result, Exception):
                    logger.error(f"Task {task_id} failed: {result}")

                    # Try executable fallback
                    fallback_used = await self._try_fallback(
                        task, task_results, image_url, voice_text
                    )

                    errors.append(
                        {
                            "task_id": task_id,
                            "agent": task["agent"],
                            "error": str(result),
                            "fallback_used": fallback_used is not None,
                        }
                    )

                    if fallback_used:
                        task_results[task_id] = fallback_used
                    else:
                        task_results[task_id] = {"status": "failed", "error": str(result)}
                else:
                    task_results[task_id] = result
                    logger.info(f"Task {task_id} completed successfully")

            # ═══════════════════════════════════════════════════════
            # SELF-REFLECTION: Quality check after each wave
            # ═══════════════════════════════════════════════════════

            await self._self_reflection_check(wave_num, wave_tasks, task_results)

        # ═══════════════════════════════════════════════════════════
        # PHASE: REFEREE DEBATE (Track 3 differentiator)
        # ═══════════════════════════════════════════════════════════

        referee = self.workers.get("JING-REFEREE")
        if referee and any(
            t["agent"] in {"JING-EYE", "JING-SCRIBE", "JING-KIT"} for t in plan["tasks"]
        ):
            logger.info("JING-FOREMAN: Initiating inter-agent debate via JING-REFEREE")
            try:
                eye_result = self._get_agent_result(task_results, plan, "JING-EYE")
                scribe_result = self._get_agent_result(task_results, plan, "JING-SCRIBE")
                kit_result = self._get_agent_result(task_results, plan, "JING-KIT")

                debate_result = await referee.resolve(
                    eye_result=eye_result,
                    scribe_result=scribe_result,
                    kit_result=kit_result,
                    original_voice_text=voice_text,
                )
                logger.info(
                    f"JING-REFEREE: {debate_result['num_conflicts_resolved']} conflicts resolved, "
                    f"consensus quality: {debate_result.get('reconciled', {}).get('consensus_quality', 'N/A')}"
                )
            except Exception as e:
                logger.error(f"JING-REFEREE debate failed: {e}", exc_info=True)

        # ═══════════════════════════════════════════════════════════
        # CONSOLIDATE RESULTS (use REFEREE reconciled if available)
        # ═══════════════════════════════════════════════════════════

        if debate_result and debate_result.get("reconciled"):
            consolidated = debate_result["reconciled"]
            consolidated["debate_metadata"] = {
                "num_conflicts": debate_result.get("num_conflicts_resolved", 0),
                "confidence_scores": debate_result.get("confidence_scores", {}),
                "consensus_quality": debate_result.get("reconciled", {}).get(
                    "consensus_quality", "medium"
                ),
            }
            logger.info("Using REFEREE-mediated consensus result")
        else:
            consolidated = await self._consolidate_results(plan, task_results)

        total_duration_ms = (time.time() - start_time) * 1000

        # ═══════════════════════════════════════════════════════════
        # BUILD FINAL RESPONSE
        # ═══════════════════════════════════════════════════════════

        final_response = {
            "execution_summary": {
                "total_tasks": len(plan["tasks"]),
                "successful_tasks": len(
                    [t for t in task_results.values() if t.get("status") != "failed"]
                ),
                "failed_tasks": len(errors),
                "total_duration_ms": total_duration_ms,
                "total_cost_usd": self._calculate_total_cost(),
            },
            "consolidated_response": consolidated,
            "agent_results": {
                task["agent"]: task_results.get(task["task_id"], {})
                for task in plan["tasks"]
                if task["agent"] not in {"JING-VOICE", "JING-REFEREE"}
            },
            "debate_result": debate_result,
            "errors": errors,
        }

        logger.info(
            f"JING-FOREMAN completed execution: "
            f"{final_response['execution_summary']['successful_tasks']}/"
            f"{final_response['execution_summary']['total_tasks']} tasks successful, "
            f"{total_duration_ms:.0f}ms total"
        )

        return final_response

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute method required by BaseAgent. Delegates to execute_plan()."""
        return await self.execute_plan(
            plan=task_input.get("plan", {}),
            image_url=task_input.get("image_url"),
            voice_text=task_input.get("voice_text"),
        )

    async def _execute_task(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Dict[str, Any]:
        """
        Execute a single task by calling the appropriate worker agent.

        Args:
            task: Task definition from the plan
            task_results: Results from previously completed tasks
            image_url: Image URL/path (for JING-EYE)
            voice_text: Voice description (for context)

        Returns:
            Task result dictionary
        """
        task_id = task["task_id"]
        agent_name = task["agent"]

        logger.info(f"Executing task {task_id} with {agent_name}")

        start_time = time.time()

        try:
            worker = self.workers.get(agent_name)
            if not worker:
                raise AgentExecutionError(f"Unknown agent: {agent_name}")

            task_input = self._build_task_input(task, task_results, image_url, voice_text)

            result = await worker.execute(task_input)

            duration_ms = (time.time() - start_time) * 1000

            log_agent_execution(
                agent_name=agent_name,
                task_id=task_id,
                status="success",
                duration_ms=duration_ms,
            )

            return {
                "status": "success",
                "data": result,
                "duration_ms": duration_ms,
            }

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            log_agent_execution(
                agent_name=agent_name,
                task_id=task_id,
                status="failed",
                duration_ms=duration_ms,
            )

            if task.get("fallback"):
                logger.warning(f"Task {task_id} failed, applying fallback: {task['fallback']}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "fallback": task["fallback"],
                    "duration_ms": duration_ms,
                }

            raise

    async def _try_fallback(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """Try to execute a fallback handler for a failed task."""
        fallback_strategy = task.get("fallback")
        if not fallback_strategy:
            return None

        handler = self.fallback_handlers.get(fallback_strategy)
        if not handler:
            logger.warning(f"No executable handler for fallback: {fallback_strategy}")
            return {"status": "failed", "fallback_logged": fallback_strategy}

        logger.info(f"Executing fallback handler: {fallback_strategy} for task {task['task_id']}")
        try:
            result = await handler(task, task_results, image_url, voice_text)
            return result
        except Exception as e:
            logger.error(f"Fallback handler {fallback_strategy} also failed: {e}")
            return None

    async def _fallback_alternative_source(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Dict[str, Any]:
        """Fallback: Try a simpler model or alternative approach."""
        logger.info(f"Fallback: Using qwen-turbo as alternative for {task['agent']}")

        from src.services.qwen_client import get_qwen_client

        client = get_qwen_client()

        fallback_prompt = f"Task: {task['objective']}. Provide a simplified response."
        try:
            response = await client.chat(
                model="qwen-turbo",
                user_message=fallback_prompt,
                temperature=0.5,
                max_tokens=500,
            )
            return {
                "status": "success",
                "data": {"fallback_result": response},
                "fallback_used": True,
            }
        except Exception:
            return {
                "status": "failed",
                "fallback_used": True,
                "error": "Alternative source also failed",
            }

    async def _fallback_simplify_diagnosis(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Dict[str, Any]:
        """Fallback: Provide a simplified diagnosis based on voice text."""
        return {
            "status": "success",
            "data": {
                "probable_cause": voice_text or "Unknown issue",
                "overall_severity": "unknown",
                "overall_confidence": 0.3,
                "object_identification": {"type": "Unknown", "brand": "", "model": ""},
                "safety_warnings": [],
                "fallback_note": "Simplified diagnosis due to agent failure",
            },
            "fallback_used": True,
        }

    async def _fallback_text_to_screen(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Dict[str, Any]:
        """Fallback: Convert voice to text output for screen display."""
        consolidated = await self._consolidate_results({"tasks": [task]}, task_results)
        return {
            "status": "success",
            "data": {
                "spoken_response": f"Diagnosis: {consolidated.get('diagnosis', 'Unknown')}. "
                f"Check the app for full details.",
                "estimated_duration_seconds": 10,
                "fallback_used": True,
            },
            "fallback_used": True,
        }

    async def _fallback_skip_and_continue(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Dict[str, Any]:
        """Fallback: Skip this task and continue with a placeholder."""
        return {
            "status": "skipped",
            "data": {
                "note": f"Task {task['task_id']} ({task['agent']}) skipped due to failure",
            },
            "fallback_used": True,
        }

    async def _self_reflection_check(
        self,
        wave_num: int,
        wave_tasks: List[Dict[str, Any]],
        task_results: Dict[str, Any],
    ) -> None:
        """
        Self-reflection: Quality check after each wave.

        Checks:
        - Are there any failed tasks that need attention?
        - Do we have sufficient data for the next wave?
        - Should we adjust the execution strategy?
        """
        failed_in_wave = [
            t for t in wave_tasks if task_results.get(t["task_id"], {}).get("status") == "failed"
        ]

        if failed_in_wave:
            logger.warning(
                f"Self-reflection: {len(failed_in_wave)} task(s) failed in wave {wave_num}: "
                f"{[t['task_id'] for t in failed_in_wave]}"
            )

            # Check if any critical task failed
            critical_failed = [t for t in failed_in_wave if t.get("priority") == "critical"]
            if critical_failed:
                logger.warning(
                    f"CRITICAL tasks failed: {[t['task_id'] for t in critical_failed]}. "
                    f"Downstream tasks may produce degraded results."
                )

        # Check data quality for downstream waves
        if wave_num == 1:
            eye_results = [
                task_results.get(t["task_id"], {}) for t in wave_tasks if t["agent"] == "JING-EYE"
            ]
            if eye_results and all(r.get("status") != "success" for r in eye_results):
                logger.warning(
                    "Self-reflection: No successful EYE analysis. Proceeding with voice-only."
                )

    def _get_agent_result(
        self,
        task_results: Dict[str, Any],
        plan: Dict[str, Any],
        agent_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get the result from a specific agent across all tasks."""
        for task in plan["tasks"]:
            if task["agent"] == agent_name:
                result = task_results.get(task["task_id"], {})
                if result.get("status") == "success":
                    return result.get("data")
        return None

    def _build_task_input(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        image_url: Optional[str],
        voice_text: Optional[str],
    ) -> Dict[str, Any]:
        """Build the input for a specific task based on its agent type."""
        agent_name = task["agent"]
        task_input = {"task_id": task["task_id"]}

        if agent_name == "JING-EYE":
            task_input["image_source"] = image_url
            task_input["context"] = voice_text
            task_input["technician_notes"] = voice_text

        elif agent_name == "JING-SCRIBE":
            eye_result = self._get_dependency_result(task, task_results, "JING-EYE")

            if eye_result:
                oi = eye_result.get("object_identification", {})
                task_input["brand"] = oi.get("brand", "Unknown")
                task_input["model"] = oi.get("model", "Unknown")
                task_input["object_type"] = oi.get("type", "Unknown")
                task_input["problem"] = eye_result.get("probable_cause", "Unknown problem")
                task_input["eye_analysis"] = eye_result
            else:
                task_input["brand"] = "Unknown"
                task_input["model"] = "Unknown"
                task_input["problem"] = voice_text or "Unknown problem"

        elif agent_name == "JING-KIT":
            eye_result = self._get_dependency_result(task, task_results, "JING-EYE")
            scribe_result = self._get_dependency_result(task, task_results, "JING-SCRIBE")

            if eye_result:
                oi = eye_result.get("object_identification", {})
                task_input["brand"] = oi.get("brand", "Unknown")
                task_input["model"] = oi.get("model", "Unknown")
                task_input["object_type"] = oi.get("type", "Unknown")
                task_input["problem"] = eye_result.get("probable_cause", "Unknown problem")
                task_input["eye_analysis"] = eye_result

            if scribe_result:
                task_input["repair_steps"] = scribe_result.get("repair_procedure", [])

        elif agent_name == "JING-STEWARD":
            eye_result = self._get_dependency_result(task, task_results, "JING-EYE")
            scribe_result = self._get_dependency_result(task, task_results, "JING-SCRIBE")
            kit_result = self._get_dependency_result(task, task_results, "JING-KIT")

            task_input["mode"] = "budget"

            if eye_result:
                task_input["diagnosis"] = eye_result.get("probable_cause", "Unknown problem")
                task_input["urgency"] = eye_result.get("overall_severity", "normal")

            if kit_result:
                parts = []
                for part in kit_result.get("parts_required", []):
                    price = 0.0
                    if part.get("where_to_buy"):
                        price_str = part["where_to_buy"][0].get("estimated_price", "$0")
                        try:
                            import re

                            numbers = re.findall(r"\d+", price_str)
                            if numbers:
                                price = float(numbers[0])
                        except:
                            price = 0.0

                    parts.append(
                        {
                            "item": part.get("part_name", "Unknown part"),
                            "quantity": 1,
                            "unit_price": price,
                            "total": price,
                        }
                    )
                task_input["parts"] = parts

                tools = [
                    f"{t['tool_name']} {t['specification']}"
                    for t in kit_result.get("tools_required", [])
                ]
                task_input["tools"] = tools

            if scribe_result:
                task_input["estimated_hours"] = self._parse_duration_to_hours(
                    scribe_result.get("estimated_time", "1 hour")
                )

            if eye_result:
                obj_type = eye_result.get("object_identification", {}).get("type", "").lower()
                if any(word in obj_type for word in ["faucet", "pipe", "plumb", "toilet", "sink"]):
                    task_input["trade"] = "plumber"
                elif any(word in obj_type for word in ["hvac", "thermostat", "furnace", "ac"]):
                    task_input["trade"] = "hvac"
                elif any(
                    word in obj_type for word in ["washer", "dryer", "dishwasher", "refrigerator"]
                ):
                    task_input["trade"] = "appliance"
                elif any(word in obj_type for word in ["panel", "breaker", "wire", "outlet"]):
                    task_input["trade"] = "electrician"
                else:
                    task_input["trade"] = "general"

        elif agent_name == "JING-VOICE":
            eye_result = self._get_dependency_result(task, task_results, "JING-EYE")
            scribe_result = self._get_dependency_result(task, task_results, "JING-SCRIBE")
            kit_result = self._get_dependency_result(task, task_results, "JING-KIT")

            if eye_result:
                task_input["diagnosis"] = eye_result.get("probable_cause", "Unknown problem")
                task_input["safety_warnings"] = [
                    w["warning"] for w in eye_result.get("safety_warnings", [])
                ]

            if kit_result:
                parts = kit_result.get("parts_required", [])
                if parts:
                    task_input["part_number"] = parts[0].get("oem_part_number")

                tools = kit_result.get("tools_required", [])
                task_input["tools"] = [f"{t['tool_name']} {t['specification']}" for t in tools[:3]]

                cost = kit_result.get("estimated_total_cost", {})
                task_input["additional_context"] = {
                    "estimated_cost": cost.get("total", "Unknown"),
                }

            if scribe_result:
                task_input["manual_reference"] = scribe_result.get("relevant_section", {}).get(
                    "page_reference"
                )
                task_input["additional_context"] = task_input.get("additional_context", {})
                task_input["additional_context"]["estimated_time"] = scribe_result.get(
                    "estimated_time", "Unknown"
                )

        return task_input

    def _get_dependency_result(
        self,
        task: Dict[str, Any],
        task_results: Dict[str, Any],
        agent_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Get the result from a dependency task (by agent name)."""
        for dep_task_id in task.get("depends_on", []):
            dep_result = task_results.get(dep_task_id, {})
            if dep_result.get("status") == "success":
                return dep_result.get("data")
        return None

    def _parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string like '30-45 minutes' to hours."""
        import re

        if not duration_str:
            return 1.0
        numbers = re.findall(r"\d+", duration_str)
        if not numbers:
            return 1.0
        avg_minutes = sum(int(n) for n in numbers) / len(numbers)
        if "hour" in duration_str.lower():
            return avg_minutes
        return max(0.25, avg_minutes / 60)

    async def _consolidate_results(
        self,
        plan: Dict[str, Any],
        task_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Consolidate results from all agents into a unified response."""
        eye_result = None
        scribe_result = None
        kit_result = None

        for task in plan["tasks"]:
            task_id = task["task_id"]
            result = task_results.get(task_id, {})

            if result.get("status") != "success":
                continue

            data = result.get("data", {})

            if task["agent"] == "JING-EYE":
                eye_result = data
            elif task["agent"] == "JING-SCRIBE":
                scribe_result = data
            elif task["agent"] == "JING-KIT":
                kit_result = data

        consolidated = {
            "diagnosis": "Unknown",
            "severity": "unknown",
            "procedure_summary": "No procedure available",
            "key_tools": [],
            "part_number": None,
            "manual_reference": None,
            "safety_warnings": [],
            "estimated_cost": "Unknown",
            "estimated_time": "Unknown",
        }

        if eye_result:
            consolidated["diagnosis"] = eye_result.get("probable_cause", "Unknown")
            consolidated["severity"] = eye_result.get("overall_severity", "unknown")
            consolidated["safety_warnings"] = [
                w["warning"] for w in eye_result.get("safety_warnings", [])
            ]

        if scribe_result:
            num_steps = len(scribe_result.get("repair_procedure", []))
            consolidated["procedure_summary"] = f"{num_steps}-step repair procedure available"
            consolidated["manual_reference"] = scribe_result.get("relevant_section", {}).get(
                "page_reference"
            )
            consolidated["estimated_time"] = scribe_result.get("estimated_time", "Unknown")

        if kit_result:
            parts = kit_result.get("parts_required", [])
            if parts:
                consolidated["part_number"] = parts[0].get("oem_part_number")

            tools = kit_result.get("tools_required", [])
            consolidated["key_tools"] = [
                f"{t['tool_name']} {t['specification']}" for t in tools[:3]
            ]

            cost = kit_result.get("estimated_total_cost", {})
            consolidated["estimated_cost"] = cost.get("total", "Unknown")

        return consolidated

    def _calculate_total_cost(self) -> float:
        """Calculate total cost from Qwen client."""
        from src.services.qwen_client import get_qwen_client

        client = get_qwen_client()
        summary = client.get_cost_summary()
        return summary["total_cost"]

    async def consolidate(self, plan: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Public method for consolidation (used by orchestrator).

        This is a wrapper around _consolidate_results for compatibility.
        """
        return await self._consolidate_results(plan, results)


# ═══════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════


async def _demo():
    """Demo JING-FOREMAN with a complete workflow."""
    from src.agents.master import MasterAgent

    foreman = ForemanAgent()
    master = MasterAgent()

    print("\n" + "=" * 70)
    print("JING-FOREMAN Execution Demo")
    print("=" * 70)

    print("\n📋 Scenario: HVAC technician with a broken thermostat")
    print("   Image: (simulated) honeywell_thermostat.jpg")
    print("   Voice: 'This Honeywell T9 won't power on'")

    try:
        print("\n[1/2] JING-MASTER creating plan...")
        plan = await master.plan(
            image_url="data/images/honeywell_thermostat.jpg",
            voice_text="This Honeywell T9 won't power on",
        )
        print(f"   ✅ Plan created with {len(plan['tasks'])} tasks")

        print("\n[2/2] JING-FOREMAN executing plan...")
        result = await foreman.execute_plan(
            plan=plan,
            image_url="data/images/honeywell_thermostat.jpg",
            voice_text="This Honeywell T9 won't power on",
        )

        print("\n✅ Execution completed!")

        print(f"\n📊 Execution Summary:")
        summary = result["execution_summary"]
        print(f"   Total tasks: {summary['total_tasks']}")
        print(f"   Successful: {summary['successful_tasks']}")
        print(f"   Failed: {summary['failed_tasks']}")
        print(f"   Total duration: {summary['total_duration_ms']:.0f}ms")
        print(f"   Total cost: ${summary['total_cost_usd']:.4f}")

        print(f"\n🎯 Consolidated Response:")
        consolidated = result["consolidated_response"]
        print(f"   Diagnosis: {consolidated['diagnosis']}")
        print(f"   Severity: {consolidated['severity']}")
        print(f"   Procedure: {consolidated['procedure_summary']}")
        print(f"   Part number: {consolidated['part_number'] or 'N/A'}")
        print(f"   Manual: {consolidated['manual_reference'] or 'N/A'}")
        print(f"   Estimated cost: {consolidated['estimated_cost']}")
        print(f"   Estimated time: {consolidated['estimated_time']}")

        if consolidated["key_tools"]:
            print(f"   Key tools: {', '.join(consolidated['key_tools'])}")

        if consolidated["safety_warnings"]:
            print(f"\n🚨 Safety Warnings:")
            for warning in consolidated["safety_warnings"]:
                print(f"   • {warning}")

        if result["errors"]:
            print(f"\n⚠️  Errors:")
            for error in result["errors"]:
                print(f"   • Task {error['task_id']} ({error['agent']}): {error['error']}")

    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import asyncio

    asyncio.run(_demo())
