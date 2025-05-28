import logging
from typing import Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Gemini LLM client wrapper"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize Gemini client

        Args:
            model_name: Model name to use (default: gemini-pro)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            api_key: Google API key (if not provided, will use GOOGLE_API_KEY env var)
        """
        self.model_name = settings.GOOGLE_CHAT_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = settings.GOOGLE_API_KEY

        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key parameter."
            )

        self._client = None

    def get_chat_model(self) -> BaseChatModel:
        """Get the chat model instance"""
        if self._client is None:
            self._client = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                google_api_key=self.api_key,
            )
        return self._client

    def create_client(
        self, model_name: Optional[str] = None, temperature: Optional[float] = None, max_tokens: Optional[int] = None
    ) -> BaseChatModel:
        """Create a new client instance with different parameters

        Args:
            model_name: Override model name
            temperature: Override temperature
            max_tokens: Override max tokens

        Returns:
            New chat model instance
        """
        return ChatGoogleGenerativeAI(
            model=model_name or self.model_name,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            google_api_key=self.api_key,
        )
