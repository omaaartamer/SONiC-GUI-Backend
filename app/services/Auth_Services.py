import os
import asyncssh
from fastapi import HTTPException
from app.models.User import UserCreate
from app.db.tiny import users_table, User
from app.core.Security import hash_password, create_access_token, verify_password
from dotenv import load_dotenv
from app.services.SSH_Services import ssh_sessions

load_dotenv()
SSH_SWITCH_IP = os.getenv("SONIC_SWITCH_IP")

def signup(user: UserCreate):
    db_user = users_table.get(User.username == user.username.lower())
    email_exists = users_table.get(User.email == user.email.lower())

    if db_user:
        raise HTTPException(
            status_code=409,
            detail=[{"loc": ["body", "username"], "msg": "Username already exists"}]
        )
    elif email_exists:
        raise HTTPException(
            status_code=409,
            detail=[{"loc": ["body", "email"], "msg": "Email already exists"}]
        )


    hashed_pw = hash_password(user.password)
    user_data = user.model_dump()
    user_data["hashed_password"] = hashed_pw
    del user_data["password"]

    user_data["role"] = "admin"

    users_table.insert(user_data)

    print("Using DB file:", os.getenv("DB_PATH"))

    return "User created successfully"



async def login(websocket):
    await websocket.accept()
    try:
        creds = await websocket.receive_json()
        username = creds["username"]
        password = creds["password"]

        db_user = users_table.get(User.username == username.lower())
        hashed_pw = db_user.get("hashed_password") if db_user else None

        if not db_user or not hashed_pw or not verify_password(password, hashed_pw):
            await websocket.send_json({"error": "Invalid username or password"})
            await websocket.close()
            return

        access_token = create_access_token(
            data={"sub": db_user["username"], "role": db_user["role"]}
        )
        
        
        conn = await asyncssh.connect(
            SSH_SWITCH_IP,
            username=username,
            password=password
        )

        ssh_sessions[username] = conn

        await websocket.send_json({
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Login successful, SSH session ready"
        })

    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()