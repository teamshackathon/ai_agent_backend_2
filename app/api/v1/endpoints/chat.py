import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.core.llm.client.gemini_client import GeminiClient
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


def get_chat_service(gemini_client: GeminiClient = Depends(get_gemini_client)) -> ChatService:
    """Dependency to get chat service"""
    try:
        return ChatService(gemini_client)
    except Exception as e:
        logger.error(f"Failed to create chat service: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initialize chat service.")


@router.post("/chat", response_model=ChatOutput)
async def chat_endpoint(chat_input: ChatInput, chat_service: ChatService = Depends(get_chat_service), current_user = Depends(get_current_user)) -> ChatOutput:
    """Chat endpoint using Gemini LLM

    Args:
        chat_input: Chat input containing role, response, history, and optional model name
        chat_service: Chat service dependency

    Returns:
        Chat response with role and response content

    Raises:
        HTTPException: If chat processing fails
    """
    try:
        logger.info(f"Processing chat request for role: {chat_input.role}")

        # Process the chat request
        result = chat_service.chat(chat_input)

        logger.info("Chat request processed successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat request: {str(e)}")
