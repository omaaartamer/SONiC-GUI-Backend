from fastapi import APIRouter, WebSocket
from app.services.SSH_Services import handle_ssh_session ,switch_status

router = APIRouter()

@router.websocket("/cli/{username}")
async def cli(websocket: WebSocket, username: str):
    await handle_ssh_session(websocket, username)

@router.websocket("/status/{username}")
async def cpu_percentage(websocket: WebSocket, username: str):
    await switch_status(websocket, username)

