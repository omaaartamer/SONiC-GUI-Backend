import asyncssh
from fastapi import APIRouter, WebSocket
from app.services.SSH_Services import handle_ssh_session, switch_status

router = APIRouter()

@router.websocket("/ws/ssh")
async def ssh_websocket(websocket: WebSocket):
    await websocket.accept()
    await handle_ssh_session(websocket)


@router.websocket("/ws/cpu_status")
async def cpu_percentage(websocket: WebSocket):
    await websocket.accept()
    await switch_status(websocket)
