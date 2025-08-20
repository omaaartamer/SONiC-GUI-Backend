from fastapi import APIRouter
from app.models.User import UserCreate, UserLoginResponse,UserLogin
from app.services.Auth_Services import signup as signup_service, login as login_service


router = APIRouter()

@router.post("/signup", response_model=str)
async def signup(user: UserCreate):
        return signup_service(user)
    
@router.post("/login", response_model=UserLoginResponse)
async def login(user: UserLogin):
    return login_service(user)

