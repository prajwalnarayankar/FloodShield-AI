from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.services.freshness_service import calculate_data_age
from app.services.upstream_service import get_upstream_basin_status


def get_dashboard_summary(db: Session) -> dict:
    """
    Calculate real Karnataka-wide KPI statistics from PostgreSQL database.
    """
    stations = db.query(Station).all()
    total_stations = len(stations)

    recent_stations = 0
    stale_stations = 0
    unavailable_stations = 0

    station_risks = {
        "LOW": 0,
        "MEDIUM": 0,
        "HIGH": 0,
        "EXTREME": 0
    }

    active_alerts = db.query(Alert).filter(Alert.status == "ACTIVE").count()

    # Determine freshness and risk for each station
    now = datetime.now(timezone.utc)
    for st in stations:
        latest_obs = db.query(RiverObservation).filter(
            RiverObservation.station_id == st.station_id,
            RiverObservation.water_level.isnot(None)
        ).order_by(RiverObservation.observation_time.desc()).first()

        if latest_obs:
            _, _, status = calculate_data_age(latest_obs.observation_time, now)
            if status == "RECENT":
                recent_stations += 1
            else:
                stale_stations += 1
        else:
            unavailable_stations += 1

        # Latest prediction for station
        latest_pred = db.query(Prediction).filter(
            Prediction.station_id == st.station_id
        ).order_by(Prediction.prediction_time.desc()).first()

        if latest_pred and latest_pred.flood_risk in station_risks:
            station_risks[latest_pred.flood_risk] += 1
        else:
            station_risks["LOW"] += 1

    return {
        "total_stations": total_stations,
        "recent_stations": recent_stations,
        "stale_stations": stale_stations,
        "unavailable_stations": unavailable_stations,
        "low_risk": station_risks["LOW"],
        "medium_risk": station_risks["MEDIUM"],
        "high_risk": station_risks["HIGH"],
        "extreme_risk": station_risks["EXTREME"],
        "active_alerts": active_alerts,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


def get_system_data_health(db: Session) -> list[dict]:
    """
    Provide health, latest observation timestamp, record counts, and freshness status
    for all upstream and hydrological data sources.
    """
    now = datetime.now(timezone.utc)
    health = []

    # 1. CWC / NWIC River Water Level Telemetry
    nwic_count = db.query(RiverObservation).filter(RiverObservation.water_level.isnot(None)).count()
    nwic_latest = db.query(RiverObservation).filter(RiverObservation.water_level.isnot(None)).order_by(RiverObservation.observation_time.desc()).first()

    if nwic_latest:
        age_hrs, age_str, status = calculate_data_age(nwic_latest.observation_time, now)
        health.append({
            "source": "CWC / NWIC Water Level Telemetry",
            "type": "Hydrological Water Level",
            "records_stored": nwic_count,
            "latest_observation": nwic_latest.observation_time.strftime("%d %b %Y %H:%M"),
            "data_age": age_str,
            "status": status,
            "error": None
        })
    else:
        health.append({
            "source": "CWC / NWIC Water Level Telemetry",
            "type": "Hydrological Water Level",
            "records_stored": 0,
            "latest_observation": None,
            "data_age": "No data",
            "status": "UNAVAILABLE",
            "error": "No records in database yet"
        })

    # 2. CWC Discharge
    discharge_count = db.query(RiverObservation).filter(RiverObservation.discharge.isnot(None)).count()
    discharge_latest = db.query(RiverObservation).filter(RiverObservation.discharge.isnot(None)).order_by(RiverObservation.observation_time.desc()).first()

    if discharge_latest:
        age_hrs, age_str, status = calculate_data_age(discharge_latest.observation_time, now)
        health.append({
            "source": "CWC River Discharge Telemetry / Manual Daily",
            "type": "Hydrological Flow Rate (m³/s)",
            "records_stored": discharge_count,
            "latest_observation": discharge_latest.observation_time.strftime("%d %b %Y %H:%M"),
            "data_age": age_str,
            "status": status,
            "error": None
        })
    else:
        health.append({
            "source": "CWC River Discharge Telemetry / Manual Daily",
            "type": "Hydrological Flow Rate (m³/s)",
            "records_stored": 0,
            "latest_observation": None,
            "data_age": "No data",
            "status": "UNAVAILABLE",
            "error": "No discharge records in database"
        })

    # 3. IMD / CWC Rainfall Telemetry
    from app.models.rainfall import RainfallObservation
    rain_count = db.query(RainfallObservation).count()
    rain_latest = db.query(RainfallObservation).order_by(RainfallObservation.observation_time.desc()).first()

    if rain_latest:
        age_hrs, age_str, status = calculate_data_age(rain_latest.observation_time, now)
        health.append({
            "source": "CWC / IMD Rainfall Telemetry",
            "type": "Meteorological Precipitation (mm)",
            "records_stored": rain_count,
            "latest_observation": rain_latest.observation_time.strftime("%d %b %Y %H:%M"),
            "data_age": age_str,
            "status": status,
            "error": None
        })
    else:
        health.append({
            "source": "CWC / IMD Rainfall Telemetry",
            "type": "Meteorological Precipitation (mm)",
            "records_stored": 0,
            "latest_observation": None,
            "data_age": "No data",
            "status": "UNAVAILABLE",
            "error": "No rainfall records"
        })

    return health
