from fastapi import APIRouter, HTTPException, Depends
from app.repositories.user_repository import create_user, get_user_by_username_or_email, get_user_by_email, get_user_by_username
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password,verify_password, create_access_token, verify_access_token
from datetime import timedelta

router = APIRouter()

@router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    """User signup endpoint ensuring unique username and email."""
    existing_email = await get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_username = await get_user_by_username(user.username)
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = hash_password(user.password)
    new_user = await create_user(user.username, user.email, hashed_password)

    return UserResponse(**new_user)


@router.post("/login")
async def login(identifier: str, password: str):
    """Allow login with either username or email"""
    db_user = await get_user_by_username_or_email(identifier)
    if not db_user or not verify_password(password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user["is_verified"]:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token({"sub": db_user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}



@router.get("/protected")
async def protected_route(user: dict = Depends(verify_access_token)):
    """Example of a protected route."""
    return {"message": "You have access!", "user": user}
