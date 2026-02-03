from typing import Annotated
from fastapi import Depends
from app.core.interfaces import LLMClient
from app.services.lm_studio import LMStudioClient

def get_llm_client() -> LLMClient:
    return LMStudioClient()

LLMClientDep = Annotated[LLMClient, Depends(get_llm_client)]
