from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.database import get_db
from app.models.rainfall import RainfallObservation
from app.services.imd_service import fetch_imd_warnings
from app.services.freshness_service import format_observation_timestamp

router = APIRouter(
    prefix="/rainfall",
    tags=["Rainfall"]
)


@router.get("")
@router.get("/")
def get_rainfall_summary(district: str | None = "Yadgir", taluk: str | None = None, db: Session = Depends(get_db)):
    """
    Get latest rainfall observations for Yadgir District taluks.
    """
    # Group by location to get the latest reading per Yadgir location
    locations = db.query(
        RainfallObservation.location_id,
        func.max(RainfallObservation.observation_time).label("max_time")
    ).filter(
        RainfallObservation.district == "Yadgir"
    ).group_by(
        RainfallObservation.location_id
    ).all()

    results = []
    for loc in locations:
        latest = db.query(RainfallObservation).filter(
            RainfallObservation.location_id == loc.location_id,
            RainfallObservation.observation_time == loc.max_time
        ).first()

        if latest:
            # Determine taluk name
            taluk_name = "Yadgir"
            for t in ["Yadgir", "Shahapur", "Shorapur", "Hunsagi", "Gurmitkal"]:
                if t.lower() in latest.location_name.lower():
                    taluk_name = t
                    break

            if taluk and taluk.upper() != "ALL" and taluk.lower() not in taluk_name.lower():
                continue

            results.append({
                "location_id": latest.location_id,
                "location_name": latest.location_name,
                "taluk": f"{taluk_name} Taluk",
                "state": latest.state,
                "district": latest.district,
                "basin": latest.basin or "Krishna",
                "latitude": latest.latitude,
                "longitude": latest.longitude,
                "rainfall_1h": latest.rainfall_1h if latest.rainfall_1h is not None else 0.0,
                "rainfall_6h": latest.rainfall_6h if latest.rainfall_6h is not None else 0.0,
                "rainfall_24h": latest.rainfall_24h if latest.rainfall_24h is not None else 0.0,
                "status": "Dry / Normal" if (latest.rainfall_24h or 0.0) == 0.0 else "Precipitation",
                "observation_time": format_observation_timestamp(latest.observation_time),
                "source": latest.source or "CWC/IMD Telemetry"
            })

    results.sort(key=lambda x: x["location_name"])
    return results


@router.get("/warnings")
def get_weather_warnings():
    """Fetch official IMD district weather warnings."""
    return fetch_imd_warnings()
