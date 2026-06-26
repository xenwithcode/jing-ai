"""
JING-EYE: The Vision Specialist

JING-EYE analyzes images and videos sent by field technicians to diagnose
technical problems. It uses Qwen-VL-Max (vision-language model) to:
- Identify appliances, devices, and mechanical components
- Detect visible damage, leaks, wear, misalignments
- Read brand names, model numbers, and serial plates
- Estimate problem severity from visual cues
- Identify safety hazards

This is typically the FIRST agent activated in a JING workflow, as most
technician requests include an image of the problem.

Usage:
    >>> from src.agents.eye import EyeAgent
    >>> eye = EyeAgent()
    >>> result = await eye.analyze(
    ...     image_source="data/images/leaking_faucet.jpg",
    ...     context="Technician says this Moen faucet is dripping"
    ... )
    >>> print(result["object_identification"]["brand"])
    'Moen'
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

from src.agents.base_agent import BaseAgent, AgentExecutionError, AgentValidationError
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EyeAgent(BaseAgent):
    """
    JING-EYE: Vision specialist for technical problem diagnosis.

    This agent uses Qwen-VL-Max to analyze images and provide structured
    diagnostic information that other agents (SCRIBE, KIT) can use.
    """

    def __init__(self):
        """Initialize JING-EYE with qwen-vl-max model."""
        super().__init__(name="JING-EYE")
        logger.info("JING-EYE initialized (vision specialist)")

    def _get_default_model(self) -> str:
        """EYE uses the vision model."""
        return settings.QWEN_VL_MODEL

    async def analyze(
        self,
        image_source: Union[str, Path, bytes],
        context: Optional[str] = None,
        technician_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze an image to diagnose a technical problem.

        Args:
            image_source: URL, file path, or raw bytes of the image
            context: Additional context about the problem (e.g., technician's description)
            technician_notes: Any specific questions or notes from the technician

        Returns:
            Structured diagnostic result with:
            - object_identification
            - problem_detected
            - overall_severity
            - probable_cause
            - safety_warnings
            - confidence
            - limitations
            - recommendations

        Raises:
            AgentValidationError: If image is invalid
            AgentExecutionError: If analysis fails
        """
        # ═══════════════════════════════════════════════════════════
        # VALIDATE IMAGE SOURCE
        # ═══════════════════════════════════════════════════════════

        if isinstance(image_source, (str, Path)):
            path = Path(image_source)
            if path.exists() and not path.is_file():
                raise AgentValidationError(f"Image source is not a file: {path}")

            if path.exists():
                # Check file size (max 10MB)
                size_mb = path.stat().st_size / (1024 * 1024)
                if size_mb > settings.MAX_UPLOAD_SIZE_MB:
                    raise AgentValidationError(
                        f"Image too large: {size_mb:.2f}MB > {settings.MAX_UPLOAD_SIZE_MB}MB"
                    )

                # Check file extension
                valid_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
                if path.suffix.lower() not in valid_extensions:
                    raise AgentValidationError(
                        f"Invalid image format: {path.suffix}. "
                        f"Supported: {', '.join(valid_extensions)}"
                    )

        logger.info(f"JING-EYE analyzing image: {image_source}")

        # ═══════════════════════════════════════════════════════════
        # BUILD THE PROMPT
        # ═══════════════════════════════════════════════════════════

        prompt = self._build_analysis_prompt(
            context=context,
            technician_notes=technician_notes,
        )

        # ═══════════════════════════════════════════════════════════
        # CALL QWEN VISION API
        # ═══════════════════════════════════════════════════════════

        try:
            response_text = await self.call_qwen_vision(
                prompt=prompt,
                image_source=image_source,
                temperature=0.3,
                max_tokens=1500,
            )
        except Exception as e:
            logger.error(f"JING-EYE vision analysis failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Vision analysis failed: {e}") from e

        # ═══════════════════════════════════════════════════════════
        # PARSE AND VALIDATE RESPONSE
        # ═══════════════════════════════════════════════════════════

        try:
            import json
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JING-EYE returned invalid JSON: {response_text[:200]}...")
            raise AgentExecutionError(f"Invalid JSON from EYE: {e}") from e

        validated_result = self._validate_analysis(result)

        logger.info(
            f"JING-EYE analysis complete: "
            f"{validated_result['object_identification']['object']} - "
            f"severity: {validated_result['overall_severity']}, "
            f"confidence: {validated_result['confidence']['level']}"
        )

        return validated_result

    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute method required by BaseAgent.

        Delegates to analyze() method.
        """
        return await self.analyze(
            image_source=task_input.get("image_source"),
            context=task_input.get("context"),
            technician_notes=task_input.get("technician_notes"),
        )

    def _build_analysis_prompt(
        self,
        context: Optional[str],
        technician_notes: Optional[str],
    ) -> str:
        """Build the prompt for image analysis."""
        parts = ["══════ IMAGE ANALYSIS REQUEST ══════\n"]

        if context:
            parts.append(f"📝 CONTEXT: {context}")
        else:
            parts.append("📝 CONTEXT: (none provided - analyze image only)")

        if technician_notes:
            parts.append(f"\n🔧 TECHNICIAN NOTES: {technician_notes}")

        parts.append("\n══════════════════════════════════")
        parts.append("\nAnalyze this image and provide a structured diagnostic in JSON format.")
        parts.append("Follow your system prompt framework exactly.")

        return "\n".join(parts)

    def _validate_analysis(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that the analysis has the required structure.

        Args:
            result: The raw analysis dictionary from Qwen

        Returns:
            The validated analysis

        Raises:
            AgentValidationError: If the analysis is missing required fields
        """
        required_keys = [
            "object_identification",
            "problem_detected",
            "overall_severity",
            "probable_cause",
            "confidence",
        ]

        for key in required_keys:
            if key not in result:
                raise AgentValidationError(f"Analysis missing required key: {key}")

        oi = result["object_identification"]
        if not isinstance(oi, dict):
            raise AgentValidationError("object_identification must be a dictionary")
        if "object" not in oi:
            raise AgentValidationError("object_identification missing 'object'")

        pd = result["problem_detected"]
        if not isinstance(pd, dict):
            raise AgentValidationError("problem_detected must be a dictionary")

        if result["overall_severity"] not in ["minor", "moderate", "critical"]:
            raise AgentValidationError(
                f"Invalid overall_severity: {result['overall_severity']}"
            )

        conf = result["confidence"]
        if not isinstance(conf, dict):
            raise AgentValidationError("confidence must be a dictionary")
        if "level" not in conf or "score" not in conf:
            raise AgentValidationError("confidence missing 'level' or 'score'")
        if conf["level"] not in ["high", "medium", "low"]:
            raise AgentValidationError(f"Invalid confidence level: {conf['level']}")
        if not isinstance(conf["score"], (int, float)) or not (0 <= conf["score"] <= 1):
            raise AgentValidationError(f"Invalid confidence score: {conf['score']}")

        if "safety_warnings" not in result:
            result["safety_warnings"] = []
        elif not isinstance(result["safety_warnings"], list):
            result["safety_warnings"] = [result["safety_warnings"]]

        if "limitations" not in result:
            result["limitations"] = []
        elif not isinstance(result["limitations"], list):
            result["limitations"] = [result["limitations"]]

        if "recommendations" not in result:
            result["recommendations"] = []
        elif not isinstance(result["recommendations"], list):
            result["recommendations"] = [result["recommendations"]]

        if "alternative_causes" not in result:
            result["alternative_causes"] = []
        elif not isinstance(result["alternative_causes"], list):
            result["alternative_causes"] = [result["alternative_causes"]]

        logger.debug("Analysis validated successfully")
        return result

    def get_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the analysis.

        Args:
            analysis: The validated analysis result

        Returns:
            A concise summary string
        """
        oi = analysis["object_identification"]
        pd = analysis["problem_detected"]
        conf = analysis["confidence"]

        summary_parts = [f"Object: {oi['object']}"]
        if oi.get("brand"):
            summary_parts.append(f"Brand: {oi['brand']}")
        if oi.get("model"):
            summary_parts.append(f"Model: {oi['model']}")
        summary_parts.append(f"Problem: {pd['description']}")
        summary_parts.append(f"Severity: {analysis['overall_severity']}")
        summary_parts.append(f"Cause: {analysis['probable_cause']}")
        summary_parts.append(f"Confidence: {conf['level']} ({conf['score']:.2f})")
        if analysis["safety_warnings"]:
            summary_parts.append(f"Safety warnings: {len(analysis['safety_warnings'])}")

        return " | ".join(summary_parts)


async def _demo():
    """Demo JING-EYE with a realistic scenario."""
    eye = EyeAgent()

    print("\n" + "="*70)
    print("JING-EYE Vision Analysis Demo")
    print("="*70)

    test_image_path = Path("data/images/leaking_faucet.jpg")

    if not test_image_path.exists():
        print(f"\n⚠️  Test image not found at: {test_image_path}")
        print("   Creating a placeholder test with a URL instead...")

        test_image = "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Kitchen_faucet.jpg/800px-Kitchen_faucet.jpg"
        context = "Kitchen faucet appears to be dripping from the spout"
    else:
        test_image = test_image_path
        context = "Technician reports this faucet has been dripping since last night"

    print(f"\n📸 Image: {test_image}")
    print(f"📝 Context: {context}")

    try:
        result = await eye.analyze(
            image_source=test_image,
            context=context,
            technician_notes="Customer says it's been getting worse over the past week",
        )

        print("\n✅ Analysis complete!")

        oi = result["object_identification"]
        print(f"\n🔍 Object Identification:")
        print(f"   Object: {oi['object']}")
        print(f"   Brand: {oi.get('brand', 'N/A')}")
        print(f"   Model: {oi.get('model', 'N/A')}")
        print(f"   Type: {oi['type']}")
        print(f"   Condition: {oi['condition']}")

        pd = result["problem_detected"]
        print(f"\n⚠️  Problem Detected:")
        print(f"   Description: {pd['description']}")
        print(f"   Location: {pd['location']}")
        print(f"   Type: {pd['type']}")
        print(f"   Severity: {pd['severity_visible']}")

        print(f"\n📊 Overall Severity: {result['overall_severity'].upper()}")
        print(f"🎯 Probable Cause: {result['probable_cause']}")

        if result["alternative_causes"]:
            print(f"\n🔄 Alternative Causes:")
            for cause in result["alternative_causes"]:
                print(f"   • {cause}")

        if result["safety_warnings"]:
            print(f"\n🚨 Safety Warnings:")
            for warning in result["safety_warnings"]:
                print(f"   • [{warning['severity'].upper()}] {warning['warning']}")
                print(f"     Action: {warning['action_required']}")
        else:
            print(f"\n✅ No safety warnings")

        conf = result["confidence"]
        print(f"\n📈 Confidence:")
        print(f"   Level: {conf['level']}")
        print(f"   Score: {conf['score']:.2f}")
        print(f"   Reasoning: {conf['reasoning']}")

        if result["limitations"]:
            print(f"\n⚠️  Limitations:")
            for limit in result["limitations"]:
                print(f"   • {limit}")

        if result["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in result["recommendations"]:
                print(f"   • {rec}")

        print(f"\n📝 Summary: {eye.get_summary(result)}")

        from src.services.qwen_client import get_qwen_client
        client = get_qwen_client()
        summary = client.get_cost_summary()
        print(f"\n💰 Cost of this analysis: ${summary['total_cost']:.4f}")
        print(f"   Remaining budget: ${summary['remaining_budget']:.2f}")

    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
