"""
JING-SCRIBE: The Documentation Specialist

JING-SCRIBE finds, retrieves, and extracts technical information from manuals,
specifications, and technical documents. It uses a hybrid approach:

1. First tries to find official manuals (via web search if available)
2. Falls back to certified technical databases
3. Uses Qwen's internal knowledge as last resort (with disclosure)

This agent is typically activated AFTER JING-EYE identifies the specific
appliance/model, so it knows exactly what to look for.

Usage:
    >>> from src.agents.scribe import ScribeAgent
    >>> scribe = ScribeAgent()
    >>> result = await scribe.find_procedure(
    ...     brand="Moen",
    ...     model="Chateau 7400",
    ...     problem="cartridge failure causing drip"
    ... )
    >>> print(result["repair_procedure"])
"""

import json
from typing import Any, Dict, Optional

from src.agents.base_agent import BaseAgent, AgentExecutionError, AgentValidationError
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScribeAgent(BaseAgent):
    """
    JING-SCRIBE: Documentation specialist for technical procedures.
    
    Uses a hybrid approach:
    - Qwen's internal knowledge (always available)
    - Web search (if Tavily API key is configured)
    - Vector DB / RAG (if configured - for post-hackathon)
    """
    
    def __init__(self, web_search_enabled: bool = False):
        """
        Initialize JING-SCRIBE.
        
        Args:
            web_search_enabled: Enable web search for finding manuals online.
                               Requires TAVILY_API_KEY in .env
        """
        super().__init__(name="JING-SCRIBE")
        self.web_search_enabled = web_search_enabled
        
        # Check for Tavily API key
        if web_search_enabled:
            try:
                from src.utils.config import settings
                if hasattr(settings, 'TAVILY_API_KEY') and settings.TAVILY_API_KEY:
                    logger.info("JING-SCRIBE initialized with web search enabled")
                else:
                    logger.warning(
                        "Web search requested but TAVILY_API_KEY not set. "
                        "Falling back to internal knowledge only."
                    )
                    self.web_search_enabled = False
            except Exception:
                self.web_search_enabled = False
        
        if not self.web_search_enabled:
            logger.info("JING-SCRIBE initialized (internal knowledge only)")
    
    def _get_default_model(self) -> str:
        """SCRIBE uses qwen-plus (good balance of cost and quality)."""
        return settings.QWEN_PLUS_MODEL
    
    async def find_procedure(
        self,
        brand: str,
        model: str,
        problem: str,
        object_type: Optional[str] = None,
        eye_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Find the repair procedure for a specific problem.
        
        Args:
            brand: Brand name (e.g., "Moen", "Honeywell")
            model: Model number/name (e.g., "Chateau 7400", "T9")
            problem: Description of the problem
            object_type: Type of object (faucet, thermostat, etc.)
            eye_analysis: Full analysis from JING-EYE (optional context)
        
        Returns:
            Structured procedure with steps, tools, specs, and warnings
        
        Raises:
            AgentValidationError: If inputs are invalid
            AgentExecutionError: If retrieval fails
        """
        # ═══════════════════════════════════════════════════════════
        # VALIDATE INPUTS
        # ═══════════════════════════════════════════════════════════
        
        if not brand or not model:
            raise AgentValidationError("Brand and model are required")
        
        if not problem:
            raise AgentValidationError("Problem description is required")
        
        logger.info(f"JING-SCRIBE finding procedure for: {brand} {model} - {problem}")
        
        # ═══════════════════════════════════════════════════════════
        # STEP 1: WEB SEARCH (if enabled)
        # ═══════════════════════════════════════════════════════════
        
        web_context = ""
        if self.web_search_enabled:
            try:
                web_context = await self._search_for_manual(brand, model, problem)
                logger.info(f"Web search returned {len(web_context)} chars of context")
            except Exception as e:
                logger.warning(f"Web search failed, falling back to internal knowledge: {e}")
                web_context = ""
        
        # ═══════════════════════════════════════════════════════════
        # STEP 2: BUILD PROMPT WITH ALL CONTEXT
        # ═══════════════════════════════════════════════════════════
        
        prompt = self._build_procedure_prompt(
            brand=brand,
            model=model,
            problem=problem,
            object_type=object_type,
            eye_analysis=eye_analysis,
            web_context=web_context,
        )
        
        # ═══════════════════════════════════════════════════════════
        # STEP 3: CALL QWEN
        # ═══════════════════════════════════════════════════════════
        
        try:
            response_text = await self.call_qwen(
                user_message=prompt,
                temperature=0.2,
                max_tokens=2500,
            )
        except Exception as e:
            logger.error(f"JING-SCRIBE procedure retrieval failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Procedure retrieval failed: {e}") from e
        
        # ═══════════════════════════════════════════════════════════
        # STEP 4: PARSE AND VALIDATE
        # ═══════════════════════════════════════════════════════════
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JING-SCRIBE returned invalid JSON: {response_text[:200]}...")
            raise AgentExecutionError(f"Invalid JSON from SCRIBE: {e}") from e
        
        validated_result = self._validate_procedure(result)
        
        logger.info(
            f"JING-SCRIBE found procedure: "
            f"manual_found={validated_result['manual_found']['found']}, "
            f"source={validated_result['manual_found']['source']}, "
            f"steps={len(validated_result['repair_procedure'])}"
        )
        
        return validated_result
    
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute method required by BaseAgent. Delegates to find_procedure()."""
        return await self.find_procedure(
            brand=task_input.get("brand", ""),
            model=task_input.get("model", ""),
            problem=task_input.get("problem", ""),
            object_type=task_input.get("object_type"),
            eye_analysis=task_input.get("eye_analysis"),
        )
    
    async def _search_for_manual(
        self,
        brand: str,
        model: str,
        problem: str,
    ) -> str:
        """
        Search the web for the official manual.
        
        Uses Tavily API if available. Returns a summary of findings.
        """
        try:
            from tavily import AsyncTavilyClient
            
            if not hasattr(settings, 'TAVILY_API_KEY') or not settings.TAVILY_API_KEY:
                return ""
            
            client = AsyncTavilyClient(api_key=settings.TAVILY_API_KEY)
            
            query = f"{brand} {model} official repair manual service guide {problem}"
            
            logger.debug(f"Tavily search: {query}")
            
            response = await client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_answer=True,
            )
            
            context_parts = ["═══ WEB SEARCH RESULTS ═══\n"]
            
            if response.get("answer"):
                context_parts.append(f"SUMMARY: {response['answer']}\n")
            
            for i, result in enumerate(response.get("results", []), 1):
                context_parts.append(f"\n--- Source {i} ---")
                context_parts.append(f"Title: {result.get('title', 'N/A')}")
                context_parts.append(f"URL: {result.get('url', 'N/A')}")
                context_parts.append(f"Content: {result.get('content', '')[:500]}")
            
            return "\n".join(context_parts)
        
        except ImportError:
            logger.debug("Tavily not installed, skipping web search")
            return ""
        except Exception as e:
            logger.warning(f"Web search error: {e}")
            return ""
    
    def _build_procedure_prompt(
        self,
        brand: str,
        model: str,
        problem: str,
        object_type: Optional[str],
        eye_analysis: Optional[Dict[str, Any]],
        web_context: str,
    ) -> str:
        """Build the prompt for procedure retrieval."""
        parts = ["═══ PROCEDURE RETRIEVAL REQUEST ═══\n"]
        
        parts.append(f"🏷️  BRAND: {brand}")
        parts.append(f"📋 MODEL: {model}")
        
        if object_type:
            parts.append(f"🔧 OBJECT TYPE: {object_type}")
        
        parts.append(f"\n⚠️  PROBLEM: {problem}")
        
        if eye_analysis:
            parts.append(f"\n👁️  JING-EYE ANALYSIS:")
            parts.append(f"   Object: {eye_analysis.get('object_identification', {}).get('object', 'N/A')}")
            parts.append(f"   Severity: {eye_analysis.get('overall_severity', 'N/A')}")
            parts.append(f"   Probable cause: {eye_analysis.get('probable_cause', 'N/A')}")
        
        if web_context:
            parts.append(f"\n{web_context}")
        else:
            parts.append("\n📚 WEB SEARCH: Not available. Use your internal knowledge.")
            parts.append("IMPORTANT: Disclose clearly that you're using internal knowledge, not an official manual.")
        
        parts.append("\n══════════════════════════════════")
        parts.append("\nFind and provide the repair procedure in JSON format.")
        parts.append("Follow your system prompt framework exactly.")
        parts.append("If you cannot find the official manual, state it clearly and use your best knowledge.")
        
        return "\n".join(parts)
    
    def _validate_procedure(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the procedure has the required structure."""
        required_keys = ["manual_found", "repair_procedure", "knowledge_disclosure"]
        for key in required_keys:
            if key not in result:
                raise AgentValidationError(f"Procedure missing required key: {key}")
        
        mf = result["manual_found"]
        if not isinstance(mf, dict):
            raise AgentValidationError("manual_found must be a dictionary")
        
        if "found" not in mf or "source" not in mf:
            raise AgentValidationError("manual_found missing 'found' or 'source'")
        
        valid_sources = {"official_manual", "certified_database", "internal_knowledge", "web_search"}
        if mf["source"] not in valid_sources:
            raise AgentValidationError(f"Invalid source: {mf['source']}. Must be one of: {valid_sources}")
        
        rp = result["repair_procedure"]
        if not isinstance(rp, list):
            raise AgentValidationError("repair_procedure must be a list")
        
        if len(rp) == 0:
            raise AgentValidationError("repair_procedure cannot be empty")
        
        for i, step in enumerate(rp):
            if not isinstance(step, dict):
                raise AgentValidationError(f"Step {i} must be a dictionary")
            if "step_number" not in step or "action" not in step:
                raise AgentValidationError(f"Step {i} missing step_number or action")
        
        if "technical_specifications" not in result:
            result["technical_specifications"] = {}
        
        if "special_tools" not in result:
            result["special_tools"] = []
        
        if "safety_warnings" not in result:
            result["safety_warnings"] = []
        
        if "common_mistakes" not in result:
            result["common_mistakes"] = []
        
        if "estimated_time" not in result:
            result["estimated_time"] = "Unknown"
        
        if "difficulty_level" not in result:
            result["difficulty_level"] = "intermediate"
        
        logger.debug("Procedure validated successfully")
        
        return result
    
    def get_summary(self, procedure: Dict[str, Any]) -> str:
        """Get a human-readable summary of the procedure."""
        mf = procedure["manual_found"]
        
        summary_parts = []
        
        if mf["found"]:
            summary_parts.append(f"Manual: {mf['title']}")
            summary_parts.append(f"Source: {mf['source']}")
        else:
            summary_parts.append("No official manual found")
            summary_parts.append("Using internal knowledge")
        
        summary_parts.append(f"Steps: {len(procedure['repair_procedure'])}")
        summary_parts.append(f"Time: {procedure.get('estimated_time', 'Unknown')}")
        summary_parts.append(f"Difficulty: {procedure.get('difficulty_level', 'Unknown')}")
        
        if procedure["safety_warnings"]:
            summary_parts.append(f"Safety warnings: {len(procedure['safety_warnings'])}")
        
        return " | ".join(summary_parts)


async def _demo():
    """Demo JING-SCRIBE with a realistic scenario."""
    scribe = ScribeAgent(web_search_enabled=False)
    
    print("\n" + "="*70)
    print("JING-SCRIBE Documentation Demo")
    print("="*70)
    
    print("\n📋 Scenario: Moen Chateau 7400 faucet with cartridge failure")
    
    try:
        result = await scribe.find_procedure(
            brand="Moen",
            model="Chateau 7400",
            problem="cartridge failure causing drip from spout",
            object_type="kitchen faucet",
            eye_analysis={
                "object_identification": {
                    "object": "Kitchen faucet",
                    "brand": "Moen",
                    "model": "Chateau 7400"
                },
                "overall_severity": "moderate",
                "probable_cause": "Worn cartridge allowing water to bypass valve seal"
            }
        )
        
        print("\n✅ Procedure retrieved successfully!")
        
        print(f"\n📖 Manual Found:")
        mf = result["manual_found"]
        print(f"   Found: {mf['found']}")
        if mf["found"]:
            print(f"   Title: {mf.get('title', 'N/A')}")
            print(f"   Manufacturer: {mf.get('manufacturer', 'N/A')}")
            print(f"   Source: {mf['source']}")
            if mf.get("url"):
                print(f"   URL: {mf['url']}")
        
        if result.get("relevant_section"):
            print(f"\n📑 Relevant Section:")
            rs = result["relevant_section"]
            print(f"   Section: {rs.get('section_name', 'N/A')}")
            print(f"   Page: {rs.get('page_reference', 'N/A')}")
        
        print(f"\n🔧 Repair Procedure ({len(result['repair_procedure'])} steps):")
        for step in result["repair_procedure"]:
            print(f"   {step['step_number']}. {step['action']}")
            if step.get("details"):
                print(f"      {step['details']}")
            if step.get("warnings"):
                for warning in step["warnings"]:
                    print(f"      ⚠️  {warning}")
            if step.get("tools_needed"):
                print(f"      🔧 Tools: {', '.join(step['tools_needed'])}")
        
        if result["special_tools"]:
            print(f"\n🛠️  Special Tools:")
            for tool in result["special_tools"]:
                print(f"   • {tool['tool_name']}")
                if tool.get("part_number"):
                    print(f"     Part #: {tool['part_number']}")
                if tool.get("alternative"):
                    print(f"     Alternative: {tool['alternative']}")
        
        if result["safety_warnings"]:
            print(f"\n🚨 Safety Warnings:")
            for warning in result["safety_warnings"]:
                print(f"   [{warning['severity'].upper()}] {warning['warning']}")
        
        if result["common_mistakes"]:
            print(f"\n⚠️  Common Mistakes:")
            for mistake in result["common_mistakes"]:
                print(f"   • {mistake}")
        
        print(f"\n⏱️  Estimated Time: {result.get('estimated_time', 'Unknown')}")
        print(f"📊 Difficulty: {result.get('difficulty_level', 'Unknown')}")
        print(f"\n📝 Knowledge Disclosure: {result['knowledge_disclosure']}")
        
        print(f"\n📋 Summary: {scribe.get_summary(result)}")
        
        from src.services.qwen_client import get_qwen_client
        client = get_qwen_client()
        summary = client.get_cost_summary()
        print(f"\n💰 Cost: ${summary['total_cost']:.4f}")
        print(f"   Remaining budget: ${summary['remaining_budget']:.2f}")
        
    except Exception as e:
        print(f"\n❌ Procedure retrieval failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
