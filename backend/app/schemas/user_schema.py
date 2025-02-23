from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    identifier: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

class UserVerification(BaseModel):
    email: EmailStr

class UserToken(BaseModel):
    access_token: str
