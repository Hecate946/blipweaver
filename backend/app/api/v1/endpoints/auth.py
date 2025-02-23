import logging
from fastapi import APIRouter, HTTPException, Depends
from app.repositories import user_repository
from app.schemas import user_schema
from app.core import security
from app.core.logger import logger  # Import logger

router = APIRouter()

@router.post("/signup", response_model=user_schema.UserResponse)
async def signup(user: user_schema.UserCreate):
    """User signup endpoint ensuring unique username and email."""
    logger.info(f"Signup attempt for username: {user.username}, email: {user.email}")

    existing_email = await user_repository.get_user_by_email(user.email)
    if existing_email:
        logger.warning(f"Signup failed: Email {user.email} already registered")
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await user_repository.get_user_by_username(user.username)
    if existing_username:
        logger.warning(f"Signup failed: Username {user.username} already taken")
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = security.hash_password(user.password)
    new_user = await user_repository.create_user(user.username, user.email, hashed_password)

    logger.info(f"Signup successful for username: {user.username}, email: {user.email}")
    return user_schema.UserResponse(**new_user)

@router.post("/login")
async def login(user: user_schema.UserLogin):
    """Allow login with either username or email"""
    logger.info(f"Login attempt for identifier: {user.identifier}")

    db_user = await user_repository.get_user_by_username_or_email(user.identifier)
    if not db_user or not security.verify_password(user.password, db_user["hashed_password"]):
        logger.warning(f"Login failed for identifier: {user.identifier}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user["is_verified"]:
        logger.warning(f"Login failed: User {user.identifier} not verified")
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = security.create_access_token({"sub": db_user["email"]})
    logger.info(f"Login successful for identifier: {user.identifier}")

    return {"access_token": access_token}

@router.get("/protected")
async def protected_route(user: dict = Depends(security.verify_access_token)):
    """Example of a protected route."""
    logger.info(f"Protected route accessed by: {user['sub']}")
    return {"message": "You have access!", "user": user}

@router.post("/request-email-verification")
async def request_email_verification(user: user_schema.UserVerification):
    """
    Generate an email verification token for the provided email.
    """
    token = security.create_email_verification_token(user.email)
    return {"verification_token": token}

@router.post("/verify-email")
async def verify_email(user: user_schema.UserToken):
    """
    Verify the provided email verification token and mark the user as verified.
    """
    token = user.access_token
    verified_email = security.verify_email_token(token)
    if not verified_email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    # Mark the user as verified in the database
    await user_repository.mark_user_verified(verified_email)
    return {"message": "Email verified successfully"}

@router.post("/logout")
async def logout():
    """
    Endpoint for logout.
    For a JWT stateless authentication, logout is handled client-side.
    This endpoint is provided for completeness.
    """
    return {"message": "Logged out successfully"}

@router.delete("/delete-account")
async def delete_account(user: dict = Depends(security.verify_access_token)):
    """
    Delete the account of the currently authenticated user.
    """
    deleted = await user_repository.delete_user(user["sub"])  # 'sub' contains the user's email
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Account deleted successfully"}