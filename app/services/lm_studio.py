import httpx
from app.core.interfaces import LLMClient
from app.core.config import settings
from app.models.chat import ChatCompletionRequest, ChatCompletionResponse

class LMStudioClient(LLMClient):
    def __init__(self, base_url: str = settings.LM_STUDIO_BASE_URL):
        self.base_url = base_url

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            response = await client.post(
                "chat/completions",
                json=request.model_dump(exclude_none=True, exclude={"template_id", "template_variables"})
            )
            response.raise_for_status()
            return ChatCompletionResponse(**response.json())
