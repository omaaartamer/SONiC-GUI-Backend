from fastapi import APIRouter, WebSocket
from app.services.SSH_Services import handle_ssh_session

router = APIRouter()

@router.websocket("/ws/ssh")
async def ssh_websocket(websocket: WebSocket):
    await websocket.accept()
    await handle_ssh_session(websocket)
