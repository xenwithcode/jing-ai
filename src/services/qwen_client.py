"""
Qwen Cloud API client for JING.

This is the core service that all JING agents use to communicate with Qwen Cloud.
It handles:
- Chat completions (text)
- Vision analysis (images for JING-EYE)
- Audio processing (for JING-VOICE)
- Cost tracking (critical for the $40 hackathon budget)
- Retry logic with exponential backoff
- Structured logging of every API call

Usage:
    >>> from src.services.qwen_client import get_qwen_client
    >>> client = get_qwen_client()
    >>> response = await client.chat("qwen-max", "Hello, JING!")
    >>> print(response)
"""

import base64
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import httpx
from openai import AsyncOpenAI, APIError, RateLimitError, APITimeoutError
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.utils.config import settings
from src.utils.logger import get_logger, log_api_call

logger = get_logger(__name__)


# ═══════════════════════════════════════════════════════════════
# COST TRACKING (Critical for hackathon budget!)
# ═══════════════════════════════════════════════════════════════

MODEL_PRICES = {
    "qwen-turbo": {"input": 0.05, "output": 0.20},
    "qwen-plus": {"input": 0.40, "output": 1.20},
    "qwen-max": {"input": 1.04, "output": 3.90},
    "qwen-vl-plus": {"input": 0.80, "output": 2.00},
    "qwen-vl-max": {"input": 1.50, "output": 5.00},
    "qwen-audio-turbo": {"input": 0.30, "output": 0.90},
    "text-embedding-v3": {"input": 0.07, "output": 0.0},
}


class CostTracker:
    """Track API costs in real-time to stay within budget."""

    def __init__(self, budget_limit: float = 40.0):
        self.budget_limit = budget_limit
        self.total_cost = 0.0
        self.call_count = 0
        self.calls_by_model: Dict[str, Dict[str, Any]] = {}

    def record_call(
        self,
        model: str,
        tokens_in: int,
        tokens_out: int,
        cost: float,
        duration_ms: float,
    ) -> None:
        """Record an API call and update totals."""
        self.total_cost += cost
        self.call_count += 1

        if model not in self.calls_by_model:
            self.calls_by_model[model] = {
                "calls": 0,
                "tokens_in": 0,
                "tokens_out": 0,
                "cost": 0.0,
            }

        self.calls_by_model[model]["calls"] += 1
        self.calls_by_model[model]["tokens_in"] += tokens_in
        self.calls_by_model[model]["tokens_out"] += tokens_out
        self.calls_by_model[model]["cost"] += cost

        if self.total_cost > self.budget_limit * 0.8:
            logger.warning(
                f"Budget warning: ${self.total_cost:.2f} / ${self.budget_limit:.2f} "
                f"({self.total_cost/self.budget_limit*100:.1f}% used)"
            )

        if self.total_cost > self.budget_limit:
            logger.error(
                f"BUDGET EXCEEDED: ${self.total_cost:.2f} / ${self.budget_limit:.2f}"
            )

    def get_remaining_budget(self) -> float:
        return max(0.0, self.budget_limit - self.total_cost)

    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_cost": round(self.total_cost, 4),
            "remaining_budget": round(self.get_remaining_budget(), 4),
            "call_count": self.call_count,
            "calls_by_model": self.calls_by_model,
        }


cost_tracker = CostTracker(budget_limit=40.0)


# ═══════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS
# ═══════════════════════════════════════════════════════════════

class QwenClientError(Exception):
    pass


class QwenBudgetExceededError(QwenClientError):
    pass


class QwenRateLimitError(QwenClientError):
    pass


class QwenAPIError(QwenClientError):
    pass


# ═══════════════════════════════════════════════════════════════
# MAIN CLIENT
# ═══════════════════════════════════════════════════════════════

