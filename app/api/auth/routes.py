from fastapi import APIRouter, HTTPException
from app.models.user import UserCreate, UserResponse
from app.db.mongo import db

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    # Insert new user into the database
    result = await db.users.insert_one(user.dict())
    return {"message": "User created successfully", "id": str(result.inserted_id)
            , "username": user.username, "email": user.email,
            "message": "User created successfully"}