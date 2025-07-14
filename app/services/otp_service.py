from datetime import datetime, timedelta
import random
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage
from app.db.mongo import users,otps
from fastapi import HTTPException

load_dotenv()

def generate_otp() -> int:
    return random.randint(100000, 999999)


def send_otp_email(to_email: str, otp: str):
    EMAIL = os.getenv("EMAIL_ADDRESS")
    PASSWORD = os.getenv("EMAIL_PASSWORD")
    msg = EmailMessage()
    msg['Subject'] = "Your OTP Code"
    msg['From'] = EMAIL
    msg['To'] = to_email
    msg.set_content(f"Your OTP is: {otp}. It expires in 5 minutes.")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL,PASSWORD) # type: ignore
        smtp.send_message(msg)

async def handle_otp_request(email: str, user_id:str, intent: str):
        # Generate a 6-digit OTP
    otp_code = generate_otp()

    # Prepare OTP document for storage
    otp_entry = {
        "otp": otp_code,
        "user_id": user_id.lower(),
        "intent": intent,  # 'signup' or 'login'
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }
    await otps.delete_many({"user_id": user_id.lower()})
    await otps.insert_one(otp_entry)

    # Send the OTP via email (function must be implemented separately)
    await send_otp_email(email, otp_code)  # type: ignore if needed

    return {"message": "OTP sent to your email"}


async def verify_otp(user_id:str, otp:str):
    """
    Verifies the provided OTP against the stored one.
    Returns different messages based on the intent (signup/login).
    """

    # Fetch OTP record from database
    db_otp = await otps.find_one({"user_id": user_id.lower()})

    if not db_otp:
        raise HTTPException(status_code=404, detail="OTP not found for this user")

    # Check if OTP is expired
    if datetime.utcnow() > db_otp["expires_at"]:
        raise HTTPException(status_code=400, detail="OTP has expired")

    # Check if OTP matches
    if db_otp["otp"] != otp:
        raise HTTPException(status_code=400, detail="Wrong OTP")

    # Optionally delete OTP after verification
    await otps.delete_one({"user_id": user_id.lower()})

    # Return appropriate message based on intent
    intent=db_otp.get("intent")
    if not intent:
        raise HTTPException(status_code=400, detail="Intent not specified in OTP record")
    return {
        "message": f"{intent.capitalize()} verified successfully"
    }