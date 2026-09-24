from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr
from app.models import AuthProvider, InviteMethod, PropertyWorkerStatus, Role


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    assigned_property_id: Optional[str] = None
    invited_via: Optional[InviteMethod] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    device_info: Optional[str] = None
    ip_address: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: Role
    user_id: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    role: Role
    auth_provider: AuthProvider
    assigned_property_id: Optional[str] = None
    worker_status: Optional[PropertyWorkerStatus] = None
    created_at: datetime