import logging
import uuid
from typing import Optional

from app.core.llm.chain.base import BaseChain
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.schemas.chat import ChatInput, ChatMessage, ChatOutput

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat interactions"""

    def __init__(self, chain: BaseChain, chat_history_repository: Optional[ChatHistoryRepository] = None):
        """Initialize the chat service

        Args:
            chain: LLM chain for processing chat messages
            chat_history_repository: Optional repository for storing chat history
        """
        self.chain = chain
        self.chat_history_repository = chat_history_repository

    async def chat(self, chat_input: ChatInput, user_id: Optional[str] = None) -> ChatOutput:
        """Process chat request with persistent history

        Args:
            chat_input: Chat input data
            user_id: Optional user ID for history tracking

        Returns:
            Chat response
        """
        try:
            # Generate UUID for chat_id if not provided
            if chat_input.chat_id is None:
                chat_input.chat_id = str(uuid.uuid4())
                logger.info(f"Generated new chat_id: {chat_input.chat_id}")

            # Set default model name if not provided
            if not chat_input.model_name:
                chat_input.model_name = "gemini-pro"

            # If chat history repository is available, get history from MongoDB
            if self.chat_history_repository:
                # Retrieve history from repository
                history = await self.chat_history_repository.get_history(chat_input.chat_id)

                # Update input with retrieved history
                chat_input.history = history

                # Add current user message to history
                user_message = ChatMessage(role=chat_input.role, content=chat_input.response)
                await self.chat_history_repository.append_message(chat_input.chat_id, user_message, user_id)

            # Invoke the chain directly with ChatInput
            result = self.chain.invoke(chat_input)

            # Add chat_id to the result
            result.chat_id = chat_input.chat_id

            # Save assistant's response to history if repository is available
            if self.chat_history_repository:
                assistant_message = ChatMessage(role=result.role, content=result.response)
                await self.chat_history_repository.append_message(chat_input.chat_id, assistant_message, user_id)

            return result

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            # Return error response
            return ChatOutput(
                role="assistant", response=f"Sorry, I encountered an error: {str(e)}", chat_id=chat_input.chat_id
            )
