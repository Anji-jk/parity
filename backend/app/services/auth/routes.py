from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DBSession

from app.shared.db.config.session import get_db
from app.services.auth.schema import SignupRequest, UserResponse
from app.services.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignupRequest, db: DBSession = Depends(get_db)):
    return AuthService.register(db=db, data=data)
