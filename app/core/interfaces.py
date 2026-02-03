from abc import ABC, abstractmethod
from app.models.chat import ChatCompletionRequest, ChatCompletionResponse

class LLMClient(ABC):
    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Send a chat completion request to the LLM."""
        pass
