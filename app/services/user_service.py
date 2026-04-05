from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password, create_access_token


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email, User.is_deleted == False).first()


def list_users(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
):
    query = db.query(User).filter(User.is_deleted == False)

    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def create_user(db: Session, payload: UserCreate) -> User:
    if get_user_by_email(db, payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if payload.name is not None:
        user.name = payload.name
    if payload.role is not None:
        user.role = payload.role
    if payload.is_active is not None:
        user.is_active = payload.is_active

    user.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def soft_delete_user(db: Session, user_id: int) -> None:
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> str:
    """Authenticate credentials and return a JWT access token."""
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact an admin.",
        )

    token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return token, user
