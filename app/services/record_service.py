from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.record import FinancialRecord, RecordType, RecordCategory
from app.schemas.record import RecordCreate, RecordUpdate


def get_record_by_id(db: Session, record_id: int) -> Optional[FinancialRecord]:
    return (
        db.query(FinancialRecord)
        .filter(FinancialRecord.id == record_id, FinancialRecord.is_deleted == False)
        .first()
    )


def list_records(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    type: Optional[RecordType] = None,
    category: Optional[RecordCategory] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    if type:
        query = query.filter(FinancialRecord.type == type)
    if category:
        query = query.filter(FinancialRecord.category == category)
    if date_from:
        query = query.filter(FinancialRecord.date >= date_from)
    if date_to:
        query = query.filter(FinancialRecord.date <= date_to)

    query = query.order_by(FinancialRecord.date.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


def create_record(db: Session, payload: RecordCreate, created_by: int) -> FinancialRecord:
    record = FinancialRecord(
        amount=payload.amount,
        type=payload.type,
        category=payload.category,
        date=payload.date,
        notes=payload.notes,
        created_by=created_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record_id: int, payload: RecordUpdate) -> FinancialRecord:
    record = get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    if payload.amount is not None:
        record.amount = payload.amount
    if payload.type is not None:
        record.type = payload.type
    if payload.category is not None:
        record.category = payload.category
    if payload.date is not None:
        record.date = payload.date
    if payload.notes is not None:
        record.notes = payload.notes

    record.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(record)
    return record


def soft_delete_record(db: Session, record_id: int) -> None:
    record = get_record_by_id(db, record_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    record.is_deleted = True
    record.deleted_at = datetime.now(timezone.utc)
    db.commit()
