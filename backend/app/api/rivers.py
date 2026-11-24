from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.prediction import Prediction

router = APIRouter(
    prefix="/rivers",
    tags=["Rivers"]
)


@router.get("")
@router.get("/")
def get_all_rivers(db: Session = Depends(get_db)):
    """Summary of all monitored river systems in Karnataka and connected basins."""
    stations = db.query(Station).all()
    rivers = {}

    for st in stations:
        river_name = st.river
        if river_name not in rivers:
            rivers[river_name] = {
                "river": river_name,
                "basin": st.basin,
                "stations_count": 0,
                "states_covered": set(),
                "highest_risk": "LOW",
                "stations": []
            }

        rivers[river_name]["stations_count"] += 1
        rivers[river_name]["states_covered"].add(st.state)

        latest_obs = db.query(RiverObservation).filter(
            RiverObservation.station_id == st.station_id
        ).order_by(RiverObservation.observation_time.desc()).first()

        pred = db.query(Prediction).filter(
            Prediction.station_id == st.station_id
        ).order_by(Prediction.prediction_time.desc()).first()

        risk = pred.flood_risk if pred else "LOW"

        # Track highest risk on this river
        risk_hierarchy = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "EXTREME": 4}
        if risk_hierarchy.get(risk, 1) > risk_hierarchy.get(rivers[river_name]["highest_risk"], 1):
            rivers[river_name]["highest_risk"] = risk

        rivers[river_name]["stations"].append({
            "station_id": st.station_id,
            "station_name": st.station_name,
            "district": st.district,
            "water_level": latest_obs.water_level if latest_obs else None,
            "discharge": latest_obs.discharge if latest_obs else None,
            "risk": risk
        })

    # Convert sets to sorted lists
    output = []
    for r in rivers.values():
        r["states_covered"] = sorted(list(r["states_covered"]))
        output.append(r)

    return sorted(output, key=lambda x: x["stations_count"], reverse=True)


@router.get("/{river_name}")
def get_river_detail(river_name: str, db: Session = Depends(get_db)):
    """Get all stations and current observations along a specific river."""
    stations = db.query(Station).filter(Station.river.ilike(f"%{river_name}%")).all()
    if not stations:
        raise HTTPException(status_code=404, detail="River not found")

    result = []
    for st in stations:
        latest_obs = db.query(RiverObservation).filter(
            RiverObservation.station_id == st.station_id
        ).order_by(RiverObservation.observation_time.desc()).first()

        pred = db.query(Prediction).filter(
            Prediction.station_id == st.station_id
        ).order_by(Prediction.prediction_time.desc()).first()

        result.append({
            "station_id": st.station_id,
            "station_name": st.station_name,
            "basin": st.basin,
            "district": st.district,
            "state": st.state,
            "latitude": st.latitude,
            "longitude": st.longitude,
            "warning_level": st.warning_level,
            "danger_level": st.danger_level,
            "water_level": latest_obs.water_level if latest_obs else None,
            "discharge": latest_obs.discharge if latest_obs else None,
            "observation_time": latest_obs.observation_time.isoformat() if latest_obs else None,
            "risk": pred.flood_risk if pred else "LOW",
            "confidence": pred.confidence if pred else 0.85
        })

    return {
        "river": river_name,
        "stations": result
    }
