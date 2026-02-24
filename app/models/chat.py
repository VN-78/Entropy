from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field

# Tool definitions
class Function(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    arguments: Optional[str] = None # Added for tool calls

class Tool(BaseModel):
    type: Literal["function"] = "function"
    function: Function

class ToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: Function

# Chat Models
class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    reasoning_content: Optional[str] = None  # For thinking/reasoning text

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = "local-model"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = -1
    stream: bool = False
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    # Prompt Template Support
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None

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
