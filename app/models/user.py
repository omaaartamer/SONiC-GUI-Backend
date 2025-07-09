from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    message: str

class UserLogin(BaseModel):
    username: str
    password: str

