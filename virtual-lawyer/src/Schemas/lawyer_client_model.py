"""
Pydantic models for Lawyer-Client relationship validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class LawyerClientBase(BaseModel):
    """Base lawyer-client model with common fields"""
    lawyerId: str = Field(..., description="Lawyer ID")
    clientId: str = Field(..., description="Client/Citizen user ID")
    clientName: str = Field(..., description="Client name")
    clientEmail: EmailStr = Field(..., description="Client email")
    clientPhone: Optional[str] = Field(None, max_length=20, description="Client phone")
    caseType: Optional[str] = Field(None, description="Type of case")
    status: str = Field(default="Active", description="Relationship status: Active, Inactive, Closed")


class LawyerClientCreate(LawyerClientBase):
    """Model for creating a new lawyer-client relationship"""
    activeCases: int = Field(default=0, ge=0, description="Number of active cases")
    totalCases: int = Field(default=0, ge=0, description="Total cases together")


class LawyerClientUpdate(BaseModel):
    """Model for updating lawyer-client relationship (all fields optional)"""
    clientName: Optional[str] = None
    clientEmail: Optional[EmailStr] = None
    clientPhone: Optional[str] = Field(None, max_length=20)
    caseType: Optional[str] = None
    status: Optional[str] = None
    activeCases: Optional[int] = Field(None, ge=0)
    totalCases: Optional[int] = Field(None, ge=0)


class LawyerClientResponse(LawyerClientBase):
    """Lawyer-client model for API responses"""
    activeCases: int = 0
    totalCases: int = 0
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

