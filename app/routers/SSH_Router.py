from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.SSH_Services import handle_ssh_session, switch_status
from app.core.Security import verify_token
import json

router = APIRouter()

@router.websocket("/ws/ssh")
async def ssh_websocket(websocket: WebSocket):
    await websocket.accept()
    
    try:
        auth_data = await websocket.receive_text()
        auth_info = json.loads(auth_data)
        
        token = auth_info.get("token")
        password = auth_info.get("password")
        
        if not token or not password:
            await websocket.send_text("** Authentication required: token and password **")
            await websocket.close()
            return
            
        try:
            verify_token(token)
        except Exception as e:
            await websocket.send_text(f"** Authentication failed: {str(e)} **")
            await websocket.close()
            return
            
        await handle_ssh_session(websocket, token, password)
        
    except WebSocketDisconnect:
        pass
    except json.JSONDecodeError:
        await websocket.send_text("** Invalid authentication format **")
        await websocket.close()
    except Exception as e:
        await websocket.send_text(f"** Error: {str(e)} **")
        await websocket.close()


@router.websocket("/ws/cpu_status")
async def cpu_percentage(websocket: WebSocket):
    await websocket.accept()
    await switch_status(websocket)

