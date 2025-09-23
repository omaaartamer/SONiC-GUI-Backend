from fastapi import APIRouter, WebSocket, Depends
from app.services.SSH_Services import handle_ssh_session ,switch_status
from app.core.Security import get_current_user

router = APIRouter()

@router.websocket("/cli/{username}")
async def cli(websocket: WebSocket, username: str, user: dict = Depends(get_current_user)):
    await handle_ssh_session(websocket, username)

@router.websocket("/status/{username}")
async def cpu_percentage(websocket: WebSocket, username: str):
    await switch_status(websocket, username)

