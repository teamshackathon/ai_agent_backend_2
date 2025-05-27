import logging

from app.core.llm.chain.chatchain import ChatChain
from app.core.llm.client.gemini_client import GeminiClient
from app.schemas.chat import ChatInput, ChatOutput

logger = logging.getLogger(__name__)


class ChatService:
    """Chat service using Gemini LLM"""

    def __init__(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        self._setup_chain()

    def _setup_chain(self):
        """Setup the chat chain"""
        chat_llm = self.gemini_client.get_chat_model()
        self.chain = ChatChain(chat_llm)

    def chat(self, chat_input: ChatInput) -> ChatOutput:
        """Process chat request

        Args:
            chat_input: Chat input data

        Returns:
            Chat response
        """
        try:
            # Set default model name if not provided
            if not chat_input.model_name:
                chat_input.model_name = "gemini-pro"

            # Invoke the chain directly with ChatInput
            result = self.chain.invoke(chat_input)

            return result

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            # Return error response
            return ChatOutput(role="assistant", response=f"Sorry, I encountered an error: {str(e)}")
