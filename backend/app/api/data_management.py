from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.services.dashboard_service import get_system_data_health
from app.services.data_collector import run_full_data_sync

router = APIRouter(
    tags=["Data Health & Refresh"]
)


@router.get("/data-health")
def data_health(db: Session = Depends(get_db)):
    """
    Data health check: Returns freshness, record count, and timestamp
    for each official hydrological and meteorological data source.
    """
    return get_system_data_health(db)


@router.post("/data/refresh")
def trigger_data_refresh(db: Session = Depends(get_db)):
    """
    Trigger real-time data sync from official CWC, NWIC, and IMD sources.
    Updates water levels, discharge, rainfall, predictions, and alerts.
    """
    return run_full_data_sync(db)
