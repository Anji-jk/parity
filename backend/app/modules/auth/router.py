from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session as DBSession

from app.core.dependencies import get_current_user, get_db
from app.models import User
from app.modules.auth.schema import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(data: SignupRequest, db: DBSession = Depends(get_db)):
    return AuthService.register(db=db, data=data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, request: Request, db: DBSession = Depends(get_db)):
    if not data.ip_address and request.client:
        data.ip_address = request.client.host
    if not data.device_info:
        data.device_info = request.headers.get("User-Agent")
    return AuthService.login(db=db, credentials=data)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user