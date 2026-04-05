import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.core.security import hash_password
from app.models.user import User, UserRole

# ── In-memory SQLite for tests ───────────────────────────────────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"

test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


# ── Helper: seed users ────────────────────────────────────────────────────────
def _make_user(db, email, role, password="password123"):
    user = User(
        name=f"Test {role.value.capitalize()}",
        email=email,
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def db_session():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_user(db_session):
    return _make_user(db_session, "admin@test.com", UserRole.admin)


@pytest.fixture
def analyst_user(db_session):
    return _make_user(db_session, "analyst@test.com", UserRole.analyst)


@pytest.fixture
def viewer_user(db_session):
    return _make_user(db_session, "viewer@test.com", UserRole.viewer)


def get_token(client, email, password="password123"):
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(client, admin_user):
    return get_token(client, admin_user.email)


@pytest.fixture
def analyst_token(client, analyst_user):
    return get_token(client, analyst_user.email)


@pytest.fixture
def viewer_token(client, viewer_user):
    return get_token(client, viewer_user.email)
