"""
Pydantic models for Case validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CaseBase(BaseModel):
    """Base case model with common fields"""
    case_type: str = Field(..., description="Type of case (e.g., Bail Application, Appeal)")
    court: str = Field(..., description="Court name")
    judge: Optional[str] = Field(None, description="Judge name")
    sections: Optional[List[str]] = Field(default_factory=list, description="Legal sections involved")
    police_station: Optional[str] = Field(None, description="Police station name")
    fir_number: Optional[str] = Field(None, description="FIR number")
    description: Optional[str] = Field(None, description="Case description")
    filing_date: Optional[str] = Field(None, description="Filing date (ISO format)")
    next_hearing: Optional[str] = Field(None, description="Next hearing date (ISO format)")
    status: str = Field(default="Active", description="Case status: Active, Hearing Scheduled, Closed, Urgent")


class CaseCreate(CaseBase):
    """Model for creating a new case"""
    priority: Optional[str] = Field(None, description="Priority: High, Medium, Low (for lawyer cases)")
    client_name: Optional[str] = Field(None, description="Client name (for lawyer cases)")
    deadline: Optional[str] = Field(None, description="Deadline (for lawyer cases)")
    userId: Optional[str] = Field(None, description="Citizen user ID (if citizen case)")
    lawyerId: Optional[str] = Field(None, description="Lawyer ID (if lawyer case)")


class CaseUpdate(BaseModel):
    """Model for updating case (all fields optional)"""
    case_type: Optional[str] = None
    court: Optional[str] = None
    judge: Optional[str] = None
    sections: Optional[List[str]] = None
    police_station: Optional[str] = None
    fir_number: Optional[str] = None
    description: Optional[str] = None
    filing_date: Optional[str] = None
    next_hearing: Optional[str] = None
    deadline: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    documents_count: Optional[int] = Field(None, ge=0)
    assigned_lawyer: Optional[str] = None
    assigned_lawyer_id: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    hours_billed: Optional[int] = Field(None, ge=0)
    client_name: Optional[str] = None


class CaseResponse(CaseBase):
    """Case model for API responses"""
    id: str
    priority: Optional[str] = None
    userId: Optional[str] = None
    lawyerId: Optional[str] = None
    client_name: Optional[str] = None
    documents_count: int = 0
    assigned_lawyer: Optional[str] = None
    assigned_lawyer_id: Optional[str] = None
    progress: int = 0
    deadline: Optional[str] = None
    hours_billed: Optional[int] = None
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

