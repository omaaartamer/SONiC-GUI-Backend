from fastapi import APIRouter, WebSocket
from app.services.Chatbot_Services import chatbot_service

router = APIRouter()

@router.websocket("/chat/{username}")
async def chatbot(websocket: WebSocket, username: str):
    await chatbot_service(websocket, username)
