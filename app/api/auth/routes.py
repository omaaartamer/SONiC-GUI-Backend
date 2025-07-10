from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserResponse,UserLogin
from app.db.mongo import db,users
from app.services.auth_services import verify_password, hash_pasword

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    # Check if user already exists
    db_user = await users.find_one({"username": user.username})
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Insert new user into the database with hased password
    hashed_pw = hash_pasword(user.password)
    user_data = user.dict()
    user_data["hashed_password"] = hashed_pw
    del user_data["password"]

    result = await users.insert_one(user_data)
    return {
        "message": "User created successfully",
        "id": str(result.inserted_id),
        "username": user.username,
        "email": user.email
    }


@router.post("/login", response_model=UserResponse)
async def login(user: UserLogin):
    
    # Check if user already exists
    db_user = await users.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=401,detail="User does not exist")
    
    elif not verify_password(user.password,db_user["hashed_password"]):
        raise HTTPException(status_code=401,detail="invailed password")
    
    return {
        "message": "Login successful",
        "id": str(db_user["_id"]),
        "username": db_user["username"],
        "email": db_user["email"]
    }