from fastapi import APIRouter, WebSocket, Depends
from app.services.Chatbot_Services import chatbot_service
from app.core.Security import get_current_user

router = APIRouter()

@router.websocket("/chat/{username}")
async def chatbot(websocket: WebSocket, username: str, user: dict = Depends(get_current_user)):
    await chatbot_service(websocket, username)
