from pydantic import BaseModel, Field
from datetime import datetime

class OTPRequest(BaseModel):
    user_id: str
    email: str
    intent: str  # e.g., "signup" or "login"

class OTPEntry(BaseModel):
    otp: int
    user_id: str
    expires_at: datetime
    intent: str

class OTPVerification(BaseModel):
    user_id: str
    otp: int
