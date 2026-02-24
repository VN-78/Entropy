import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import asyncio

from app.api.deps import LLMClientDep
from app.models.chat import ChatCompletionRequest, Message
from app.services.mcp_client import data_refinery_mcp

router = APIRouter()
logger = logging.getLogger(__name__)

class AgentRunRequest(BaseModel):
    messages: List[Message]
    file_uri: str
    template_id: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None

async def agent_loop(request: AgentRunRequest, llm_client: Any):
    """
    Generator that orchestrates the LLM and the MCP data refinery tools.
    Yields SSE events (JSON strings) containing progress updates.
    """
    
    # 1. Fetch available tools from MCP server
    try:
        yield f"data: {json.dumps({'status': 'info', 'message': 'Connecting to Data Refinery...'})}\n\n"

        tools = await data_refinery_mcp.list_tools()
        yield f"data: {json.dumps({'status': 'info', 'message': f'Discovered {len(tools)} tools.'})}\n\n"


    except Exception as e:
        yield f"data: {json.dumps({'status': 'error', 'message': f'Failed to connect to tools: {e}'})}\n\n"


        return

    # 2. Add System Prompt instructing the agent to use tools
    system_prompt = f"You are an AI Data Analyst. You have access to tools to process data. The user has uploaded a file at URI: {request.file_uri}. Always start by inspecting the dataset using `inspect_dataset`."
    messages = [{"role": "system", "content": system_prompt}] + [m.model_dump() for m in request.messages]

    max_iterations = 5
    for i in range(max_iterations):
        yield f"data: {json.dumps({'status': 'thinking', 'message': 'Analyzing prompt and selecting tool...'})}\n\n"


        
        chat_req = ChatCompletionRequest(
            messages=[Message(**m) for m in messages],
            tools=tools
        )
        
        try:
            # Send to LM Studio
            response = await llm_client.chat_completion(chat_req)
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': f'LLM Error: {e}'})}\n\n"


            return
            
        choice = response.choices[0]
        message = choice.message
        
        # Append assistant message to history
        messages.append(message.model_dump(exclude_none=True))
        
        # If the LLM wants to call tools
        if message.tool_calls:
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)
                
                yield f"data: {json.dumps({'status': 'executing', 'message': f'Running tool {func_name}...', 'tool': func_name, 'args': func_args})}\n\n"


                
                try:
                    # Execute tool via MCP
                    tool_result = await data_refinery_mcp.call_tool(func_name, func_args)
                    
                    yield f"data: {json.dumps({'status': 'success', 'message': f'Tool {func_name} completed.', 'result': tool_result})}\n\n"

                    
                    # Append tool result to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result
                    })
                except Exception as e:
                    error_msg = f"Error running {func_name}: {e}"
                    yield f"data: {json.dumps({'status': 'error', 'message': error_msg})}\n\n"


                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": error_msg
                    })
        else:
            # Agent replied with standard text (Final answer)
            yield f"data: {json.dumps({'status': 'complete', 'message': message.content})}\n\n"


            break
            
    else:
         yield f"data: {json.dumps({'status': 'error', 'message': 'Reached maximum reasoning iterations.'})}\n\n"



@router.post("/run")
async def run_agent(request: AgentRunRequest, client: LLMClientDep):
    return StreamingResponse(agent_loop(request, client), media_type="text/event-stream")
