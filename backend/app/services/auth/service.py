import secrets
from fastapi import status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from src.core.firebase import verify_phone_token
from src.core.exceptions import AppError
from src.core.security import hash_password
from src.services.auth.schema import (
    AvailabilityCheckRequest,
    AvailabilityResponse,
    SignupRequest,
)
from src.shared.db.models.user import AppUser

def generae_user_id() -> str:
    return f"{secrets.randbelow(10**6):06d}"

class AuthService:
    @staticmethod
    def check_availability(db: DBSession, data: AvailabilityCheckRequest) -> AvailabilityResponse:
        existing_user = db.query(AppUser).filter(
            or_(AppUser.email == data.email, AppUser.phone == data.phone)
        ).first()
        
        if existing_user:
            if existing_user.email == data.email:
                return AvailabilityResponse(
                    is_available=False,
                    detail="This email is already registered.",
                    conflict_field="email",
                )
            return AvailabilityResponse(
                is_available=False,
                detail="This phone number is already registered.",
                conflict_field="phone",
            )
            
        return AvailabilityResponse(is_available=True)

    @staticmethod
    def register(db: DBSession, data: SignupRequest) -> AppUser:
        # 1. Final duplicate check to prevent race conditions
        availability = AuthService.check_availability(db, AvailabilityCheckRequest(email=data.email, phone=data.phone))
        if not availability.is_available:
            AuthService._raise_availability_error(availability)

        # 2. Verify Firebase OTP Token
        verify_phone_token(id_token=data.firebase_id_token, expected_phone=data.phone)

    
        new_user = AppUser(
            id=generae_user_id(),
            firstName=data.firstName,
            lastName=data.lastName,
            email=data.email,
            phone=data.phone,
            isPhoneVerified=True,
            passwordHash=hash_password(data.password),
            userRole=data.role,
        )

        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            availability = AuthService.check_availability(
                db,
                AvailabilityCheckRequest(email=data.email, phone=data.phone),
            )
            if not availability.is_available:
                AuthService._raise_availability_error(availability)
            raise
        return new_user

    @staticmethod
    def _raise_availability_error(availability: AvailabilityResponse) -> None:
        field = availability.conflict_field
        if field == "email":
            raise AppError(
                "EMAIL_TAKEN",
                status.HTTP_409_CONFLICT,
                availability.detail or "This email is already registered.",
            )
        if field == "phone":
            raise AppError(
                "PHONE_TAKEN",
                status.HTTP_409_CONFLICT,
                availability.detail or "This phone number is already registered.",
            )
        raise AppError(
            "ACCOUNT_CONFLICT",
            status.HTTP_409_CONFLICT,
            "An account with these details is already registered.",
        )
