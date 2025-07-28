from fastapi import HTTPException
from app.models.User import UserCreate, UserLogin
from app.db.mongo import db,users
from app.core.Security import hash_pasword, create_access_token, verify_password



async def signup(user: UserCreate):
    # Check if user already exists
    db_user = await users.find_one({"username": user.username})
    email_exists = await users.find_one({"email": user.email.lower()})
    if db_user:
        raise HTTPException(status_code=401, detail="Username already exists")
    elif  email_exists:
        raise HTTPException(status_code=401, detail="email already exists")

    # Insert new user into the database with hased password
    hashed_pw = hash_pasword(user.password)
    user_data = user.model_dump()
    user_data["hashed_password"] = hashed_pw
    del user_data["password"]

    user_data["role"] = "admin"


    await users.insert_one(user_data)
    print("Using DB:", db.name)


async def login(user: UserLogin):
    
    # Check if user already exists
    db_user = await users.find_one({"username": user.username})
    hashed_pw= db_user.get("hashed_password") if db_user else None

    if not db_user:
        raise HTTPException(status_code=403, detail="Invalid username or password")

    if not hashed_pw or not verify_password(user.password, hashed_pw):
        raise HTTPException(status_code=403, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": db_user["username"], "role":db_user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        # "username": db_user["username"],
        # "user_id": db_user["user_id"],
        # "role": db_user.get("role", "user") #if no role assigned, default to "user"
    }
