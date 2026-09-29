from typing import Literal, Optional
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator
from app.shared.db.enums.role import Role


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


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def check_identifier(self):
        if not self.email and not self.phone:
            raise ValueError("Either email or phone must be provided for login.")
        return self


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str