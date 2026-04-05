from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.dependencies import require_analyst_or_admin
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get dashboard summary (Analyst and Admin)",
)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_or_admin),
):
    """
    Returns aggregated financial data for the dashboard:
    - Total income, expenses, net balance
    - Category-wise totals
    - Monthly trends
    - Recent activity (last 10 records)

    Accessible by: analyst, admin.
    """
    return get_dashboard_summary(db)
