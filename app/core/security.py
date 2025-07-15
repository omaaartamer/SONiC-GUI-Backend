from dotenv import load_dotenv
from datetime import timedelta,datetime,timezone
from passlib.context import CryptContext
from fastapi.security import  OAuth2PasswordBearer
from jose import jwt
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


def hash_pasword(password: str) -> str:
    return pwd_context.hash(password)

# Verify a password on login
def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password,hashed_password)