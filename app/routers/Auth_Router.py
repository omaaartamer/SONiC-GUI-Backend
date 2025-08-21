from fastapi import APIRouter, WebSocket
from app.models.User import UserCreate
from app.services.Auth_Services import signup as signup_service, login as login_service


router = APIRouter()

@router.post("/signup", response_model=str)
def signup(user: UserCreate):
        return signup_service(user)
    

@router.websocket("/login")
async def login(websocket: WebSocket):
    await login_service(websocket)


