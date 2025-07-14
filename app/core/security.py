import os
import bcrypt
from dotenv import load_dotenv
from datetime import timedelta,datetime,timezone
from fastapi import status, Depends, HTTPException
from app.db.mongo import users
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer
from jose import jwt, JWTError

#hasing the password using bcrypt
#salt is added to randomise and prevent the same password having the same hashing
# This tells FastAPI where to get the token from
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

load_dotenv()
SECRET_KEY =os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

def hash_pasword(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'),salt)
    return hashed.decode('utf-8')

# Verify a password on login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))