"""
JING-VOICE: The Hands-Free Voice Interface

JING-VOICE converts consolidated technical responses into natural, concise
speech optimized for field technicians working with dirty hands, in tight
spaces, or on ladders.

Key features:
- Responses under 30 seconds when spoken
- Part numbers spelled out and repeated twice
- Safety warnings stated first
- Confirmation question at the end
- Optimized for audio delivery (not reading)

Usage:
    >>> from src.agents.voice import VoiceAgent
    >>> voice = VoiceAgent()
    >>> result = await voice.synthesize(
    ...     diagnosis="Moen Chateau 7400 cartridge failure",
    ...     part_number="Moen 1225",
    ...     tools=["Allen key 3/32", "needle-nose pliers"],
    ...     manual_reference="Page 12"
    ... )
    >>> print(result["spoken_response"])
"""

import json
from typing import Any, Dict, List, Optional

from src.agents.base_agent import BaseAgent, AgentExecutionError, AgentValidationError
from src.utils.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceAgent(BaseAgent):
    """
    JING-VOICE: Voice interface specialist.
    
    Converts technical responses into concise, spoken-optimized text
    that can be delivered via TTS (text-to-speech) to the technician.
    """
    
    def __init__(self):
        """Initialize JING-VOICE with qwen-audio-turbo model."""
        super().__init__(name="JING-VOICE")
        logger.info("JING-VOICE initialized (voice interface)")
    
    def _get_default_model(self) -> str:
        """VOICE uses qwen-audio-turbo for natural speech."""
        return settings.QWEN_AUDIO_MODEL
    
    async def synthesize(
        self,
        diagnosis: str,
        part_number: Optional[str] = None,
        tools: Optional[List[str]] = None,
        manual_reference: Optional[str] = None,
        safety_warnings: Optional[List[str]] = None,
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Synthesize a spoken response from technical information.
        
        Args:
            diagnosis: Brief diagnosis of the problem
            part_number: Critical part number (if any)
            tools: List of key tools needed (2-3 max)
            manual_reference: Manual page/section reference
            safety_warnings: Any safety warnings (stated first)
            additional_context: Extra context from other agents
        
        Returns:
            Structured voice response with:
            - spoken_response: Text to be spoken
            - estimated_duration_seconds: How long it takes to speak
            - critical_info_repeated: Info repeated for clarity
            - safety_warning_first: Whether safety warning is first
            - confirmation_question: Closing question
        
        Raises:
            AgentValidationError: If inputs are invalid
            AgentExecutionError: If synthesis fails
        """
        # ═══════════════════════════════════════════════════════════
        # VALIDATE INPUTS
        # ═══════════════════════════════════════════════════════════
        
        if not diagnosis:
            raise AgentValidationError("Diagnosis is required")
        
        logger.info(f"JING-VOICE synthesizing response for: {diagnosis[:50]}...")
        
        # ═══════════════════════════════════════════════════════════
        # BUILD PROMPT
        # ═══════════════════════════════════════════════════════════
        
        prompt = self._build_voice_prompt(
            diagnosis=diagnosis,
            part_number=part_number,
            tools=tools,
            manual_reference=manual_reference,
            safety_warnings=safety_warnings,
            additional_context=additional_context,
        )
        
        # ═══════════════════════════════════════════════════════════
        # CALL QWEN
        # ═══════════════════════════════════════════════════════════
        
        try:
            response_text = await self.call_qwen(
                user_message=prompt,
                temperature=0.5,  # Slightly higher for natural speech
                max_tokens=300,   # Keep it short
            )
        except Exception as e:
            logger.error(f"JING-VOICE synthesis failed: {e}", exc_info=True)
            raise AgentExecutionError(f"Voice synthesis failed: {e}") from e
        
        # ═══════════════════════════════════════════════════════════
        # PARSE AND VALIDATE
        # ═══════════════════════════════════════════════════════════
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"JING-VOICE returned invalid JSON: {response_text[:200]}...")
            raise AgentExecutionError(f"Invalid JSON from VOICE: {e}") from e
        
        validated_result = self._validate_voice_response(result)
        
        # Check duration
        if validated_result["estimated_duration_seconds"] > 30:
            logger.warning(
                f"Voice response is {validated_result['estimated_duration_seconds']}s, "
                f"exceeds 30s target. Consider shortening."
            )
        
        logger.info(
            f"JING-VOICE synthesized response: "
            f"{validated_result['estimated_duration_seconds']}s, "
            f"safety_first={validated_result['safety_warning_first']}"
        )
        
        return validated_result
    
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute method required by BaseAgent. Delegates to synthesize()."""
        return await self.synthesize(
            diagnosis=task_input.get("diagnosis", ""),
            part_number=task_input.get("part_number"),
            tools=task_input.get("tools"),
            manual_reference=task_input.get("manual_reference"),
            safety_warnings=task_input.get("safety_warnings"),
            additional_context=task_input.get("additional_context"),
        )
    
    def _build_voice_prompt(
        self,
        diagnosis: str,
        part_number: Optional[str],
        tools: Optional[List[str]],
        manual_reference: Optional[str],
        safety_warnings: Optional[List[str]],
        additional_context: Optional[Dict[str, Any]],
    ) -> str:
        """Build the prompt for voice synthesis."""
        parts = ["═══ VOICE SYNTHESIS REQUEST ═══\n"]
        
        parts.append(f"🔍 DIAGNOSIS: {diagnosis}")
        
        if part_number:
            parts.append(f"\n🔢 PART NUMBER: {part_number}")
        
        if tools:
            parts.append(f"\n🔧 KEY TOOLS: {', '.join(tools[:3])}")
        
        if manual_reference:
            parts.append(f"\n📖 MANUAL: {manual_reference}")
        
        if safety_warnings:
            parts.append(f"\n🚨 SAFETY WARNINGS:")
            for warning in safety_warnings:
                parts.append(f"   • {warning}")
        
        if additional_context:
            parts.append(f"\n📋 ADDITIONAL CONTEXT:")
            for key, value in list(additional_context.items())[:3]:
                parts.append(f"   • {key}: {value}")
        
        parts.append("\n══════════════════════════════════")
        parts.append("\nConvert this into a concise spoken response.")
        parts.append("Rules:")
        parts.append("- MAX 30 seconds when spoken (~75-90 words)")
        parts.append("- Spell out part numbers and repeat twice")
        parts.append("- Safety warnings FIRST if present")
        parts.append("- End with confirmation question")
        parts.append("- Return JSON format as specified in your system prompt")
        
        return "\n".join(parts)
    
    def _validate_voice_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the voice response has the required structure."""
        required_keys = ["spoken_response", "estimated_duration_seconds", "confirmation_question"]
        for key in required_keys:
            if key not in result:
                raise AgentValidationError(f"Voice response missing required key: {key}")
        
        # Validate spoken_response is not empty
        if not result["spoken_response"] or len(result["spoken_response"].strip()) == 0:
            raise AgentValidationError("spoken_response cannot be empty")
        
        # Validate duration is a number
        if not isinstance(result["estimated_duration_seconds"], (int, float)):
            raise AgentValidationError("estimated_duration_seconds must be a number")
        
        # Validate safety_warning_first is boolean
        if "safety_warning_first" not in result:
            result["safety_warning_first"] = False
        elif not isinstance(result["safety_warning_first"], bool):
            result["safety_warning_first"] = bool(result["safety_warning_first"])
        
        # Ensure critical_info_repeated is a list
        if "critical_info_repeated" not in result:
            result["critical_info_repeated"] = []
        elif not isinstance(result["critical_info_repeated"], list):
            result["critical_info_repeated"] = [result["critical_info_repeated"]]
        
        logger.debug("Voice response validated successfully")
        
        return result
    
    def get_spoken_text(self, voice_response: Dict[str, Any]) -> str:
        """Get just the spoken text for TTS."""
        return voice_response["spoken_response"]
    
    def estimate_word_count(self, text: str) -> int:
        """Estimate word count for duration calculation."""
        return len(text.split())
    
    def estimate_duration(self, text: str, words_per_minute: int = 150) -> float:
        """
        Estimate speaking duration in seconds.
        
        Args:
            text: The text to be spoken
            words_per_minute: Speaking rate (default 150 wpm for clear speech)
        
        Returns:
            Estimated duration in seconds
        """
        word_count = self.estimate_word_count(text)
        return (word_count / words_per_minute) * 60


# ═══════════════════════════════════════════════════════════════
# DEMO / TEST
# ═══════════════════════════════════════════════════════════════

async def _demo():
    """Demo JING-VOICE with a realistic scenario."""
    voice = VoiceAgent()
    
    print("\n" + "="*70)
    print("JING-VOICE Synthesis Demo")
    print("="*70)
    
    print("\n📋 Scenario: Moen Chateau 7400 faucet with cartridge failure")
    
    try:
        result = await voice.synthesize(
            diagnosis="Moen Chateau 7400 cartridge failure causing drip",
            part_number="Moen 1225",
            tools=["Allen key 3/32 inch", "needle-nose pliers"],
            manual_reference="Manual page 12",
            safety_warnings=None,
        )
        
        print("\n✅ Voice response synthesized successfully!")
        
        # Display results
        print(f"\n🎤 Spoken Response:")
        print(f"   \"{result['spoken_response']}\"")
        
        print(f"\n⏱️  Estimated Duration: {result['estimated_duration_seconds']} seconds")
        
        if result["critical_info_repeated"]:
            print(f"\n🔁 Critical Info Repeated:")
            for info in result["critical_info_repeated"]:
                print(f"   • {info}")
        
        print(f"\n🚨 Safety Warning First: {result['safety_warning_first']}")
        print(f"\n❓ Confirmation Question: \"{result['confirmation_question']}\"")
        
        # Word count and duration estimate
        word_count = voice.estimate_word_count(result["spoken_response"])
        estimated_duration = voice.estimate_duration(result["spoken_response"])
        print(f"\n📊 Analysis:")
        print(f"   Word count: {word_count}")
        print(f"   Estimated duration: {estimated_duration:.1f}s")
        print(f"   Within 30s target: {'✅ YES' if estimated_duration <= 30 else '❌ NO'}")
        
        # Show cost
        from src.services.qwen_client import get_qwen_client
        client = get_qwen_client()
        summary = client.get_cost_summary()
        print(f"\n💰 Cost: ${summary['total_cost']:.4f}")
        print(f"   Remaining budget: ${summary['remaining_budget']:.2f}")
        
    except Exception as e:
        print(f"\n❌ Voice synthesis failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
