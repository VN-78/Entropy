from fastapi import APIRouter
from app.api.v1 import chat, files, agent

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
