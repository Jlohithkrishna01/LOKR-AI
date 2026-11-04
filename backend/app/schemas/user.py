from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
import re

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    profile_image: Optional[str] = None
    bio: Optional[str] = None
    provider: Optional[str] = "email"
    provider_id: Optional[str] = None
    google_id: Optional[str] = None
    apple_id: Optional[str] = None
    preferred_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None

    @field_validator("name")
    def validate_name(cls, v: Optional[str]):
        if v is not None:
            v = v.strip()
            if len(v) < 2:
                raise ValueError("Name must be at least 2 characters long.")
        return v

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long.")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter.")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number.")
        return v

    @field_validator("confirm_password")
    def passwords_match(cls, v: str, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("New passwords do not match.")
        return v
