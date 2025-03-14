from fastapi import APIRouter
from schemas.chat import ChatRequest
from Controllers.chatController import chat_endpoint


router = APIRouter()

@router.post("/chat_bot/")
async def chat_endpoint_salida(request: ChatRequest):
    return await chat_endpoint(request)
    