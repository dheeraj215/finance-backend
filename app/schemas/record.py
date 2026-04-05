from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
from app.models.record import RecordType, RecordCategory


class RecordCreate(BaseModel):
    amount: float
    type: RecordType
    category: RecordCategory
    date: datetime
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be a positive number")
        return round(v, 2)


class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[RecordType] = None
    category: Optional[RecordCategory] = None
    date: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be a positive number")
        return round(v, 2) if v is not None else v


class RecordResponse(BaseModel):
    id: int
    amount: float
    type: RecordType
    category: RecordCategory
    date: datetime
    notes: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RecordListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RecordResponse]


class RecordFilters(BaseModel):
    type: Optional[RecordType] = None
    category: Optional[RecordCategory] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
