from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    password: str = Field(..., min_length=8, max_length=128)
    email: EmailStr
    role: Literal["admin","user"]

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    message: str

class UserLogin(BaseModel):
    username: str
    password: str

