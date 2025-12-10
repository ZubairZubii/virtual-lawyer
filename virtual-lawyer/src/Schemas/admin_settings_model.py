"""
Pydantic models for Admin Settings validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class AdminSettingsBase(BaseModel):
    """Base admin settings model"""
    platform_name: str = Field(..., description="Platform name")
    support_email: EmailStr = Field(..., description="Support email address")
    max_file_upload_size_mb: int = Field(default=50, ge=1, le=1000, description="Max file upload size in MB")
    email_notifications: bool = Field(default=True, description="Enable email notifications")
    ai_monitoring: bool = Field(default=True, description="Enable AI monitoring")
    auto_backup: bool = Field(default=True, description="Enable automatic backups")
    maintenance_mode: bool = Field(default=False, description="Maintenance mode flag")


class AdminSettingsUpdate(BaseModel):
    """Model for updating admin settings (all fields optional)"""
    platform_name: Optional[str] = None
    support_email: Optional[EmailStr] = None
    max_file_upload_size_mb: Optional[int] = Field(None, ge=1, le=1000)
    email_notifications: Optional[bool] = None
    ai_monitoring: Optional[bool] = None
    auto_backup: Optional[bool] = None
    maintenance_mode: Optional[bool] = None


class AdminSettingsResponse(AdminSettingsBase):
    """Admin settings model for API responses"""
    updatedAt: datetime

    class Config:
        from_attributes = True

