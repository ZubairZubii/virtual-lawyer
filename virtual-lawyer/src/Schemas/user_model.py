"""
Pydantic models for User (Citizen) validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    role: str = Field(default="Citizen", description="User role")
    status: str = Field(default="Active", description="Account status: Active, Pending, Suspended")


class UserCreate(UserBase):
    """Model for creating a new user"""
    password: str = Field(..., min_length=6, description="Password (will be hashed)")
    joinDate: Optional[str] = Field(None, description="Registration date (ISO format)")


class UserUpdate(BaseModel):
    """Model for updating user (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=6)
    status: Optional[str] = None
    casesInvolved: Optional[int] = Field(None, ge=0)


class UserInDB(UserBase):
    """User model as stored in database"""
    id: str = Field(..., description="User ID")
    password: str = Field(..., description="Hashed password")
    casesInvolved: int = Field(default=0, ge=0, description="Number of cases")
    joinDate: str = Field(..., description="Registration date")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """User model for API responses (password excluded)"""
    id: str
    casesInvolved: int = 0
    joinDate: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

