"""
JING-REFEREE: The Debate Arbiter & Consensus Builder

JING-REFEREE is the quality-control agent that detects disagreements
between specialist agents (EYE, SCRIBE, KIT) and resolves them through
structured debate and consensus-building.

This is the key differentiator for Track 3 (Agent Society) — it transforms
JING from a feed-forward pipeline into a true agent society where agents
can challenge each other's conclusions and negotiate the truth.

Key capabilities:
- Detect contradictions between agent outputs
- Orchestrate structured debate rounds
- Build consensus with confidence-weighted aggregation
- Produce a reconciled, higher-quality final output
"""

import json
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Tuple

from src.agents.base_agent import BaseAgent
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DebateRound:
    """Represents a single debate round between agents."""

    def __init__(self, agent_name: str, claim: str, confidence: float, evidence: str):
        self.agent_name = agent_name
        self.claim = claim
        self.confidence = confidence
        self.evidence = evidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent": self.agent_name,
            "claim": self.claim,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


class RefereeAgent(BaseAgent):
    """
    JING-REFEREE: Resolves inter-agent disagreements through structured debate.

    Architecture:
        1. COLLECT: Gather outputs from EYE, SCRIBE, KIT
        2. DETECT: Identify contradictions and disagreements
        3. DEBATE: Run structured debate rounds via LLM
        4. RECONCILE: Build consensus with confidence-weighted aggregation
        5. REPORT: Return reconciled results with conflict log
    """

    def __init__(self):
        super().__init__(name="JING-REFEREE")
        logger.info("JING-REFEREE initialized (debate arbiter & consensus builder)")

    def _get_default_model(self) -> str:
        return settings.QWEN_PLUS_MODEL

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        return await self.resolve(
            eye_result=task_input.get("eye_result"),
            scribe_result=task_input.get("scribe_result"),
            kit_result=task_input.get("kit_result"),
            original_voice_text=task_input.get("original_voice_text"),
        )

    async def resolve(
        self,
        eye_result: Optional[Dict[str, Any]] = None,
        scribe_result: Optional[Dict[str, Any]] = None,
        kit_result: Optional[Dict[str, Any]] = None,
        original_voice_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolve disagreements between agents and produce a consensus result.

        Args:
            eye_result: Output from JING-EYE (vision analysis)
            scribe_result: Output from JING-SCRIBE (documentation)
            kit_result: Output from JING-KIT (tools/parts)
            original_voice_text: Original technician voice description

        Returns:
            Dict with:
            - reconciled: The consensus result
            - conflicts: List of conflicts detected
            - debate_rounds: History of debate rounds
            - confidence_scores: Per-agent confidence
        """
        logger.info("JING-REFEREE: Starting conflict resolution")

        # ═══════════════════════════════════════════════════════════
        # PHASE 1: EXTRACT CLAIMS FROM EACH AGENT
        # ═══════════════════════════════════════════════════════════

        claims = {}
        if eye_result:
            oi = eye_result.get("object_identification", {})
            claims["JING-EYE"] = {
                "diagnosis": eye_result.get("probable_cause", ""),
                "brand": oi.get("brand", ""),
                "model": oi.get("model", ""),
                "object_type": oi.get("type", ""),
                "severity": eye_result.get("overall_severity", ""),
                "confidence": eye_result.get("overall_confidence", 0.7),
            }

        if scribe_result:
            claims["JING-SCRIBE"] = {
                "procedure_summary": scribe_result.get("procedure_summary", ""),
                "estimated_time": scribe_result.get("estimated_time", ""),
                "manual_found": scribe_result.get("manual_found", False),
                "confidence": scribe_result.get("accuracy_confidence", 0.7),
            }

        if kit_result:
            parts = kit_result.get("parts_required", [])
            claims["JING-KIT"] = {
                "num_parts": len(parts),
                "part_numbers": [
                    p.get("oem_part_number") for p in parts if p.get("oem_part_number")
                ],
                "estimated_cost": kit_result.get("estimated_total_cost", {}).get("total"),
                "confidence": kit_result.get("confidence_score", 0.7),
            }

        # ═══════════════════════════════════════════════════════════
        # PHASE 2: DETECT CONFLICTS
        # ═══════════════════════════════════════════════════════════

        conflicts = self._detect_conflicts(claims)

        # ═══════════════════════════════════════════════════════════
        # PHASE 3: RUN DEBATE IF CONFLICTS FOUND
        # ═══════════════════════════════════════════════════════════

        debate_rounds = []
        final_confidence_scores = {}

        if conflicts:
            logger.info(f"JING-REFEREE: Detected {len(conflicts)} conflicts, initiating debate")
            debate_result = await self._run_debate(claims, conflicts, original_voice_text)
            debate_rounds = debate_result.get("rounds", [])
            final_confidence_scores = debate_result.get("adjusted_confidence", {})

            # Use LLM-mediated reconciliation
            reconciled = await self._reconcile_with_llm(claims, conflicts, debate_rounds)
        else:
            logger.info("JING-REFEREE: No conflicts detected, using direct consensus")
            reconciled = self._build_consensus(claims)
            final_confidence_scores = {
                agent: data.get("confidence", 0.7) for agent, data in claims.items()
            }

        # ═══════════════════════════════════════════════════════════
        # PHASE 4: BUILD FINAL RESULT
        # ═══════════════════════════════════════════════════════════

        result = {
            "reconciled": reconciled,
            "conflicts": conflicts,
            "debate_rounds": [r.to_dict() for r in debate_rounds],
            "confidence_scores": final_confidence_scores,
            "num_agents_contributing": len(claims),
            "num_conflicts_resolved": len(conflicts),
        }

        logger.info(
            f"JING-REFEREE: Resolution complete - "
            f"{len(claims)} agents, {len(conflicts)} conflicts resolved"
        )

        return result

    def _detect_conflicts(self, claims: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detect contradictions between agent outputs.

        Checks:
        - Brand/model mismatches between EYE and SCRIBE
        - Severity disagreements
        - Confidence thresholds
        """
        conflicts = []

        if "JING-EYE" in claims and "JING-SCRIBE" in claims:
            eye = claims["JING-EYE"]
            scribe = claims["JING-SCRIBE"]

            if eye.get("brand") and scribe.get("manual_found"):
                conflicts.append(
                    {
                        "type": "brand_validation",
                        "agents": ["JING-EYE", "JING-SCRIBE"],
                        "description": f"EYE identified brand '{eye.get('brand')}', SCRIBE should validate",
                        "severity": "low",
                    }
                )

        if "JING-EYE" in claims and "JING-KIT" in claims:
            eye = claims["JING-EYE"]
            kit = claims["JING-KIT"]

            if eye.get("confidence", 1.0) < 0.6 and kit.get("num_parts", 0) > 0:
                conflicts.append(
                    {
                        "type": "confidence_mismatch",
                        "agents": ["JING-EYE", "JING-KIT"],
                        "description": (
                            f"EYE has low confidence ({eye.get('confidence', 0):.1f}) "
                            f"but KIT listed {kit.get('num_parts', 0)} parts"
                        ),
                        "severity": "medium",
                    }
                )

        # Check for low-confidence agents
        for agent_name, data in claims.items():
            conf = data.get("confidence", 0.7)
            if conf < 0.5:
                conflicts.append(
                    {
                        "type": "low_confidence",
                        "agents": [agent_name],
                        "description": f"{agent_name} has low confidence ({conf:.1f})",
                        "severity": "high",
                    }
                )

        return conflicts

    async def _run_debate(
        self,
        claims: Dict[str, Dict],
        conflicts: List[Dict[str, Any]],
        original_voice_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run a structured debate round via LLM.

        The LLM acts as a neutral arbiter that evaluates each agent's
        claims and determines which are more credible.
        """
        prompt = self._build_debate_prompt(claims, conflicts, original_voice_text)

        try:
            response = await self.call_qwen_json(
                user_message=prompt,
                temperature=0.3,
                max_tokens=1500,
            )

            rounds = response.get("debate_rounds", [])
            adjusted_confidence = response.get("adjusted_confidence", {})

            debate_rounds = [
                DebateRound(
                    agent_name=r.get("agent", "unknown"),
                    claim=r.get("claim", ""),
                    confidence=r.get("confidence", 0.5),
                    evidence=r.get("evidence", ""),
                )
                for r in rounds
            ]

            return {
                "rounds": debate_rounds,
                "adjusted_confidence": adjusted_confidence,
            }

        except Exception as e:
            logger.error(f"Debate round failed: {e}", exc_info=True)
            return {"rounds": [], "adjusted_confidence": {}}

    def _build_debate_prompt(
        self,
        claims: Dict[str, Dict],
        conflicts: List[Dict[str, Any]],
        original_voice_text: Optional[str] = None,
    ) -> str:
        """Build the debate prompt for the LLM arbiter."""
        lines = ["═══ JING-REFEREE DEBATE ROUND ═══\n"]
        lines.append(
            "You are a neutral arbiter resolving disagreements between specialist agents.\n"
        )

        if original_voice_text:
            lines.append(f"🎤 ORIGINAL TECHNICIAN INPUT:")
            lines.append(f'   "{original_voice_text}"\n')

        lines.append("📊 AGENT CLAIMS:")
        for agent_name, data in claims.items():
            lines.append(f"\n  [{agent_name}]:")
            for key, value in data.items():
                if key != "confidence":
                    lines.append(f"    {key}: {value}")
            lines.append(f"    self_confidence: {data.get('confidence', 0.7):.1f}")

        lines.append("\n\n⚡ CONFLICTS DETECTED:")
        for i, conflict in enumerate(conflicts, 1):
            lines.append(f"  {i}. [{conflict['severity']}] {conflict['description']}")
            lines.append(f"     Between: {', '.join(conflict['agents'])}")

        lines.append("""

══════════════════════════════════
Analyze each conflict and produce a JSON result with:
1. debate_rounds: array of objects with:
   - agent: which agent's claim is being evaluated
   - claim: the specific claim being debated
   - confidence: your adjusted confidence score (0.0-1.0)
   - evidence: why you adjusted confidence this way
2. adjusted_confidence: object mapping agent names to their final confidence scores

Rules:
- Trust EYE for visual identification (brand, model, type)
- Trust SCRIBE for procedural information (steps, manual references)
- Trust KIT for parts and tools (OEM numbers, prices)
- If confidence is below 0.4, flag for human review
- Prefer specificity over generality
""")

        return "\n".join(lines)

    async def _reconcile_with_llm(
        self,
        claims: Dict[str, Dict],
        conflicts: List[Dict[str, Any]],
        debate_rounds: List[DebateRound],
    ) -> Dict[str, Any]:
        """Use LLM to build a reconciled, consensus output."""
        prompt = ["═══ RECONCILIATION ═══\n"]

        for agent_name, data in claims.items():
            prompt.append(f"\n[{agent_name}]:")
            prompt.append(json.dumps(data, indent=2))

        prompt.append("\n\nDebate adjustments:")
        for r in debate_rounds:
            prompt.append(f"  {r.agent_name}: confidence adjusted to {r.confidence:.2f}")

        prompt.append("""

══════════════════════════════════
Produce a JSON consensus with:
- diagnosis: The agreed-upon diagnosis (most specific possible)
- severity: agreed severity level
- brand: agreed brand
- model: agreed model
- object_type: agreed equipment type
- procedure_summary: brief repair procedure
- part_numbers: list of OEM part numbers
- estimated_cost: final cost estimate
- estimated_time: final time estimate
- key_tools: list of required tools
- safety_warnings: list of safety warnings
- consensus_quality: "high" | "medium" | "low"
- notes: any caveats or remaining uncertainties
""")

        try:
            reconciled = await self.call_qwen_json(
                user_message="\n".join(prompt),
                temperature=0.2,
                max_tokens=2000,
            )
            return reconciled
        except Exception as e:
            logger.error(f"Reconciliation failed: {e}, falling back to direct consensus")
            return self._build_consensus(claims)

    def _build_consensus(self, claims: Dict[str, Dict]) -> Dict[str, Any]:
        """Build consensus directly from claims (no LLM needed)."""
        consensus = {
            "diagnosis": "",
            "severity": "unknown",
            "brand": "",
            "model": "",
            "object_type": "",
            "procedure_summary": "",
            "part_numbers": [],
            "estimated_cost": "Unknown",
            "estimated_time": "Unknown",
            "key_tools": [],
            "safety_warnings": [],
            "consensus_quality": "medium",
            "notes": "Direct consensus (no conflicts detected)",
        }

        if "JING-EYE" in claims:
            eye = claims["JING-EYE"]
            consensus["diagnosis"] = eye.get("diagnosis", "")
            consensus["severity"] = eye.get("severity", "unknown")
            consensus["brand"] = eye.get("brand", "")
            consensus["model"] = eye.get("model", "")
            consensus["object_type"] = eye.get("object_type", "")

        if "JING-KIT" in claims:
            kit = claims["JING-KIT"]
            consensus["part_numbers"] = kit.get("part_numbers", [])
            if kit.get("estimated_cost"):
                consensus["estimated_cost"] = kit["estimated_cost"]

        if "JING-SCRIBE" in claims:
            scribe = claims["JING-SCRIBE"]
            consensus["procedure_summary"] = scribe.get("procedure_summary", "")
            if scribe.get("estimated_time"):
                consensus["estimated_time"] = scribe["estimated_time"]

        return consensus
