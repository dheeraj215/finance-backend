from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import LoginRequest, TokenResponse
from app.services.user_service import authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse, summary="Login and get access token")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email and password.
    Returns a Bearer JWT token valid for 24 hours.
    """
    token, user = authenticate_user(db, payload.email, payload.password)
    return TokenResponse(access_token=token, user=user)
