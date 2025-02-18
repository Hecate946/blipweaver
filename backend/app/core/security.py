import jwt
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError

load_dotenv()

# Secret key and algorithm for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expires in 1 hour
EMAIL_VERIFY_EXPIRE_HOURS = 24 

# Set up bcrypt hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Set up OAuth2PasswordBearer for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    """Hash a password securely using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

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
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
def create_email_verification_token(email: str):
    """Generate a token for email verification"""
    expire = datetime.utcnow() + timedelta(hours=EMAIL_VERIFY_EXPIRE_HOURS)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_email_token(token: str):
    """Decode and validate email verification token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.PyJWTError:
        return None  # Invalid token
    