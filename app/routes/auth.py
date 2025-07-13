from fastapi import APIRouter, Depends, HTTPException, Request
from app.models.user import UserCreate, UserLoginResponse,UserLogin
from app.db.mongo import db,users,otps
from app.core.limiter import limiter
from pymongo.errors import PyMongoError
from app.models.otp import OTPRequest, OTPVerification
from app.services.otp_service import handle_otp_request as otpRequest_service, verify_otp as verify_otp_service
from app.core.security import  get_current_user
from app.services.auth_services import signup as signup_service, login as login_service


router = APIRouter()

@router.post("/signup", response_model=UserLoginResponse)
@limiter.limit("5/minute")
async def signup(request: Request,user: UserCreate):
    try:
        return await signup_service(user)
    
    except HTTPException as e: #for errors raised in services to be passed here
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

@router.post("/login", response_model=UserLoginResponse)
@limiter.limit("5/minute")
async def login(request: Request,user: UserLogin):
    
    try:
        return await login_service(user)
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


@router.put("/admin/changeRole/{username}")
async def change_role(username: str, new_role: str, current_user=Depends(get_current_user)):

    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can change user roles")


    result = await users.update_one(
        {"username": username},
        {"$set": {"role": new_role}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or role is already set")

    return {"message": f"Role of '{username}' changed to '{new_role}'"}


@router.post("/request-otp")
async def request_otp(data: OTPRequest):
    try:
        return await otpRequest_service(data.email, data.user_id, data.intent)
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    


@router.post("/verify-otp")
async def verify_otp(data: OTPVerification):
    try:
        return await verify_otp_service(data.user_id, data.otp)
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
    except PyMongoError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
@router.get("/debug-users")
async def debug_users():
    users_list = await users.find().to_list(5)
    
    # Convert ObjectId to string for each user
    for user in users_list:
        user["_id"] = str(user["_id"])
    
    return users_list

