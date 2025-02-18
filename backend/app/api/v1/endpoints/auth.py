import logging
from fastapi import APIRouter, HTTPException, Depends
from app.repositories.user_repository import create_user, get_user_by_username_or_email, get_user_by_email, get_user_by_username
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token, verify_access_token
from app.core.logger import logger  # Import logger

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    """User signup endpoint ensuring unique username and email."""
    logger.info(f"Signup attempt for username: {user.username}, email: {user.email}")

    existing_email = await get_user_by_email(user.email)
    if existing_email:
        logger.warning(f"Signup failed: Email {user.email} already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await get_user_by_username(user.username)
    if existing_username:
        logger.warning(f"Signup failed: Username {user.username} already taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = await create_user(user.username, user.email, hashed_password)

    logger.info(f"Signup successful for username: {user.username}, email: {user.email}")
    return UserResponse(**new_user)

@router.post("/login")
async def login(user: UserLogin):
    """Allow login with either username or email"""
    logger.info(f"Login attempt for identifier: {user.identifier}")

    db_user = await get_user_by_username_or_email(user.identifier)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        logger.warning(f"Login failed for identifier: {user.identifier}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user["is_verified"]:
        logger.warning(f"Login failed: User {user.identifier} not verified")
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token({"sub": db_user["email"]})
    logger.info(f"Login successful for identifier: {user.identifier}")

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected")
async def protected_route(user: dict = Depends(verify_access_token)):
    """Example of a protected route."""
    logger.info(f"Protected route accessed by: {user['sub']}")
    return {"message": "You have access!", "user": user}
