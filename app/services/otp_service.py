import random
import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage


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