class QwenClient:
    """
    Async client for Qwen Cloud API.

    Wraps the OpenAI-compatible API with:
    - Cost tracking
    - Retry logic
    - Structured logging
    - Budget protection
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        budget_limit: float = 40.0,
    ):
        self.api_key = api_key or settings.QWEN_API_KEY
        self.base_url = base_url or settings.QWEN_BASE_URL
        self.budget_limit = budget_limit

        self._client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=httpx.AsyncClient(
                timeout=60.0,
                follow_redirects=True,
            ),
        )

        logger.info(f"QwenClient initialized with base_url={self.base_url}")

    # ═══════════════════════════════════════════════════════════
    # CORE CHAT COMPLETION
    # ═══════════════════════════════════════════════════════════

    @retry(
        stop=stop_after_attempt(settings.AGENT_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((RateLimitError, APITimeoutError)),
        reraise=True,
    )
    async def chat(
        self,
        model: str,
        user_message: str,
        system: Optional[str] = None,
        messages: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Basic chat completion (text only).

        Args:
            model: Model name (e.g., "qwen-max", "qwen-plus")
            user_message: The user's message
            system: Optional system prompt
            messages: Optional full message history (overrides user_message)
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
            response_format: e.g., {"type": "json_object"} for JSON output

        Returns:
            The model's response as a string

        Raises:
            QwenBudgetExceededError: If budget is exceeded
            QwenAPIError: For other API errors
        """
        if cost_tracker.total_cost >= self.budget_limit:
            raise QwenBudgetExceededError(
                f"Budget exceeded: ${cost_tracker.total_cost:.2f} / ${self.budget_limit:.2f}"
            )

        if messages is None:
            messages = []
            if system:
                messages.append({"role": "system", "content": system})
            messages.append({"role": "user", "content": user_message})

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if response_format:
            kwargs["response_format"] = response_format

        start_time = time.time()

        try:
            response = await self._client.chat.completions.create(**kwargs)
            duration_ms = (time.time() - start_time) * 1000

            content = response.choices[0].message.content or ""

            usage = response.usage
            if usage:
                tokens_in = usage.prompt_tokens
                tokens_out = usage.completion_tokens
                cost = self._calculate_cost(model, tokens_in, tokens_out)

                cost_tracker.record_call(
                    model=model,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost=cost,
                    duration_ms=duration_ms,
                )

                log_api_call(
                    model=model,
                    tokens_in=tokens_in,
                    tokens_out=tokens_out,
                    cost_usd=cost,
                    duration_ms=duration_ms,
                )

            return content

        except RateLimitError as e:
            logger.warning(f"Rate limit hit for {model}, retrying...")
            raise
        except APITimeoutError as e:
            logger.warning(f"Timeout for {model}, retrying...")
            raise
        except APIError as e:
            logger.error(f"Qwen API error: {e}")
            raise QwenAPIError(f"Qwen API error: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error calling {model}: {e}", exc_info=True)
            raise QwenClientError(f"Unexpected error: {e}") from e

    # ═══════════════════════════════════════════════════════════
    # VISION (for JING-EYE)
    # ═══════════════════════════════════════════════════════════

    async def vision(
        self,
        model: str,
        prompt: str,
        image_source: Union[str, Path, bytes],
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Vision analysis (image + text).

        Args:
            model: Vision model (e.g., "qwen-vl-max")
            prompt: Text prompt for the image
            image_source: URL string, file path, or raw bytes
            system: Optional system prompt
            temperature: Sampling temperature (lower for vision)
            max_tokens: Maximum tokens to generate

        Returns:
            The model's analysis as a string
        """
        if isinstance(image_source, Path) or (
            isinstance(image_source, str) and Path(image_source).exists()
        ):
            image_data = self._encode_image_to_base64(Path(image_source))
            image_content = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            }
        elif isinstance(image_source, bytes):
            image_data = base64.b64encode(image_source).decode("utf-8")
            image_content = {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
            }
        else:
            image_content = {
                "type": "image_url",
                "image_url": {"url": str(image_source)},
            }

        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                image_content,
            ],
        })

        return await self.chat(
            model=model,
            user_message="",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # ═══════════════════════════════════════════════════════════
    # JSON MODE (for JING-MASTER plans)
    # ═══════════════════════════════════════════════════════════

    async def chat_json(
        self,
        model: str,
        user_message: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Chat with guaranteed JSON output.

        Perfect for JING-MASTER plans and JING-EYE structured results.

        Returns:
            Parsed JSON as a dictionary
        """
        import json

        response = await self.chat(
            model=model,
            user_message=user_message,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response[:200]}...")
            raise QwenClientError(f"Invalid JSON from model: {e}") from e

    # ═══════════════════════════════════════════════════════════
    # UTILITIES
    # ═══════════════════════════════════════════════════════════

    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        prices = MODEL_PRICES.get(model)
        if not prices:
            logger.warning(f"Unknown model {model}, assuming $0 cost")
            return 0.0

        cost_in = (tokens_in / 1_000_000) * prices["input"]
        cost_out = (tokens_out / 1_000_000) * prices["output"]
        return cost_in + cost_out

    def _encode_image_to_base64(self, image_path: Path) -> str:
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_cost_summary(self) -> Dict[str, Any]:
        return cost_tracker.get_summary()

    def get_remaining_budget(self) -> float:
        return cost_tracker.get_remaining_budget()

    async def health_check(self) -> bool:
        """Check if Qwen Cloud API is reachable."""
        try:
            await self.chat(model="qwen-turbo", user_message="ping", max_tokens=5)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# ═══════════════════════════════════════════════════════════════
# SINGLETON ACCESSOR
# ═══════════════════════════════════════════════════════════════

@lru_cache()
def get_qwen_client() -> QwenClient:
    """Get singleton QwenClient instance."""
    return QwenClient()


# ═══════════════════════════════════════════════════════════════
# TEST / DEMO
# ═══════════════════════════════════════════════════════════════

async def _demo():
    """Demo the QwenClient with a simple test."""
    client = get_qwen_client()

    print("\n" + "=" * 60)
    print("Qwen Client Demo")
    print("=" * 60)

    print("\n1. Health check...")
    healthy = await client.health_check()
    print(f"   API healthy: {healthy}")

    if not healthy:
        print("   API not reachable. Check your QWEN_API_KEY.")
        return

    print("\n2. Basic chat with qwen-turbo...")
    response = await client.chat(
        model="qwen-turbo",
        user_message="Say 'Hello JING!' in exactly 3 words.",
        max_tokens=20,
    )
    print(f"   Response: {response}")

    print("\n3. JSON mode with qwen-plus...")
    plan = await client.chat_json(
        model="qwen-plus",
        system="You are a helpful assistant that returns JSON.",
        user_message='Return {"status": "ok", "message": "JING is ready"}',
    )
    print(f"   Parsed JSON: {plan}")

    print("\n4. Cost summary:")
    summary = client.get_cost_summary()
    print(f"   Total cost: ${summary['total_cost']:.4f}")
    print(f"   Remaining: ${summary['remaining_budget']:.4f}")
    print(f"   Calls: {summary['call_count']}")

    print("\n" + "=" * 60)
    print("QwenClient is working correctly!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(_demo())
