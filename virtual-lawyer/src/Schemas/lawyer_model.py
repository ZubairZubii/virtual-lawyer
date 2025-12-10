"""
Pydantic models for Lawyer validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class LawyerBase(BaseModel):
    """Base lawyer model with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    specialization: str = Field(..., description="Primary specialization")
    specializations: List[str] = Field(default_factory=list, description="List of specializations")
    location: Optional[str] = Field(None, max_length=100, description="Location/City")
    yearsExp: int = Field(default=0, ge=0, description="Years of experience")
    verificationStatus: str = Field(default="Pending", description="Verification status: Verified, Pending, Rejected")


class LawyerCreate(LawyerBase):
    """Model for creating a new lawyer"""
    password: str = Field(..., min_length=6, description="Password (will be hashed)")
    joinDate: Optional[str] = Field(None, description="Registration date (ISO format)")


class LawyerUpdate(BaseModel):
    """Model for updating lawyer (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=6)
    specialization: Optional[str] = None
    specializations: Optional[List[str]] = None
    location: Optional[str] = Field(None, max_length=100)
    yearsExp: Optional[int] = Field(None, ge=0)
    verificationStatus: Optional[str] = None
    casesSolved: Optional[int] = Field(None, ge=0)
    cases: Optional[int] = Field(None, ge=0)
    winRate: Optional[int] = Field(None, ge=0, le=100)
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews: Optional[int] = Field(None, ge=0)


class LawyerInDB(LawyerBase):
    """Lawyer model as stored in database"""
    id: str = Field(..., description="Lawyer ID")
    password: str = Field(..., description="Hashed password")
    casesSolved: int = Field(default=0, ge=0, description="Total cases solved")
    cases: int = Field(default=0, ge=0, description="Total cases handled")
    winRate: int = Field(default=0, ge=0, le=100, description="Win rate percentage")
    rating: float = Field(default=0.0, ge=0, le=5, description="Average rating")
    reviews: int = Field(default=0, ge=0, description="Number of reviews")
    joinDate: str = Field(..., description="Registration date")
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True


class LawyerResponse(LawyerBase):
    """Lawyer model for API responses (password excluded)"""
    id: str
    casesSolved: int = 0
    cases: int = 0
    winRate: int = 0
    rating: float = 0.0
    reviews: int = 0
    joinDate: str
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

