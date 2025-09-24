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


# @router.post("/login", summary="HTTP login for Swagger and frontend")
# async def login_http(form_data: OAuth2PasswordRequestForm = Depends()):
#     db_user = users_table.get(User.username == form_data.username.lower())
#     if not db_user or not verify_password(form_data.password, db_user["hashed_password"]):
#         raise HTTPException(status_code=401, detail="Invalid username or password")

#     token = create_access_token(data={"sub": db_user["username"], "role": db_user["role"]})
#     return {"access_token": token, "token_type": "bearer"}