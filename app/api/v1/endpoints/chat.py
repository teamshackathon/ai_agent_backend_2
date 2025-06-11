import logging

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.api.deps import get_current_user, get_mongo_db
from app.core.llm.client.gemini_client import GeminiClient
from app.repositories.chat_history_repository import ChatHistoryRepository
from app.schemas.chat import ChatInput, ChatOutput
from app.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_gemini_client() -> GeminiClient:
    """Dependency to get Gemini client"""
    try:
        return GeminiClient()
    except Exception as e:
        logger.error(f"Failed to create Gemini client: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to initialize LLM client. Please check API key configuration."
        )


def get_chat_service(
    gemini_client: GeminiClient = Depends(get_gemini_client), mongodb: AsyncIOMotorDatabase = Depends(get_mongo_db)
) -> ChatService:
    """Dependency to get chat service with history repository

    Args:
        gemini_client: Gemini LLM client
        mongodb: MongoDB database connection

    Returns:
        Configured chat service with history repository
    """
    try:
        # Create history repository with MongoDB connection
        chat_history_repository = ChatHistoryRepository(mongodb)

        # Create chat service with repository
        return ChatService(gemini_client, chat_history_repository)
    except Exception as e:
        logger.error(f"Failed to create chat service: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize chat service.")


@router.post("/chat", response_model=ChatOutput)
async def chat_endpoint(
    chat_input: ChatInput, chat_service: ChatService = Depends(get_chat_service), current_user=Depends(get_current_user)
) -> ChatOutput:
    """Chat endpoint using Gemini LLM with persistent history

    Args:
        chat_input: Chat input containing role, response, history, and chat_id
        chat_service: Chat service dependency
        current_user: Current authenticated user

    Returns:
        Chat response with role and response content

    Raises:
        HTTPException: If chat processing fails
    """
    try:
        logger.info(f"Processing chat request for chat_id: {chat_input.chat_id}")

        # Get user ID from authenticated user if available
        user_id = None
        if current_user:
            user_id = current_user.id

        # Process the chat request with user ID for history tracking
        result = await chat_service.chat(chat_input, user_id)

        logger.info("Chat request processed successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")
