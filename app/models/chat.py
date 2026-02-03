from typing import List, Optional, Literal
from pydantic import BaseModel

class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "local-model"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = -1
    stream: bool = False

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Optional[dict] = None
