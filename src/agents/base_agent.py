"""
Base class for all JING agents.

All agents inherit from this base class to ensure:
- Consistent initialization
- Automatic prompt loading from prompts/ folder
- Standardized error handling
- Cost tracking integration
- Structured logging

Usage:
    >>> class MyAgent(BaseAgent):
    ...     async def execute(self, task_input: Dict) -> Dict:
    ...         response = await self.call_qwen("Your prompt here")
    ...         return {"result": response}
"""

import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from src.services.qwen_client import QwenClient, get_qwen_client
from src.utils.config import settings
from src.utils.logger import get_logger, log_agent_execution

logger = get_logger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for all JING agents.

    Provides common functionality:
    - System prompt loading from prompts/ folder
    - Qwen client access
    - Execution tracking and logging
    - Error handling
    """

    def __init__(
        self,
        name: str,
        model: Optional[str] = None,
        qwen_client: Optional[QwenClient] = None,
    ):
        """
        Initialize the agent.

        Args:
            name: Agent name (e.g., "JING-EYE", "JING-MASTER")
            model: Qwen model to use (defaults based on agent type)
            qwen_client: Optional QwenClient instance (uses singleton if not provided)
        """
        self.name = name
        self.model = model or self._get_default_model()
        self.qwen_client = qwen_client or get_qwen_client()
        self.system_prompt = self._load_prompt()

        logger.info(f"Initialized agent: {self.name} with model: {self.model}")

    def _get_default_model(self) -> str:
        """
        Get default model for this agent type.

        Override in subclasses to specify different defaults.
        """
        return settings.QWEN_PLUS_MODEL

    def _load_prompt(self) -> str:
        """
        Load system prompt from prompts/ folder.

        Looks for: src/prompts/{agent_name_lowercase}.md

        Returns:
            The system prompt as a string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_filename = self.name.lower().replace("jing-", "") + ".md"
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_filename

        if not prompt_path.exists():
            raise FileNotFoundError(
                f"System prompt not found for {self.name} at: {prompt_path}"
            )

        prompt_content = prompt_path.read_text(encoding="utf-8")
        logger.debug(f"Loaded prompt for {self.name} from {prompt_path}")

        return prompt_content

    @abstractmethod
    async def execute(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's specific task.

        Must be implemented by all subclasses.

        Args:
            task_input: Dictionary containing task-specific inputs

        Returns:
            Dictionary containing the task results
        """
        pass

    async def call_qwen(
        self,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Helper method to call Qwen API with this agent's system prompt.

        Args:
            user_message: The user's message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to client.chat()

        Returns:
            The model's response as a string
        """
        return await self.qwen_client.chat(
            model=self.model,
            system=self.system_prompt,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    async def call_qwen_json(
        self,
        user_message: str,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Helper method to call Qwen API with JSON output.

        Args:
            user_message: The user's message
            temperature: Sampling temperature (lower for structured output)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to client.chat_json()

        Returns:
            Parsed JSON as a dictionary
        """
        return await self.qwen_client.chat_json(
            model=self.model,
            system=self.system_prompt,
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    async def call_qwen_vision(
        self,
        prompt: str,
        image_source: Any,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """
        Helper method to call Qwen API with vision (image + text).

        Args:
            prompt: Text prompt for the image
            image_source: URL, file path, or bytes
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional arguments passed to client.vision()

        Returns:
            The model's analysis as a string
        """
        return await self.qwen_client.vision(
            model=self.model,
            system=self.system_prompt,
            prompt=prompt,
            image_source=image_source,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    def log_execution(self, task_id: str, status: str, duration_ms: float) -> None:
        """
        Log agent execution for tracking and debugging.

        Args:
            task_id: Task identifier
            status: Execution status (success, failed, timeout)
            duration_ms: Execution duration in milliseconds
        """
        log_agent_execution(
            agent_name=self.name,
            task_id=task_id,
            status=status,
            duration_ms=duration_ms,
        )


class AgentExecutionError(Exception):
    """Raised when an agent execution fails."""
    pass


class AgentTimeoutError(AgentExecutionError):
    """Raised when an agent execution times out."""
    pass


class AgentValidationError(AgentExecutionError):
    """Raised when agent input validation fails."""
    pass
