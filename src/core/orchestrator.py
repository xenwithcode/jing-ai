"""
JING Orchestrator: The Complete Workflow Engine

This is the main entry point for the JING system. It coordinates the entire
workflow from technician input to final response:

1. Receive input (image + voice/text)
2. JING-MASTER creates execution plan
3. JING-FOREMAN executes plan with all worker agents
4. Return consolidated response

Usage:
    >>> from src.core.orchestrator import get_orchestrator
    >>> orchestrator = get_orchestrator()
    >>> result = await orchestrator.process(
    ...     image_url="data/images/faucet.jpg",
    ...     voice_text="This Moen is dripping"
    ... )
    >>> print(result["consolidated_response"])
"""

import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union

from src.agents.master import MasterAgent
from src.agents.foreman import ForemanAgent
from src.agents.steward import StewardAgent
from src.services.qwen_client import get_qwen_client
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class JingOrchestrator:
    """
    Main orchestrator for the JING multi-agent system.
    
    This class provides a simple, high-level interface to the entire JING
    workflow. It hides the complexity of planning and execution behind a
    single `process()` method.
    
    Architecture:
        Technician Input
              ↓
        JING-MASTER (plans)
              ↓
        JING-FOREMAN (executes)
              ↓
        ┌─────┴─────┬──────────┬──────────┬─────────────┐
        ↓           ↓          ↓          ↓             ↓
    JING-EYE   JING-SCRIBE  JING-KIT  JING-VOICE  JING-STEWARD
        ↓           ↓          ↓          ↓             ↓
        └─────┬─────┴──────────┴──────────┴─────────────┘
              ↓
        Consolidated Response
              ↓
        Technician Output
    """
    
    def __init__(self):
        """Initialize the orchestrator with all required agents."""
        self.master = MasterAgent()
        self.foreman = ForemanAgent()
        self.steward = StewardAgent()
        self.qwen_client = get_qwen_client()
        
        logger.info("JING Orchestrator initialized")
        logger.info(f"  Budget: ${self.qwen_client.get_remaining_budget():.2f} remaining")
    
    async def process(
        self,
        image_source: Optional[Union[str, Path, bytes]] = None,
        voice_text: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process a technician request end-to-end.
        
        This is the main entry point for JING. It takes the technician's
        input (image + voice/text) and returns a complete diagnostic with
        repair procedure, tools, parts, and voice response.
        
        Args:
            image_source: Image URL, file path, or bytes (optional but recommended)
            voice_text: Voice description or text description of the problem
            additional_context: Any extra context (location, time, history, etc.)
        
        Returns:
            Complete response dictionary with:
            - execution_summary: Timing, costs, success/failure counts
            - plan: The execution plan from JING-MASTER
            - consolidated_response: Unified response for the technician
            - agent_results: Detailed results from each agent
            - voice_response: Spoken response from JING-VOICE
            - errors: Any errors that occurred
        
        Raises:
            ValueError: If neither image nor voice is provided
            RuntimeError: If critical agents fail
        
        Example:
            >>> result = await orchestrator.process(
            ...     image_source="data/images/faucet.jpg",
            ...     voice_text="This Moen is dripping"
            ... )
            >>> print(result["consolidated_response"]["diagnosis"])
        """
        # ═══════════════════════════════════════════════════════════
        # VALIDATE INPUTS
        # ═══════════════════════════════════════════════════════════
        
        if not image_source and not voice_text:
            raise ValueError("At least one of image_source or voice_text must be provided")
        
        logger.info("="*70)
        logger.info("JING ORCHESTRATOR: Starting new request")
        logger.info("="*70)
        logger.info(f"  Image: {'Yes' if image_source else 'No'}")
        logger.info(f"  Voice: {'Yes' if voice_text else 'No'}")
        logger.info(f"  Additional context: {len(additional_context or {})} fields")
        
        start_time = time.time()
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 1: PLANNING (JING-MASTER)
        # ═══════════════════════════════════════════════════════════
        
        logger.info("\n[PHASE 1] JING-MASTER: Creating execution plan...")
        phase1_start = time.time()
        
        try:
            # Convert image_source to string for MASTER
            image_url = None
            if image_source:
                if isinstance(image_source, Path):
                    image_url = str(image_source)
                elif isinstance(image_source, bytes):
                    raise ValueError(
                        "Image bytes not supported yet. Use file path or URL."
                    )
                else:
                    image_url = str(image_source)
            
            plan = await self.master.plan(
                image_url=image_url,
                voice_text=voice_text,
                additional_context=additional_context,
            )
            
            phase1_duration = (time.time() - phase1_start) * 1000
            logger.info(f"  ✅ Plan created in {phase1_duration:.0f}ms")
            logger.info(f"  📋 Tasks: {len(plan['tasks'])}")
            logger.info(f"  ⚡ Waves: {len(plan['execution_strategy']['parallel_groups'])}")
            logger.info(f"  🎯 Urgency: {plan['request_analysis']['urgency']}")
        
        except Exception as e:
            logger.error(f"  ❌ Planning failed: {e}", exc_info=True)
            raise RuntimeError(f"JING-MASTER planning failed: {e}") from e
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 2: EXECUTION (JING-FOREMAN)
        # ═══════════════════════════════════════════════════════════
        
        logger.info("\n[PHASE 2] JING-FOREMAN: Executing plan...")
        phase2_start = time.time()
        
        try:
            execution_result = await self.foreman.execute_plan(
                plan=plan,
                image_url=image_url,
                voice_text=voice_text,
            )
            
            phase2_duration = (time.time() - phase2_start) * 1000
            logger.info(f"  ✅ Execution completed in {phase2_duration:.0f}ms")
            logger.info(f"  📊 Tasks: {execution_result['execution_summary']['successful_tasks']}/{execution_result['execution_summary']['total_tasks']} successful")
        
        except Exception as e:
            logger.error(f"  ❌ Execution failed: {e}", exc_info=True)
            raise RuntimeError(f"JING-FOREMAN execution failed: {e}") from e
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 3: STEWARD (Financial Analysis + Budget)
        # ═══════════════════════════════════════════════════════════
        
        logger.info("\n[PHASE 3] JING-STEWARD: Generating financial analysis...")
        phase3_start = time.time()
        
        steward_result = None
        try:
            # Extract EYE and KIT results for STEWARD
            eye_result = execution_result.get("agent_results", {}).get("JING-EYE", {}).get("data", {})
            kit_result = execution_result.get("agent_results", {}).get("JING-KIT", {}).get("data", {})
            consolidated = execution_result.get("consolidated_response", {})
            
            steward_result = await self.steward.generate_budget(
                diagnosis=consolidated.get("diagnosis", voice_text or "Unknown issue"),
                parts=None,
                tools=consolidated.get("key_tools", []),
                estimated_hours=1.0,
                trade="general",
                client_name=None,
                urgency=consolidated.get("severity", "normal"),
                eye_analysis=eye_result if eye_result else None,
                kit_result=kit_result if kit_result else None,
            )
            
            phase3_duration = (time.time() - phase3_start) * 1000
            logger.info(f"  ✅ Budget generated in {phase3_duration:.0f}ms")
            
        except Exception as e:
            phase3_duration = (time.time() - phase3_start) * 1000
            logger.error(f"  ❌ Steward analysis failed: {e}", exc_info=True)
            steward_result = None
        
        # ═══════════════════════════════════════════════════════════
        # PHASE 4: FINAL ASSEMBLY
        # ═══════════════════════════════════════════════════════════
        
        logger.info("\n[PHASE 4] Assembling final response...")
        
        total_duration_ms = (time.time() - start_time) * 1000
        
        # Extract voice response if available
        voice_response = None
        for task in plan["tasks"]:
            if task["agent"] == "JING-VOICE":
                task_id = task["task_id"]
                for agent_name, agent_result in execution_result.get("agent_results", {}).items():
                    if agent_name == "JING-VOICE":
                        voice_response = agent_result
                        break
        
        # Build final response
        final_response = {
            "execution_summary": {
                "total_duration_ms": total_duration_ms,
                "planning_duration_ms": phase1_duration,
                "execution_duration_ms": phase2_duration,
                "total_cost_usd": execution_result["execution_summary"]["total_cost_usd"],
                "remaining_budget_usd": self.qwen_client.get_remaining_budget(),
                "total_tasks": execution_result["execution_summary"]["total_tasks"],
                "successful_tasks": execution_result["execution_summary"]["successful_tasks"],
                "failed_tasks": execution_result["execution_summary"]["failed_tasks"],
            },
            "plan": plan,
            "consolidated_response": execution_result["consolidated_response"],
            "agent_results": execution_result["agent_results"],
            "voice_response": voice_response,
            "steward_analysis": steward_result,
            "errors": execution_result["errors"],
        }
        
        # ═══════════════════════════════════════════════════════════
        # LOGGING SUMMARY
        # ═══════════════════════════════════════════════════════════
        
        logger.info("\n" + "="*70)
        logger.info("JING ORCHESTRATOR: Request completed")
        logger.info("="*70)
        logger.info(f"  ⏱️  Total time: {total_duration_ms:.0f}ms")
        logger.info(f"  💰 Total cost: ${final_response['execution_summary']['total_cost_usd']:.4f}")
        logger.info(f"  💵 Remaining budget: ${final_response['execution_summary']['remaining_budget_usd']:.2f}")
        if steward_result:
            logger.info(f"  💼 Budget: {steward_result.get('client_friendly_total', 'N/A')}")
        logger.info(f"  ✅ Success rate: {final_response['execution_summary']['successful_tasks']}/{final_response['execution_summary']['total_tasks']}")
        
        if final_response["errors"]:
            logger.warning(f"  ⚠️  Errors: {len(final_response['errors'])}")
            for error in final_response["errors"]:
                logger.warning(f"     - {error['task_id']} ({error['agent']}): {error['error']}")
        
        logger.info("="*70 + "\n")
        
        return final_response
    
    async def process_simple(
        self,
        image_source: Optional[Union[str, Path, bytes]] = None,
        voice_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Simplified version of process() that returns only the essential info.
        
        This is useful for quick demos or when you don't need all the details.
        
        Returns:
            Simplified response with:
            - diagnosis: What's the problem
            - part_number: Critical part number (if any)
            - tools: List of key tools
            - estimated_cost: Total estimated cost
            - spoken_response: Voice response text
        """
        full_result = await self.process(
            image_source=image_source,
            voice_text=voice_text,
        )
        
        consolidated = full_result["consolidated_response"]
        voice_response = full_result.get("voice_response", {})
        
        # Extract spoken response
        spoken_text = None
        if voice_response and isinstance(voice_response, dict):
            if voice_response.get("status") == "success":
                spoken_text = voice_response.get("data", {}).get("spoken_response")
        
        return {
            "diagnosis": consolidated.get("diagnosis", "Unknown"),
            "severity": consolidated.get("severity", "unknown"),
            "part_number": consolidated.get("part_number"),
            "tools": consolidated.get("key_tools", []),
            "estimated_cost": consolidated.get("estimated_cost", "Unknown"),
            "estimated_time": consolidated.get("estimated_time", "Unknown"),
            "spoken_response": spoken_text,
            "safety_warnings": consolidated.get("safety_warnings", []),
        }
    
    async def generate_budget(
        self,
        diagnosis: str,
        parts: Optional[list[Dict[str, Any]]] = None,
        tools: Optional[list[str]] = None,
        estimated_hours: Optional[float] = None,
        trade: str = "general",
        client_name: Optional[str] = None,
        urgency: str = "normal",
    ) -> Dict[str, Any]:
        """
        Generate a professional budget using JING-STEWARD.
        
        This is a convenience method that directly calls STEWARD without
        going through the full orchestration flow.
        """
        steward = StewardAgent()
        budget = await steward.generate_budget(
            diagnosis=diagnosis,
            parts=parts,
            tools=tools,
            estimated_hours=estimated_hours,
            trade=trade,
            client_name=client_name,
            urgency=urgency,
        )
        return budget
    
    async def generate_financial_summary(
        self,
        budget: Dict[str, Any],
        actual_parts_cost: float,
        actual_hours: float,
        amount_charged: float,
        client_name: str = "Client",
        job_title: Optional[str] = None,
        extra_costs: Optional[list[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a financial summary after job completion.
        """
        steward = StewardAgent()
        summary = await steward.generate_financial_summary(
            budget=budget,
            actual_parts_cost=actual_parts_cost,
            actual_hours=actual_hours,
            amount_charged=amount_charged,
            client_name=client_name,
            job_title=job_title,
            extra_costs=extra_costs,
        )
        return summary
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the JING system.
        
        Returns:
            Status dictionary with budget info, agent availability, etc.
        """
        return {
            "status": "operational",
            "budget": {
                "total": 40.0,
                "used": self.qwen_client.get_cost_summary()["total_cost"],
                "remaining": self.qwen_client.get_remaining_budget(),
            },
            "agents": {
                "JING-MASTER": "available",
                "JING-EYE": "available",
                "JING-SCRIBE": "available",
                "JING-KIT": "available",
                "JING-VOICE": "available",
                "JING-FOREMAN": "available",
                "JING-STEWARD": "available",
            },
            "models": {
                "qwen-max": settings.QWEN_MAX_MODEL,
                "qwen-vl-max": settings.QWEN_VL_MODEL,
                "qwen-plus": settings.QWEN_PLUS_MODEL,
                "qwen-audio": settings.QWEN_AUDIO_MODEL,
            },
        }


# ═══════════════════════════════════════════════════════════════
# SINGLETON ACCESSOR
# ═══════════════════════════════════════════════════════════════

@lru_cache()
def get_orchestrator() -> JingOrchestrator:
    """Get singleton orchestrator instance."""
    return JingOrchestrator()


# ═══════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════

async def _demo():
    """Complete end-to-end demo of the JING system."""
    orchestrator = get_orchestrator()
    
    print("\n" + "="*70)
    print("JING COMPLETE WORKFLOW DEMO")
    print("="*70)
    
    # Show initial status
    status = orchestrator.get_status()
    print(f"\n📊 Initial Status:")
    print(f"   Budget remaining: ${status['budget']['remaining']:.2f}")
    print(f"   All agents: {list(status['agents'].keys())}")
    
    # ═══════════════════════════════════════════════════════════
    # SCENARIO 1: Faucet repair
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("SCENARIO 1: Kitchen Faucet Repair")
    print("-"*70)
    print("\n👨‍🔧 Technician input:")
    print("   📸 Image: data/images/kitchen_faucet.jpg")
    print("   🎤 Voice: 'This Moen faucet has been dripping since last night'")
    
    try:
        result = await orchestrator.process(
            image_source="data/images/kitchen_faucet.jpg",
            voice_text="This Moen faucet has been dripping since last night",
        )
        
        print("\n✅ JING completed analysis!")
        
        # Display consolidated response
        print("\n🎯 CONSOLIDATED RESPONSE:")
        consolidated = result["consolidated_response"]
        print(f"   🔍 Diagnosis: {consolidated['diagnosis']}")
        print(f"   📊 Severity: {consolidated['severity']}")
        print(f"   🔧 Procedure: {consolidated['procedure_summary']}")
        print(f"   🔢 Part number: {consolidated['part_number'] or 'N/A'}")
        print(f"   📖 Manual: {consolidated['manual_reference'] or 'N/A'}")
        print(f"   💰 Estimated cost: {consolidated['estimated_cost']}")
        print(f"   ⏱️  Estimated time: {consolidated['estimated_time']}")
        
        if consolidated["key_tools"]:
            print(f"   🛠️  Key tools: {', '.join(consolidated['key_tools'])}")
        
        if consolidated["safety_warnings"]:
            print(f"\n🚨 SAFETY WARNINGS:")
            for warning in consolidated["safety_warnings"]:
                print(f"   ⚠️  {warning}")
        
        # Display voice response
        if result.get("voice_response"):
            voice_data = result["voice_response"].get("data", {})
            if voice_data.get("spoken_response"):
                print(f"\n🎤 VOICE RESPONSE:")
                print(f"   \"{voice_data['spoken_response']}\"")
                print(f"   Duration: {voice_data.get('estimated_duration_seconds', '?')}s")
        
        # Display execution summary
        print(f"\n📊 EXECUTION SUMMARY:")
        summary = result["execution_summary"]
        print(f"   Total time: {summary['total_duration_ms']:.0f}ms")
        print(f"   Planning: {summary['planning_duration_ms']:.0f}ms")
        print(f"   Execution: {summary['execution_duration_ms']:.0f}ms")
        print(f"   Cost: ${summary['total_cost_usd']:.4f}")
        print(f"   Success: {summary['successful_tasks']}/{summary['total_tasks']} tasks")
        
        if result["errors"]:
            print(f"\n⚠️  ERRORS:")
            for error in result["errors"]:
                print(f"   • {error['task_id']} ({error['agent']}): {error['error']}")
        
    except Exception as e:
        print(f"\n❌ Scenario 1 failed: {e}")
        import traceback
        traceback.print_exc()
    
    # ═══════════════════════════════════════════════════════════
    # SCENARIO 2: Simple voice-only request
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "-"*70)
    print("SCENARIO 2: Voice-Only Request (No Image)")
    print("-"*70)
    print("\n👨‍🔧 Technician input:")
    print("   📸 Image: (none)")
    print("   🎤 Voice: 'Honeywell thermostat T9 won't power on'")
    
    try:
        simple_result = await orchestrator.process_simple(
            voice_text="Honeywell thermostat T9 won't power on",
        )
        
        print("\n✅ JING completed analysis!")
        
        print("\n🎯 SIMPLE RESPONSE:")
        print(f"   🔍 Diagnosis: {simple_result['diagnosis']}")
        print(f"   📊 Severity: {simple_result['severity']}")
        print(f"   🔢 Part number: {simple_result['part_number'] or 'N/A'}")
        print(f"   🛠️  Tools: {', '.join(simple_result['tools']) if simple_result['tools'] else 'N/A'}")
        print(f"   💰 Cost: {simple_result['estimated_cost']}")
        print(f"   ⏱️  Time: {simple_result['estimated_time']}")
        
        if simple_result.get("spoken_response"):
            print(f"\n🎤 VOICE: \"{simple_result['spoken_response']}\"")
        
    except Exception as e:
        print(f"\n❌ Scenario 2 failed: {e}")
        import traceback
        traceback.print_exc()
    
    # ═══════════════════════════════════════════════════════════
    # FINAL STATUS
    # ═══════════════════════════════════════════════════════════
    
    print("\n" + "="*70)
    print("FINAL STATUS")
    print("="*70)
    
    final_status = orchestrator.get_status()
    print(f"\n💰 Budget:")
    print(f"   Total: ${final_status['budget']['total']:.2f}")
    print(f"   Used: ${final_status['budget']['used']:.4f}")
    print(f"   Remaining: ${final_status['budget']['remaining']:.2f}")
    print(f"   Usage: {(final_status['budget']['used']/final_status['budget']['total']*100):.1f}%")
    
    print("\n" + "="*70)
    print("✅ JING WORKFLOW DEMO COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
