from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.user import UserCreate, UserResponse,UserLogin, UserLoginResponse
from app.db.mongo import db
from app.services.auth_services import verify_password, hash_pasword
from app.core.limiter import limiter
from app.core.security import create_access_token, get_current_user

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
@limiter.limit("5/minute")
async def signup(request: Request,user: UserCreate):
    # Check if user already exists
    db_user = await db.users.find_one({"username": user.username})
    email_exists = await db.users.find_one({"email": user.email.lower()})
    if db_user:
        raise HTTPException(status_code=401, detail="Username already exists")
    elif  email_exists:
        raise HTTPException(status_code=401, detail="email already exists")

    # Insert new user into the database with hased password
    hashed_pw = hash_pasword(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_pw
    del user_data["password"]

    result = await db.users.insert_one(user_data)
    return {
        "message": "User created successfully",
        "id": str(result.inserted_id),
        "username": user.username.lower(),
        "email": user.email.lower,
        "role": "user"
    }


@router.post("/login", response_model=UserLoginResponse)
@limiter.limit("5/minute")
async def login(request: Request,user: UserLogin):
    
    # Check if user already exists
    db_user = await db.users.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=401,detail="User does not exist")
    
    elif not verify_password(user.password,db_user["hashed_password"]):
        raise HTTPException(status_code=401,detail="invalid password")
    
    access_token = create_access_token(data={"sub": db_user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.put("admin/chaneRole/{username}")
async def changeRole(username:str, current_user=Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change the role of a user")
    result = await db.users.update_one({"username": username}, {"$set": {"role": "admin"}})
    if result.modified_count == 0:
        raise HTTPException(status_code=404,detail="User not found or is already an admin")
    return {
        "message": f"Role of '{username}' changed to admin"
    }

