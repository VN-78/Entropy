from fastapi import APIRouter, HTTPException
from app.models.chat import ChatCompletionRequest, ChatCompletionResponse, Message
from app.api.deps import LLMClientDep
from app.core.templates import PromptManager
import httpx

router = APIRouter()

@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    client: LLMClientDep
) -> ChatCompletionResponse:
    try:
        # Handle Prompt Templates
        if request.template_id:
            try:
                system_content = PromptManager.render_system_message(
                    request.template_id, 
                    request.template_variables
                )
                # Check if a system message already exists at the beginning
                if request.messages and request.messages[0].role == "system":
                    # Optionally replace or append? Let's prepend or replace.
                    # For now, let's prepend as the "Base" system prompt.
                    request.messages.insert(0, Message(role="system", content=system_content))
                else:
                    request.messages.insert(0, Message(role="system", content=system_content))
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        return await client.chat_completion(request)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
