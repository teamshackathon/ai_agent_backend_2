import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import PromptTemplate

from app.core.llm.chain.base import BaseChain
from app.schemas.chat import ChatInput, ChatOutput

logger = logging.getLogger(__name__)


class ChatChain(BaseChain):
    """Custom chat chain that handles history formatting"""

    def __init__(self, chat_llm: BaseChatModel):
        self.chat_llm = chat_llm
        self.prompt = PromptTemplate(
            template="""You are a helpful AI assistant. Based on the conversation history and the current message, provide a helpful response.

Current message role: {role}
Current message: {response}

Chat history: {history}

Model name: {model_name}

Please provide a helpful and relevant response.""",
            input_variables=["role", "response", "history", "model_name"],
        )
        self.chain = self.prompt | self.chat_llm.with_structured_output(ChatOutput, method="function_calling")

    def get_prompt(self, inputs: ChatInput, **kwargs) -> str:
        """Get the prompt string with formatted history."""
        # Format history
        history_text = ""
        for msg in inputs.history:
            history_text += f"{msg.role}: {msg.content}\n"

        # Create formatted input
        formatted_input = {
            "role": inputs.role,
            "response": inputs.response,
            "history": history_text,
            "model_name": inputs.model_name or "gemini-pro",
        }

        return self.prompt.invoke(formatted_input, **kwargs).to_string()

    def invoke(self, inputs: ChatInput, **kwargs) -> ChatOutput:
        """Invoke the chain with history formatting."""
        # Format history
        history_text = ""
        for msg in inputs.history:
            history_text += f"{msg.role}: {msg.content}\n"

        # Create formatted input
        formatted_input = {
            "role": inputs.role,
            "response": inputs.response,
            "history": history_text,
            "model_name": inputs.model_name or "gemini-pro",
        }

        # Get result from the chain
        result = self.chain.invoke(formatted_input, **kwargs)

        # Add chat_id to result
        result.chat_id = inputs.chat_id

        return result
