# Finance Dashboard API

A role-based backend for managing financial records and dashboard analytics, built with **FastAPI**, **SQLAlchemy**, and **SQLite**.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Running](#setup--running)
- [API Overview](#api-overview)
- [Roles & Permissions](#roles--permissions)
- [Authentication](#authentication)
- [Running Tests](#running-tests)
- [Assumptions & Design Decisions](#assumptions--design-decisions)

---

## Features

- **JWT Authentication** — secure login with Bearer tokens
- **Role-based Access Control** — `viewer`, `analyst`, `admin` with enforced permissions
- **Financial Records CRUD** — create, read, update, soft-delete with filtering
- **Dashboard Analytics** — totals, category breakdowns, monthly trends, recent activity
- **Pagination** — on all list endpoints
- **Soft Deletes** — records and users are never physically removed
- **Input Validation** — Pydantic schemas with meaningful error responses
- **Auto-generated API Docs** — Swagger UI at `/docs`, ReDoc at `/redoc`
- **Unit Tests** — 30+ tests covering auth, CRUD, access control, and analytics

---

## Project Structure

```
finance-backend/
├── app/
│   ├── main.py                  # FastAPI app, lifespan, error handlers
│   ├── api/
│   │   ├── __init__.py          # API router aggregator (prefix: /api/v1)
│   │   └── routes/
│   │       ├── auth.py          # POST /auth/login
│   │       ├── users.py         # CRUD /users
│   │       ├── records.py       # CRUD /records
│   │       └── dashboard.py     # GET /dashboard/summary
│   ├── core/
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── security.py          # JWT creation/decoding, bcrypt hashing
│   │   └── dependencies.py      # Auth guards and role enforcement
│   ├── db/
│   │   └── database.py          # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── user.py              # User ORM model
│   │   └── record.py            # FinancialRecord ORM model
│   ├── schemas/
│   │   ├── user.py              # User Pydantic schemas
│   │   ├── record.py            # Record Pydantic schemas
│   │   └── dashboard.py         # Dashboard response schemas
│   ├── services/
│   │   ├── user_service.py      # User business logic
│   │   ├── record_service.py    # Record business logic
│   │   └── dashboard_service.py # Aggregation and analytics logic
│   └── tests/
│       ├── conftest.py          # Fixtures, test DB, helpers
│       ├── test_auth.py         # Login, token, /me tests
│       ├── test_users.py        # User CRUD and access control tests
│       ├── test_records.py      # Record CRUD, filtering, pagination tests
│       └── test_dashboard.py    # Dashboard analytics tests
├── scripts/
│   └── seed.py                  # Demo data seeder
├── .env.example
├── requirements.txt
└── pytest.ini
```

---

## Setup & Running

### 1. Prerequisites

- Python 3.11+

### 2. Clone and install dependencies

```bash
git clone <repo-url>
cd finance-backend

python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure environment (optional)

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box with SQLite)
```

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

A default admin is automatically created on first run:
- Email: `admin@finance.dev`
- Password: `admin123`

### 5. (Optional) Seed demo data

```bash
python scripts/seed.py
```

This creates three demo users and 11 financial records:

| Email                  | Password    | Role     |
|------------------------|-------------|----------|
| admin@finance.dev      | admin123    | admin    |
| analyst@finance.dev    | analyst123  | analyst  |
| viewer@finance.dev     | viewer123   | viewer   |

---

## API Overview

All endpoints are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint          | Description              | Auth Required |
|--------|-------------------|--------------------------|---------------|
| POST   | `/auth/login`     | Login, returns JWT token | No            |

### Users

| Method | Endpoint         | Description                    | Required Role |
|--------|------------------|--------------------------------|---------------|
| GET    | `/users/me`      | Get current user profile       | Any           |
| GET    | `/users/`        | List all users (paginated)     | Admin         |
| POST   | `/users/`        | Create a new user              | Admin         |
| GET    | `/users/{id}`    | Get user by ID                 | Admin         |
| PATCH  | `/users/{id}`    | Update name, role, or status   | Admin         |
| DELETE | `/users/{id}`    | Soft-delete a user             | Admin         |

### Financial Records

| Method | Endpoint           | Description                        | Required Role  |
|--------|--------------------|------------------------------------|----------------|
| GET    | `/records/`        | List records (paginated, filtered) | Any            |
| GET    | `/records/{id}`    | Get a single record                | Any            |
| POST   | `/records/`        | Create a new record                | Admin          |
| PATCH  | `/records/{id}`    | Update a record                    | Admin          |
| DELETE | `/records/{id}`    | Soft-delete a record               | Admin          |

**Query filters for `GET /records/`:**

| Param       | Type     | Example                   |
|-------------|----------|---------------------------|
| `type`      | string   | `income` or `expense`     |
| `category`  | string   | `salary`, `rent`, etc.    |
| `date_from` | datetime | `2024-01-01T00:00:00Z`    |
| `date_to`   | datetime | `2024-12-31T23:59:59Z`    |
| `page`      | int      | `1`                       |
| `page_size` | int      | `20`                      |

### Dashboard

| Method | Endpoint              | Description                          | Required Role      |
|--------|-----------------------|--------------------------------------|--------------------|
| GET    | `/dashboard/summary`  | Full analytics summary               | Analyst, Admin     |

**Dashboard response includes:**
- `total_income`, `total_expenses`, `net_balance`
- `total_records`, `income_records`, `expense_records`
- `category_totals` — per-category breakdown
- `monthly_trends` — income vs. expense by month
- `recent_activity` — last 10 records

---

## Roles & Permissions

| Action                       | Viewer | Analyst | Admin |
|------------------------------|:------:|:-------:|:-----:|
| Login                        | ✅     | ✅      | ✅    |
| View own profile             | ✅     | ✅      | ✅    |
| List / view records          | ✅     | ✅      | ✅    |
| View dashboard summary       | ❌     | ✅      | ✅    |
| Create / edit / delete records | ❌   | ❌      | ✅    |
| List / create / manage users | ❌     | ❌      | ✅    |

Access control is enforced in `app/core/dependencies.py` using FastAPI dependency injection:

```python
require_admin              # admin only
require_analyst_or_admin   # analyst or admin
require_any_role           # viewer, analyst, or admin (any logged-in user)
```

---

## Authentication

The API uses **JWT Bearer tokens**.

1. Call `POST /api/v1/auth/login` with your credentials
2. Copy the `access_token` from the response
3. Include it in all subsequent requests:
   ```
   Authorization: Bearer <your_token>
   ```
4. Tokens expire after **24 hours**

In Swagger UI (`/docs`), click **Authorize** and paste your token to test interactively.

---

## Running Tests

```bash
pytest
```

The test suite uses an in-memory SQLite database (separate from `finance.db`) and resets between each test function. No extra setup is needed.

```
app/tests/test_auth.py        — 5 tests
app/tests/test_users.py       — 9 tests
app/tests/test_records.py     — 9 tests
app/tests/test_dashboard.py   — 6 tests
```

---

## Assumptions & Design Decisions

### Role model
Three roles were chosen as the minimum to demonstrate meaningful permission differentiation:
- **Viewer** is read-only for records but cannot see aggregated dashboard data (which may contain sensitive summaries).
- **Analyst** adds dashboard access — useful for a finance analyst who needs insights but shouldn't modify records.
- **Admin** has full access.

### Soft deletes
Both users and records use soft deletes (`is_deleted`, `deleted_at`). This preserves audit history and prevents orphaned foreign key references. Soft-deleted records are excluded from all queries and analytics.

### Amount validation
Amounts are always stored as positive floats. Record `type` (`income` / `expense`) carries the sign semantics, keeping the data model clean and queries simple.

### Single admin seeded on startup
The app seeds a default admin on first launch so the system is immediately usable without a separate setup step. This is documented and should be changed in any real deployment.

### No refresh tokens
For simplicity, only access tokens are issued. A production system would add refresh token rotation.

### SQLite default
SQLite is the default for zero-setup convenience. Switching to PostgreSQL only requires changing `DATABASE_URL` in `.env` — the SQLAlchemy layer abstracts the difference.
