import firebase_admin
from firebase_admin import auth, credentials
from src.core.config import settings
from src.core.exceptions import AppError

def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)

def verify_phone_token(id_token: str, expected_phone: str) -> None:
    if not id_token:
        raise AppError("OTP_REQUIRED", 401, "Phone verification is required.")

    # Mock OTP tokens are accepted only in development.
    if settings.ENVIRONMENT == "development" and id_token in {
        "dev-bypass-token",
        "mock-firebase-id-token",
    }:
        return

    try:
        decoded_token = auth.verify_id_token(id_token)
    except Exception as exc:
        raise AppError(
            "OTP_INVALID",
            401,
            "Phone verification failed. Please verify your phone number again.",
        ) from exc

    firebase_phone = decoded_token.get("phone_number")
    if not firebase_phone:
        raise AppError(
            "OTP_INVALID",
            401,
            "Phone verification token does not include a phone number.",
        )
    if firebase_phone != expected_phone:
        raise AppError(
            "OTP_PHONE_MISMATCH",
            400,
            "Verified phone number does not match the submitted phone number.",
        )