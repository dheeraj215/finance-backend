from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.database import init_db
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB tables and seed admin on startup."""
    init_db()
    _seed_admin()
    yield


def _seed_admin():
    """Create a default admin user if none exists."""
    from app.db.database import SessionLocal
    from app.models.user import User, UserRole
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.email == "admin@finance.dev").first()
        if not exists:
            admin = User(
                name="Default Admin",
                email="admin@finance.dev",
                hashed_password=hash_password("admin123"),
                role=UserRole.admin,
                is_active=True,
            )
            db.add(admin)
            db.commit()
            print("✅ Seeded default admin: admin@finance.dev / admin123")
    finally:
        db.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## Finance Dashboard API

A role-based backend for managing financial records and dashboard analytics.

### Roles & Permissions

| Role     | View Records | Dashboard | Create/Edit/Delete Records | Manage Users |
|----------|-------------|-----------|---------------------------|--------------|
| viewer   | ✅           | ❌        | ❌                         | ❌           |
| analyst  | ✅           | ✅        | ❌                         | ❌           |
| admin    | ✅           | ✅        | ✅                         | ✅           |

### Quick Start
1. `POST /api/v1/auth/login` with `admin@finance.dev` / `admin123`
2. Copy the `access_token` and click **Authorize** above
3. Start exploring the endpoints
    """,
    lifespan=lifespan,
)

# ── Global validation error handler ─────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors},
    )


# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }
