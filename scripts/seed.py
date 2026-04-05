"""
Seed the database with demo users and financial records.
Run: python scripts/seed.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timezone, timedelta
from app.db.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.models.record import FinancialRecord, RecordType, RecordCategory
from app.core.security import hash_password

USERS = [
    {"name": "Alice Admin",   "email": "admin@finance.dev",   "password": "admin123",   "role": UserRole.admin},
    {"name": "Ana Analyst",   "email": "analyst@finance.dev", "password": "analyst123", "role": UserRole.analyst},
    {"name": "Victor Viewer", "email": "viewer@finance.dev",  "password": "viewer123",  "role": UserRole.viewer},
]

RECORDS = [
    # Incomes
    {"amount": 8500, "type": RecordType.income,  "category": RecordCategory.salary,      "days_ago": 30, "notes": "June salary"},
    {"amount": 1200, "type": RecordType.income,  "category": RecordCategory.freelance,   "days_ago": 25, "notes": "Web project"},
    {"amount": 500,  "type": RecordType.income,  "category": RecordCategory.investment,  "days_ago": 20, "notes": "Dividends"},
    {"amount": 8500, "type": RecordType.income,  "category": RecordCategory.salary,      "days_ago": 0,  "notes": "July salary"},
    # Expenses
    {"amount": 1800, "type": RecordType.expense, "category": RecordCategory.rent,        "days_ago": 28, "notes": "June rent"},
    {"amount": 320,  "type": RecordType.expense, "category": RecordCategory.food,        "days_ago": 22, "notes": "Groceries"},
    {"amount": 85,   "type": RecordType.expense, "category": RecordCategory.transport,   "days_ago": 18, "notes": "Metro pass"},
    {"amount": 150,  "type": RecordType.expense, "category": RecordCategory.utilities,   "days_ago": 15, "notes": "Electricity + Internet"},
    {"amount": 60,   "type": RecordType.expense, "category": RecordCategory.entertainment,"days_ago": 10,"notes": "Cinema & dinner"},
    {"amount": 200,  "type": RecordType.expense, "category": RecordCategory.healthcare,  "days_ago": 5,  "notes": "Doctor visit"},
    {"amount": 1800, "type": RecordType.expense, "category": RecordCategory.rent,        "days_ago": 0,  "notes": "July rent"},
]


def seed():
    init_db()
    db = SessionLocal()

    try:
        # Seed users
        admin_id = None
        for u in USERS:
            existing = db.query(User).filter(User.email == u["email"]).first()
            if not existing:
                user = User(
                    name=u["name"],
                    email=u["email"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                    is_active=True,
                )
                db.add(user)
                db.flush()
                print(f"  ✅ Created user: {u['email']} ({u['role'].value})")
                if u["role"] == UserRole.admin:
                    admin_id = user.id
            else:
                print(f"  ⏭  User already exists: {u['email']}")
                if existing.role == UserRole.admin:
                    admin_id = existing.id

        db.commit()

        # Seed records
        now = datetime.now(timezone.utc)
        count = db.query(FinancialRecord).count()
        if count == 0:
            for r in RECORDS:
                record = FinancialRecord(
                    amount=r["amount"],
                    type=r["type"],
                    category=r["category"],
                    date=now - timedelta(days=r["days_ago"]),
                    notes=r["notes"],
                    created_by=admin_id,
                )
                db.add(record)
            db.commit()
            print(f"  ✅ Seeded {len(RECORDS)} financial records")
        else:
            print(f"  ⏭  Records already exist ({count} found), skipping")

        print("\n✅ Seed complete!")
        print("\nLogin credentials:")
        print("  admin@finance.dev    / admin123")
        print("  analyst@finance.dev  / analyst123")
        print("  viewer@finance.dev   / viewer123")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
