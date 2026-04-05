import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class RecordType(str, enum.Enum):
    income = "income"
    expense = "expense"


class RecordCategory(str, enum.Enum):
    salary = "salary"
    freelance = "freelance"
    investment = "investment"
    food = "food"
    transport = "transport"
    utilities = "utilities"
    healthcare = "healthcare"
    entertainment = "entertainment"
    education = "education"
    rent = "rent"
    other = "other"


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(Enum(RecordType), nullable=False)
    category = Column(Enum(RecordCategory), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    notes = Column(Text, nullable=True)

    # Who created this record
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[created_by])

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
