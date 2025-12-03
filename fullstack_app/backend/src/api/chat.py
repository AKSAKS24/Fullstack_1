"""
Chat completion endpoints.  These routes handle normal conversation mode
without invoking any agents.  Clients can specify the model provider and name.
Streaming via Server‑Sent Events (SSE) is supported for progressive token output.
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from ..models.providers import get_model


router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., description="Conversation history including the latest user message")
    model: str = Field("gpt-3.5-turbo", description="Model name to use")
    stream: bool = Field(False, description="Whether to stream responses via SSE")


async def generate_completion(messages: List[Dict[str, str]], model_name: str) -> str:
    # Flatten messages into a prompt; for demonstration we simply join user messages
    prompt = "\n".join([m["content"] for m in messages if m["role"] == "user"])
    model = get_model(model_name)
    return await model.generate(prompt)


@router.post("/completions")
async def chat_completions(request: ChatRequest):
    """
    Generate a chat completion.  If `stream` is true, return a streaming response
    that yields tokens as they become available.
    """
    try:
        if request.stream:
            async def event_generator():
                text = await generate_completion([m.dict() for m in request.messages], request.model)
                # Simple streaming: yield each sentence as a separate SSE event
                for chunk in text.split(". "):
                    yield f"data: {chunk}\n\n"
            return StreamingResponse(event_generator(), media_type="text/event-stream")
        else:
            text = await generate_completion([m.dict() for m in request.messages], request.model)
            return JSONResponse({"result": text})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))