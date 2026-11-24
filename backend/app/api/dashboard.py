from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.dashboard_service import get_dashboard_summary, get_system_data_health
from app.services.upstream_service import get_upstream_basin_status

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """Statewide flood risk monitoring KPIs and counts."""
    return get_dashboard_summary(db)


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    """Public dashboard stats (no login required)."""
    return get_dashboard_summary(db)


@router.get("/analytics")
def dashboard_analytics(db: Session = Depends(get_db)):
    """Basin-level summary analytics for charts."""
    summary = get_dashboard_summary(db)
    upstream = get_upstream_basin_status(db)
    return {
        "summary": summary,
        "basins": upstream
    }