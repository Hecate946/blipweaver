import os
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from dotenv import load_dotenv

load_dotenv()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True
)

async def send_verification_email(email: str, token: str):
    """Send email verification link"""
    verify_url = f"http://127.0.0.1:8000/auth/verify-email?token={token}"
    message = MessageSchema(
        subject="BlipWeaver Email Verification",
        recipients=[email],
        body=f"Click the link to verify your email: {verify_url}",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
