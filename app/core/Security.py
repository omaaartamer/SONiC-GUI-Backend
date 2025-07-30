from dotenv import load_dotenv
from datetime import timedelta,datetime,timezone
from fastapi import HTTPException, status, Depends
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer
from jose import JWTError, jwt
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

load_dotenv()
SECRET_KEY =os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"])
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Verify a password on login
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password,hashed_password)


def get_current_user(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return {"username ": username,"role ": role}
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    
def is_admin(current_user:dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="admins only")
    return current_user
