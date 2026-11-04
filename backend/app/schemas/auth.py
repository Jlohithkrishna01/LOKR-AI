import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.schemas.user import UserResponse

class UserSignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator("name")
    def validate_name(cls, v: str):
        v = v.strip()
        if len(v) < 2:
            raise ValueError("Full Name must be at least 2 characters long.")
        return v

    @field_validator("password")
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")
        return v

    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info):
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("Passwords do not match.")
        return v

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")
        return v

    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match.")
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class GoogleAuthRequest(BaseModel):
    credential: Optional[str] = None
    access_token: Optional[str] = None
    code: Optional[str] = None

class AppleUserName(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class AppleUserData(BaseModel):
    name: Optional[AppleUserName] = None
    email: Optional[str] = None

class AppleAuthRequest(BaseModel):
    id_token: str
    code: Optional[str] = None
    user: Optional[AppleUserData] = None
