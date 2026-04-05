from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently authenticated user."""
    return current_user


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List all users (Admin only)",
    dependencies=[Depends(require_admin)],
)
def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
):
    """List all users with optional filtering. Admin only."""
    total, items = user_service.list_users(db, page, page_size, role, is_active)
    return UserListResponse(total=total, page=page, page_size=page_size, items=items)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user (Admin only)",
    dependencies=[Depends(require_admin)],
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Admin only."""
    return user_service.create_user(db, payload)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user by ID (Admin only)",
    dependencies=[Depends(require_admin)],
)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Fetch a specific user by their ID. Admin only."""
    user = user_service.get_user_by_id(db, user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update a user (Admin only)",
    dependencies=[Depends(require_admin)],
)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """Update a user's name, role, or active status. Admin only."""
    return user_service.update_user(db, user_id, payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a user (Admin only)",
    dependencies=[Depends(require_admin)],
)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Soft-delete a user (sets is_deleted=True). Admin only."""
    user_service.soft_delete_user(db, user_id)
