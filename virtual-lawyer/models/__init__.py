"""
Pydantic models for request/response validation
"""
from .user_model import UserCreate, UserUpdate, UserResponse, UserInDB
from .lawyer_model import LawyerCreate, LawyerUpdate, LawyerResponse, LawyerInDB
from .case_model import CaseCreate, CaseUpdate, CaseResponse
from .lawyer_client_model import LawyerClientCreate, LawyerClientUpdate, LawyerClientResponse
from .admin_settings_model import AdminSettingsUpdate, AdminSettingsResponse

__all__ = [
    # User models
    'UserCreate',
    'UserUpdate',
    'UserResponse',
    'UserInDB',
    # Lawyer models
    'LawyerCreate',
    'LawyerUpdate',
    'LawyerResponse',
    'LawyerInDB',
    # Case models
    'CaseCreate',
    'CaseUpdate',
    'CaseResponse',
    # Lawyer-Client models
    'LawyerClientCreate',
    'LawyerClientUpdate',
    'LawyerClientResponse',
    # Admin Settings models
    'AdminSettingsUpdate',
    'AdminSettingsResponse',
]

