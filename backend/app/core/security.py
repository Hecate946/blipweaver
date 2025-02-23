import jwt
import os
import logging
import hashlib
import base64
import hmac
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, ExpiredSignatureError

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expires in 1 hour
EMAIL_VERIFY_EXPIRE_HOURS = 24 

# Set up OAuth2PasswordBearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2_HMAC with SHA256.
    Returns the salt and hash combined, separated by a '$'.
    """
    salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    salt_b64 = base64.b64encode(salt).decode('utf-8')
    hash_b64 = base64.b64encode(pwd_hash).decode('utf-8')
    return f"{salt_b64}${hash_b64}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against the stored hash.
    The stored hash should be in the format: salt$hash (both base64 encoded).
    """
    try:
        salt_b64, hash_b64 = hashed_password.split('$')
        salt = base64.b64decode(salt_b64.encode('utf-8'))
        stored_hash = base64.b64decode(hash_b64.encode('utf-8'))
        computed_hash = hashlib.pbkdf2_hmac('sha256', plain_password.encode(), salt, 100000)
        return hmac.compare_digest(computed_hash, stored_hash)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Generate a JWT token for authentication."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str = Security(oauth2_scheme)):
    """Verify the JWT token and extract user information."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # The token is valid, return user info
    except PyJWTError:
        logger.error("Access token is invalid or expired")
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
def create_email_verification_token(email: str):
    """Generate a token for email verification."""
    expire = datetime.utcnow() + timedelta(hours=EMAIL_VERIFY_EXPIRE_HOURS)
    token = jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Created email verification token for {email} expiring at {expire}")
    return token

def verify_email_token(token: str):
    """Decode and validate email verification token.
    
    Returns the email (the 'sub' field) if successful.
    If the token is expired or invalid, logs the error and returns None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except ExpiredSignatureError:
        logger.error("Email verification token has expired")
        return None  # Token expired
    except PyJWTError as e:
        logger.error(f"Invalid email verification token: {e}")
        return None  # Invalid token
