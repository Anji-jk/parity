
from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field

from src.shared.db.enums.role import Role

class SignupRequest(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: str
    password: str
    role: Role
    firebase_id_token: str = Field(
        validation_alias=AliasChoices("firebaseIdToken", "firebase_id_token")
    )

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    firstName: str = Field(validation_alias=AliasChoices("firstName", "firstName"))
    lastName: str = Field(validation_alias=AliasChoices("lastName", "lastName"))
    email: str
    phone: Optional[str] = None
    role: Role = Field(validation_alias=AliasChoices("role", "userRole"))


class AvailabilityCheckRequest(BaseModel):
    email: EmailStr
    phone: str


class AvailabilityResponse(BaseModel):
    is_available: bool
    detail: Optional[str] = None
    conflict_field: Optional[Literal["email", "phone"]] = None
    