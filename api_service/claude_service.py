import anthropic
from anthropic import AsyncAnthropic
from typing import List, Optional, AsyncGenerator
import logging
from config import get_settings
from models import Message, ChatRequest, CompletionRequest

logger = logging.getLogger(__name__)


class ClaudeService:
    """Service for interacting with Claude API"""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.default_model = settings.default_claude_model
        self.max_tokens = settings.max_tokens_per_request

    async def chat(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 1.0,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        system: Optional[str] = None,
    ) -> dict:
        """
        Send a chat request to Claude API

        Args:
            messages: List of conversation messages
            model: Model to use (defaults to configured model)
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            system: System prompt

        Returns:
            Response dictionary from Claude API
        """
        try:
            # Convert messages to Anthropic format
            formatted_messages = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            # Prepare request parameters
            params = {
                "model": model or self.default_model,
                "max_tokens": max_tokens or self.max_tokens,
                "messages": formatted_messages,
                "temperature": temperature,
            }

            # Add optional parameters
            if top_p is not None:
                params["top_p"] = top_p
            if top_k is not None:
                params["top_k"] = top_k
            if system:
                params["system"] = system

            logger.info(f"Sending chat request with model: {params['model']}")

            # Make API call
            response = await self.client.messages.create(**params)

            return response

        except anthropic.APIError as e:
            logger.error(f"Claude API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}")
            raise

    async def chat_stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 1.0,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        system: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Send a streaming chat request to Claude API

        Args:
            messages: List of conversation messages
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            system: System prompt

        Yields:
            Text chunks from the streaming response
        """
        try:
            formatted_messages = [
                {"role": msg.role, "content": msg.content} for msg in messages
            ]

            params = {
                "model": model or self.default_model,
                "max_tokens": max_tokens or self.max_tokens,
                "messages": formatted_messages,
                "temperature": temperature,
            }

            if top_p is not None:
                params["top_p"] = top_p
            if top_k is not None:
                params["top_k"] = top_k
            if system:
                params["system"] = system

            logger.info(f"Starting streaming chat with model: {params['model']}")

            async with self.client.messages.stream(**params) as stream:
                async for text in stream.text_stream:
                    yield text

        except anthropic.APIError as e:
            logger.error(f"Claude API streaming error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in streaming chat: {str(e)}")
            raise

    async def complete(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = 1.0,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        system: Optional[str] = None,
    ) -> dict:
        """
        Generate a text completion

        Args:
            prompt: Text prompt
            model: Model to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            system: System prompt

        Returns:
            Response dictionary from Claude API
        """
        # Convert prompt to message format
        messages = [Message(role="user", content=prompt)]

        return await self.chat(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            system=system,
        )

    async def get_available_models(self) -> List[str]:
        """
        Get list of available Claude models

        Returns:
            List of model identifiers
        """
        # This is a static list for now, as Anthropic doesn't have a models endpoint
        return [
            "claude-opus-4-5-20251101",
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
        ]


# Singleton instance
_claude_service: Optional[ClaudeService] = None


def get_claude_service() -> ClaudeService:
    """Get or create Claude service instance"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeService()
    return _claude_service
