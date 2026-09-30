from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional
from datetime import datetime

UserRole = Literal[
    "AYUSH Practitioner",
    "Legal Researcher",
    "IP Consultant",
    "Academic Researcher",
    "MSME / Startup Founder",
]


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = Field(default="AYUSH Practitioner")
    full_name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = Field(default="AYUSH Practitioner")

class UserProfileResponse(BaseModel):
    id: str
    email: str
    role: str
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
    message: Optional[str] = None
