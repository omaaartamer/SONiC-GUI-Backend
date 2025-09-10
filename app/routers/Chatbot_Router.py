from fastapi import APIRouter, Websocket
from app.services.Chatbot_Services import chatbot_service

router = APIRouter()
@router.post("/")
async def chatbot(websocket : Websocket, username : str, temp : str):
    return await chatbot_service(websocket, username)