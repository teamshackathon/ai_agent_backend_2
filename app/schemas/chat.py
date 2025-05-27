from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import BaseInput, BaseOutput


class ChatMessage(BaseModel):
    """Chat message model"""

    role: str = Field(..., description="Role of the message sender (user, assistant)")
    content: str = Field(..., description="Content of the message")


class ChatInput(BaseInput):
    """Input schema for chat endpoint"""

    role: str = Field(..., description="Role of the current message")
    response: str = Field(..., description="Current message content")
    history: List[ChatMessage] = Field(default=[], description="Chat history")
    model_name: Optional[str] = Field(default=None, description="Model deployment name")


class ChatOutput(BaseOutput):
    """Output schema for chat endpoint"""

    role: str = Field(..., description="Role of the response")
    response: str = Field(..., description="Response content")


# Internal schemas for chain processing
class ChatChainInput(BaseInput):
    """Internal input schema for chat chain"""

    role: str = Field(..., description="Role of the current message")
    response: str = Field(..., description="Current message content")
    history: str = Field(..., description="Formatted chat history")
    model_name: str = Field(..., description="Model deployment name")


class ChatChainOutput(BaseOutput):
    """Internal output schema for chat chain"""

    role: str = Field(..., description="Role of the response")
    response: str = Field(..., description="Response content")
