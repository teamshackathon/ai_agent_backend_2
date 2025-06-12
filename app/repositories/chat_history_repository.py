import logging
from datetime import datetime
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class ChatHistoryRepository:
    """Repository for managing chat history in MongoDB"""

    def __init__(self, mongodb: AsyncIOMotorDatabase):
        """Initialize the repository with MongoDB connection

        Args:
            mongodb: MongoDB database connection
        """
        self.mongodb = mongodb
        self.collection = self.mongodb.talks

    async def get_history(self, chat_id: str) -> List[ChatMessage]:
        """Get chat history for a specific chat_id

        Args:
            chat_id: Unique identifier for the chat

        Returns:
            List of chat messages
        """
        try:
            # Find the talk document by chat_id
            talk = await self.collection.find_one({"chatId": chat_id})
            if not talk:
                logger.info(f"No chat history found for chat_id: {chat_id}, returning empty list")
                return []

            # Convert MongoDB messages to ChatMessage schema
            messages = []
            for msg in talk.get("messages", []):
                messages.append(ChatMessage(role=msg["role"], content=msg["text"]))

            return messages
        except Exception as e:
            logger.error(f"Error retrieving chat history for chat_id {chat_id}: {str(e)}")
            return []

    async def append_message(self, chat_id: str, message: ChatMessage, user_id: Optional[str] = None) -> bool:
        """Append a new message to the chat history

        Args:
            chat_id: Unique identifier for the chat
            message: Chat message to append
            user_id: Optional user ID associated with the chat

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find the talk document
            talk = await self.collection.find_one({"chatId": chat_id})

            # If talk doesn't exist, create a new one
            if not talk:
                logger.info(f"Creating new talk with chat_id: {chat_id}")
                await self.collection.insert_one(
                    {
                        "chatId": chat_id,
                        "userId": user_id,
                        "title": "New Conversation",  # Default title
                        "messages": [],
                        "lastUpdated": datetime.utcnow(),
                    }
                )

            # Append the message
            await self.collection.update_one(
                {"chatId": chat_id},
                {
                    "$push": {"messages": {"role": message.role, "text": message.content}},
                    "$set": {"lastUpdated": datetime.utcnow()},
                },
            )

            return True
        except Exception as e:
            logger.error(f"Error appending message to chat_id {chat_id}: {str(e)}")
            return False
