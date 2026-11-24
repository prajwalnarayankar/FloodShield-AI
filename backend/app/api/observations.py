from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database.database import get_db
from app.models.river_observation import RiverObservation
from app.models.station import Station
from app.services.freshness_service import calculate_data_age, format_observation_timestamp

router = APIRouter(
    prefix="/observations",
    tags=["Observations"]
)


@router.get("/latest")
def get_latest_observations(db: Session = Depends(get_db)):
    """Get the most recent observation for each active station."""
    stations = db.query(Station).all()
    results = []
    now = datetime.now(timezone.utc)

    for st in stations:
        obs = db.query(RiverObservation).filter(
            RiverObservation.station_id == st.station_id
        ).order_by(RiverObservation.observation_time.desc()).first()

        if obs:
            age_hrs, age_str, status = calculate_data_age(obs.observation_time, now)
            results.append({
                "station_id": st.station_id,
                "station_name": st.station_name,
                "river": st.river,
                "basin": st.basin,
                "state": st.state,
                "district": st.district,
                "water_level": obs.water_level,
                "discharge": obs.discharge,
                "observation_time": format_observation_timestamp(obs.observation_time),
                "raw_timestamp": obs.observation_time.isoformat(),
                "data_age": age_str,
                "data_age_hours": age_hrs,
                "freshness": status,
                "source": obs.source,
                "data_quality": obs.data_quality
            })

    return results


@router.get("/{station_id}")
def get_station_observations(station_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Get historical observations for a specific station."""
    station = db.query(Station).filter(Station.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    observations = db.query(RiverObservation).filter(
        RiverObservation.station_id == station_id
    ).order_by(RiverObservation.observation_time.desc()).limit(limit).all()

    now = datetime.now(timezone.utc)
    return [
        {
            "id": o.id,
            "station_id": o.station_id,
            "water_level": o.water_level,
            "discharge": o.discharge,
            "observation_time": format_observation_timestamp(o.observation_time),
            "raw_timestamp": o.observation_time.isoformat(),
            "data_age": calculate_data_age(o.observation_time, now)[1],
            "source": o.source,
            "data_quality": o.data_quality
        }
        for o in observations
    ]
