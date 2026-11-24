from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.database import get_db
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.rainfall import RainfallObservation
from app.models.prediction import Prediction
from app.services.freshness_service import calculate_data_age, format_observation_timestamp

router = APIRouter(
    prefix="/stations",
    tags=["Stations"]
)


def calculate_water_level_status(water_level: float | None, warning_level: float | None, danger_level: float | None) -> str:
    """Calculate categorical status against official CWC station thresholds."""
    if water_level is None:
        return "No Observation"
    if not danger_level or danger_level <= 0:
        return "Official danger level unavailable"

    if water_level >= danger_level:
        return "above danger"
    elif warning_level and water_level >= warning_level:
        return "above warning"
    elif warning_level:
        buffer = warning_level - water_level
        if buffer <= 0.5:
            return "near warning"
        elif buffer <= 1.5:
            return "approaching warning"
        else:
            return "normal flow"
    else:
        return "normal flow"


@router.get("")
@router.get("/")
def get_all_stations(
    basin: str | None = None,
    river: str | None = None,
    district: str | None = None,
    risk: str | None = None,
    freshness: str | None = None,
    state: str | None = None,
    db: Session = Depends(get_db)
):
    """
    Get all monitoring stations across Karnataka and upstream catchments
    with latest water levels, discharge, official warning/danger thresholds,
    data freshness, and ML risk status.
    """
    query = db.query(Station)
    if basin:
        query = query.filter(Station.basin.ilike(f"%{basin}%"))
    if river:
        query = query.filter(Station.river.ilike(f"%{river}%"))
    if district:
        query = query.filter(Station.district.ilike(f"%{district}%"))
    if state:
        query = query.filter(Station.state.ilike(f"%{state}%"))

    stations = query.all()
    results = []
    now = datetime.now(timezone.utc)

    for st in stations:
        # Latest river observation with valid water level
        latest_obs = db.query(RiverObservation).filter(
            RiverObservation.station_id == st.station_id,
            RiverObservation.water_level.isnot(None)
        ).order_by(RiverObservation.observation_time.desc()).first()

        # Water level and discharge
        wl = latest_obs.water_level if latest_obs else None
        q = latest_obs.discharge if latest_obs else None
        obs_time = latest_obs.observation_time if latest_obs else None

        if q is None:
            latest_q = db.query(RiverObservation).filter(
                RiverObservation.station_id == st.station_id,
                RiverObservation.discharge.isnot(None)
            ).order_by(RiverObservation.observation_time.desc()).first()
            if latest_q:
                q = latest_q.discharge

        # Calculate data freshness
        age_hrs, age_str, status = calculate_data_age(obs_time, now)

        # Threshold status
        threshold_status = calculate_water_level_status(wl, st.warning_level, st.danger_level)

        # Latest prediction
        pred = db.query(Prediction).filter(
            Prediction.station_id == st.station_id
        ).order_by(Prediction.prediction_time.desc()).first()

        station_risk = pred.flood_risk if pred else "LOW"
        confidence = pred.confidence if pred else 0.85
        explanation = pred.explanation if pred else "Normal hydrological conditions."
        override_applied = pred.override_applied if pred else False

        # Apply filters
        if risk and station_risk.upper() != risk.upper():
            continue
        if freshness and status.upper() != freshness.upper():
            continue

        results.append({
            "id": st.id,
            "station_id": st.station_id,
            "station_name": st.station_name,
            "river": st.river,
            "basin": st.basin,
            "state": st.state,
            "district": st.district,
            "latitude": st.latitude,
            "longitude": st.longitude,
            "source": st.source,
            "warning_level": st.warning_level,
            "danger_level": st.danger_level,
            "zero_gauge_rl": st.zero_gauge_rl,
            "is_upstream": st.is_upstream,
            "water_level": wl,
            "discharge": q,
            "threshold_status": threshold_status,
            "data_age": age_str,
            "data_age_hours": age_hrs,
            "freshness": status,
            "last_updated": format_observation_timestamp(obs_time),
            "raw_timestamp": obs_time.isoformat() if obs_time else None,
            "risk": station_risk,
            "confidence": confidence,
            "explanation": explanation,
            "override_applied": override_applied
        })

    return results


@router.get("/{station_id}")
def get_station_detail(station_id: str, db: Session = Depends(get_db)):
    """
    Get in-depth station details with recent time-series observations
    (water level, discharge, rainfall) for trend charting.
    """
    station = db.query(Station).filter(Station.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    # Fetch recent 24 observation points for time-series charts
    observations = db.query(RiverObservation).filter(
        RiverObservation.station_id == station_id,
        RiverObservation.water_level.isnot(None)
    ).order_by(RiverObservation.observation_time.desc()).limit(24).all()

    # Reorder chronologically for charting
    observations = list(reversed(observations))

    timeseries = []
    for obs in observations:
        timeseries.append({
            "time": obs.observation_time.strftime("%d %b %H:%M"),
            "timestamp": obs.observation_time.isoformat(),
            "water_level": obs.water_level,
            "discharge": obs.discharge
        })

    latest_obs = observations[-1] if observations else None
    now = datetime.now(timezone.utc)
    obs_time = latest_obs.observation_time if latest_obs else None
    age_hrs, age_str, status = calculate_data_age(obs_time, now)

    # Local district rainfall
    district_rain = db.query(RainfallObservation).filter(
        RainfallObservation.district == station.district
    ).order_by(RainfallObservation.observation_time.desc()).limit(12).all()

    if not district_rain:
        district_rain = db.query(RainfallObservation).filter(
            RainfallObservation.district == "Yadgir"
        ).order_by(RainfallObservation.observation_time.desc()).limit(12).all()

    rain_timeseries = [
        {
            "time": r.observation_time.strftime("%d %b %H:%M"),
            "rainfall_1h": r.rainfall_1h,
            "rainfall_24h": r.rainfall_24h
        }
        for r in reversed(district_rain)
    ]

    # Latest prediction
    pred = db.query(Prediction).filter(
        Prediction.station_id == station_id
    ).order_by(Prediction.prediction_time.desc()).first()

    return {
        "station": {
            "station_id": station.station_id,
            "station_name": station.station_name,
            "river": station.river,
            "basin": station.basin,
            "state": station.state,
            "district": station.district,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "warning_level": station.warning_level,
            "danger_level": station.danger_level,
            "zero_gauge_rl": station.zero_gauge_rl,
            "is_upstream": station.is_upstream,
            "source": station.source
        },
        "latest_observation": {
            "water_level": latest_obs.water_level if latest_obs else None,
            "discharge": latest_obs.discharge if latest_obs else None,
            "observation_time": format_observation_timestamp(obs_time),
            "data_age": age_str,
            "freshness": status,
            "threshold_status": calculate_water_level_status(
                latest_obs.water_level if latest_obs else None,
                station.warning_level,
                station.danger_level
            )
        },
        "prediction": {
            "risk": pred.flood_risk if pred else "LOW",
            "confidence": pred.confidence if pred else 0.85,
            "override_applied": pred.override_applied if pred else False,
            "override_reason": pred.override_reason if pred else None,
            "explanation": pred.explanation if pred else "Normal baseline.",
            "prediction_time": format_observation_timestamp(pred.prediction_time) if pred else None
        },
        "timeseries": timeseries,
        "rainfall_timeseries": rain_timeseries
    }
