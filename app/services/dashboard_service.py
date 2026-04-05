from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.record import FinancialRecord, RecordType
from app.schemas.dashboard import DashboardSummary, CategoryTotal, MonthlyTrend, RecentActivity


def get_dashboard_summary(db: Session) -> DashboardSummary:
    base_query = db.query(FinancialRecord).filter(FinancialRecord.is_deleted == False)

    # ── Totals ──────────────────────────────────────────────────────────────
    income_agg = (
        base_query.filter(FinancialRecord.type == RecordType.income)
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .scalar()
    )
    expense_agg = (
        base_query.filter(FinancialRecord.type == RecordType.expense)
        .with_entities(func.coalesce(func.sum(FinancialRecord.amount), 0.0))
        .scalar()
    )
    total_income = round(float(income_agg), 2)
    total_expenses = round(float(expense_agg), 2)

    income_count = base_query.filter(FinancialRecord.type == RecordType.income).count()
    expense_count = base_query.filter(FinancialRecord.type == RecordType.expense).count()

    # ── Category totals ─────────────────────────────────────────────────────
    category_rows = (
        base_query
        .with_entities(
            FinancialRecord.category,
            func.sum(FinancialRecord.amount).label("total"),
            func.count(FinancialRecord.id).label("count"),
        )
        .group_by(FinancialRecord.category)
        .all()
    )
    category_totals = [
        CategoryTotal(category=row.category.value, total=round(float(row.total), 2), count=row.count)
        for row in category_rows
    ]

    # ── Monthly trends (last 12 months) ─────────────────────────────────────
    monthly_rows = (
        base_query
        .with_entities(
            extract("year", FinancialRecord.date).label("year"),
            extract("month", FinancialRecord.date).label("month"),
            FinancialRecord.type,
            func.sum(FinancialRecord.amount).label("total"),
        )
        .group_by("year", "month", FinancialRecord.type)
        .order_by("year", "month")
        .all()
    )

    # Aggregate into a dict keyed by (year, month)
    trends: dict[tuple, dict] = {}
    for row in monthly_rows:
        key = (int(row.year), int(row.month))
        if key not in trends:
            trends[key] = {"income": 0.0, "expense": 0.0}
        if row.type == RecordType.income:
            trends[key]["income"] = round(float(row.total), 2)
        else:
            trends[key]["expense"] = round(float(row.total), 2)

    monthly_trends = [
        MonthlyTrend(
            year=year,
            month=month,
            income=vals["income"],
            expense=vals["expense"],
            net=round(vals["income"] - vals["expense"], 2),
        )
        for (year, month), vals in sorted(trends.items())
    ]

    # ── Recent activity (last 10 records) ───────────────────────────────────
    recent_records = (
        base_query
        .order_by(FinancialRecord.date.desc())
        .limit(10)
        .all()
    )
    recent_activity = [
        RecentActivity(
            id=r.id,
            amount=r.amount,
            type=r.type.value,
            category=r.category.value,
            date=r.date.strftime("%Y-%m-%d"),
            notes=r.notes,
        )
        for r in recent_records
    ]

    return DashboardSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=round(total_income - total_expenses, 2),
        total_records=income_count + expense_count,
        income_records=income_count,
        expense_records=expense_count,
        category_totals=category_totals,
        monthly_trends=monthly_trends,
        recent_activity=recent_activity,
    )
