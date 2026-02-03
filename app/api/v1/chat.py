from fastapi import APIRouter, HTTPException
from app.models.chat import ChatCompletionRequest, ChatCompletionResponse
from app.api.deps import LLMClientDep
import httpx

router = APIRouter()

@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    client: LLMClientDep
) -> ChatCompletionResponse:
    try:
        return await client.chat_completion(request)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
