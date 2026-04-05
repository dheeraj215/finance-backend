from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_admin,
    require_analyst_or_admin,
    require_any_role,
)
from app.models.user import User
from app.models.record import RecordType, RecordCategory
from app.schemas.record import RecordCreate, RecordUpdate, RecordResponse, RecordListResponse
from app.services import record_service

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.get("/", response_model=RecordListResponse, summary="List financial records")
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: Optional[RecordType] = Query(None, description="Filter by type: income or expense"),
    category: Optional[RecordCategory] = Query(None, description="Filter by category"),
    date_from: Optional[datetime] = Query(None, description="Filter records from this date (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Filter records up to this date (ISO 8601)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role),  # viewer, analyst, admin
):
    """
    List financial records with optional filters.
    Accessible by all roles: viewer, analyst, admin.
    """
    total, items = record_service.list_records(db, page, page_size, type, category, date_from, date_to)
    return RecordListResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{record_id}", response_model=RecordResponse, summary="Get a single record")
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_any_role),
):
    """Fetch a specific record by ID. Accessible by all roles."""
    from fastapi import HTTPException
    record = record_service.get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.post(
    "/",
    response_model=RecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a financial record (Admin only)",
)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new financial record. Admin only."""
    return record_service.create_record(db, payload, created_by=current_user.id)


@router.patch(
    "/{record_id}",
    response_model=RecordResponse,
    summary="Update a financial record (Admin only)",
)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update an existing financial record. Admin only."""
    return record_service.update_record(db, record_id, payload)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete a record (Admin only)",
)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Soft-delete a financial record. Admin only."""
    record_service.soft_delete_record(db, record_id)
