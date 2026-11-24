from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from app.database.database import get_db
from app.models.alert import Alert
from app.models.station import Station
from app.services.freshness_service import format_observation_timestamp
from app.services.alert_service import dispatch_alert, format_sms_bulletin, format_email_bulletin

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


class TestAlertRequest(BaseModel):
    station_id: str = "CWC_KR_KUDACHI"
    risk_level: str = "EXTREME"
    custom_message: str | None = None
    recipient_phone: str | None = None
    recipient_email: str | None = None


@router.get("")
@router.get("/")
def get_alerts(status: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    """Get active and past flood alerts."""
    query = db.query(Alert)
    if status:
        query = query.filter(Alert.status == status.upper())

    alerts = query.order_by(Alert.sent_at.desc()).limit(limit).all()

    results = []
    for a in alerts:
        station = db.query(Station).filter(Station.station_id == a.station_id).first()
        results.append({
            "id": a.id,
            "station_id": a.station_id,
            "station_name": station.station_name if station else a.station_id,
            "river": station.river if station else "Unknown",
            "basin": station.basin if station else "Unknown",
            "district": station.district if station else "Unknown",
            "risk_level": a.risk_level,
            "message": a.message,
            "channel": a.channel,
            "status": a.status,
            "sent_at": format_observation_timestamp(a.sent_at),
            "raw_timestamp": a.sent_at.isoformat() if a.sent_at else None
        })

    return results


@router.post("/test-trigger")
def trigger_test_alert(req: TestAlertRequest | None = None, db: Session = Depends(get_db)):
    """
    Manually triggers a test flood alert to verify the notification pipeline.
    Dispatches to database, logs SMS & Email payloads, and updates UI feed.
    """
    station_id = req.station_id if req and req.station_id else "CWC_KR_KUDACHI"
    risk_level = req.risk_level if req and req.risk_level else "EXTREME"

    station = db.query(Station).filter(Station.station_id == station_id).first()
    if not station:
        station = db.query(Station).first()
        station_id = station.station_id if station else "CWC_KR_KUDACHI"

    station_name = station.station_name if station else station_id
    river = station.river if station else "Krishna"
    basin = station.basin if station else "Krishna"
    wl = (station.danger_level + 0.85) if (station and station.danger_level) else 530.0

    default_msg = req.custom_message if (req and req.custom_message) else (
        f"[VERIFIED ALERT] {risk_level} Flood Risk triggered for station {station_name} on {river} River ({basin} Basin). "
        f"Simulated river stage: {wl:.2f}m crossed official CWC danger threshold."
    )

    alert = dispatch_alert(
        db=db,
        station_id=station_id,
        risk_level=risk_level,
        message=default_msg,
        water_level=wl,
        channel="SMS/EMAIL/WEB",
        target_phone=req.recipient_phone if req else None,
        target_email=req.recipient_email if req else None
    )

    return {
        "status": "SUCCESS",
        "message": "Test alert dispatched successfully",
        "alert": {
            "id": alert.id,
            "station_id": alert.station_id,
            "station_name": station_name,
            "risk_level": alert.risk_level,
            "message": alert.message,
            "channel": alert.channel,
            "status": alert.status,
            "sent_at": alert.sent_at.isoformat()
        },
        "dispatched_channels": {
            "web_dashboard": "Saved to PostgreSQL alerts table (visible in UI immediately)",
            "sms_payload": format_sms_bulletin(station_name, river, basin, risk_level, wl, station.danger_level if station else None),
            "email_payload": format_email_bulletin(station, risk_level, wl, default_msg) if station else {},
            "sms_delivery": getattr(alert, "sms_delivery", {"status": "NOT_ATTEMPTED"}),
            "whatsapp_delivery": getattr(alert, "whatsapp_delivery", {"status": "NOT_ATTEMPTED"}),
            "email_delivery": getattr(alert, "email_delivery", {"status": "NOT_ATTEMPTED"})
        }
    }


@router.post("/resolve/{alert_id}")
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = "RESOLVED"
    db.commit()
    return {"message": f"Alert {alert_id} marked as RESOLVED"}


@router.post("/reset-demo")
def reset_demo_alerts(db: Session = Depends(get_db)):
    """
    Resets the alerts table to a clean, realistic Yadgir District demo set.
    Includes active alerts for Narayanpur Dam and River Bhima (Yadgir),
    plus advisory records for Shahapur and Gurmitkal.
    """
    db.query(Alert).delete()
    now = datetime.now(timezone.utc)

    demo_alerts = [
        Alert(
            station_id="CWC_KR_NARAYANPUR",
            risk_level="HIGH",
            message="HIGH INFLOW ALERT: Narayanpur Dam reservoir level reached 490.80m, approaching CWC Warning Threshold (490.50m). Controlled spillway discharge initiated into Krishna riverbed. Low-lying riverbank evacuation advisories active for Shorapur and Hunsagi taluks.",
            channel="SMS/EMAIL/WEB",
            status="ACTIVE",
            sent_at=now - timedelta(minutes=18)
        ),
        Alert(
            station_id="CWC_KR_YADGIR",
            risk_level="MEDIUM",
            message="MONSOON DISCHARGE WATCH: River Bhima stage at Yadgir bridge rising at 0.12 m/hr due to 38,000 cusecs upstream release from Ujjani Reservoir. Current stage 357.60m is approaching Warning Level (359.00m).",
            channel="SMS/EMAIL/WEB",
            status="ACTIVE",
            sent_at=now - timedelta(minutes=45)
        ),
        Alert(
            station_id="CWC_YD_SHAHAPUR",
            risk_level="ADVISORY",
            message="TRIBUTARY ADVISORY: Doranahalli stream inflow stabilizing at 373.20m below Warning Level (375.00m). Riparian agricultural embankments inspected and intact.",
            channel="SMS/EMAIL/WEB",
            status="RESOLVED",
            sent_at=now - timedelta(hours=4)
        ),
        Alert(
            station_id="CWC_YD_GURMITKAL",
            risk_level="ADVISORY",
            message="ROUTINE MONSOON NOTICE: Hattikuni Reservoir gauge steady at 425.60m with managed canal releases. No downstream inundation risk.",
            channel="SMS/EMAIL/WEB",
            status="RESOLVED",
            sent_at=now - timedelta(hours=11)
        )
    ]

    db.add_all(demo_alerts)
    db.commit()

    return {
        "status": "SUCCESS",
        "message": "Demo alerts reset successfully with clean Yadgir District dataset",
        "count": len(demo_alerts)
    }


@router.post("/clear")
def clear_alerts(db: Session = Depends(get_db)):
    """Clears all alerts from the database."""
    deleted = db.query(Alert).delete()
    db.commit()
    return {"status": "SUCCESS", "deleted_count": deleted}

