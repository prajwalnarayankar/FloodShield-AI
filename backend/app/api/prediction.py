from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone
from app.database.database import get_db
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.rainfall import RainfallObservation
from app.models.prediction import Prediction
from app.ml.predict import predict_flood_risk
from app.services.freshness_service import calculate_data_age, format_observation_timestamp

router = APIRouter(
    prefix="/predictions",
    tags=["Flood Prediction"]
)


class CustomEvaluationRequest(BaseModel):
    station_id: str | None = None
    water_level: float
    discharge: float = 50.0
    water_level_change_6h: float = 0.0
    rainfall_24h: float = 0.0
    upstream_rainfall: float = 0.0
    warning_level: float | None = None
    danger_level: float | None = None


@router.get("")
@router.get("/")
def get_all_predictions(db: Session = Depends(get_db)):
    """Get the latest predictions across all monitoring stations."""
    stations = db.query(Station).all()
    results = []

    for st in stations:
        pred = db.query(Prediction).filter(
            Prediction.station_id == st.station_id
        ).order_by(Prediction.prediction_time.desc()).first()

        latest_obs = db.query(RiverObservation).filter(
            RiverObservation.station_id == st.station_id
        ).order_by(RiverObservation.observation_time.desc()).first()

        results.append({
            "station_id": st.station_id,
            "station_name": st.station_name,
            "river": st.river,
            "basin": st.basin,
            "district": st.district,
            "state": st.state,
            "latitude": st.latitude,
            "longitude": st.longitude,
            "warning_level": st.warning_level,
            "danger_level": st.danger_level,
            "water_level": latest_obs.water_level if latest_obs else None,
            "discharge": latest_obs.discharge if latest_obs else None,
            "risk": pred.flood_risk if pred else "LOW",
            "confidence": pred.confidence if pred else 0.85,
            "override_applied": pred.override_applied if pred else False,
            "override_reason": pred.override_reason if pred else None,
            "explanation": pred.explanation if pred else "Normal seasonal conditions.",
            "data_freshness": pred.data_freshness if pred else "UNAVAILABLE",
            "prediction_time": format_observation_timestamp(pred.prediction_time) if pred else None
        })

    return results


@router.get("/{station_id}")
def get_station_prediction(station_id: str, db: Session = Depends(get_db)):
    """Get prediction and explainability reasoning for a specific station."""
    station = db.query(Station).filter(Station.station_id == station_id).first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    pred = db.query(Prediction).filter(
        Prediction.station_id == station_id
    ).order_by(Prediction.prediction_time.desc()).first()

    latest_obs = db.query(RiverObservation).filter(
        RiverObservation.station_id == station_id
    ).order_by(RiverObservation.observation_time.desc()).first()

    now = datetime.now(timezone.utc)
    age_hrs, age_str, freshness = calculate_data_age(latest_obs.observation_time if latest_obs else None, now)

    if pred:
        return {
            "station_id": station.station_id,
            "station_name": station.station_name,
            "river": station.river,
            "basin": station.basin,
            "district": station.district,
            "state": station.state,
            "warning_level": station.warning_level,
            "danger_level": station.danger_level,
            "water_level": latest_obs.water_level if latest_obs else None,
            "discharge": latest_obs.discharge if latest_obs else None,
            "data_freshness": freshness,
            "data_age": age_str,
            "prediction": {
                "risk": pred.flood_risk,
                "confidence": pred.confidence,
                "override_applied": pred.override_applied,
                "override_reason": pred.override_reason,
                "explanation": pred.explanation,
                "prediction_time": format_observation_timestamp(pred.prediction_time),
                "model_version": pred.model_version
            }
        }
    else:
        # Evaluate on the fly if no prediction record exists
        wl = latest_obs.water_level if latest_obs else 10.0
        q = latest_obs.discharge if latest_obs else 50.0
        result = predict_flood_risk(
            water_level=wl,
            discharge=q,
            warning_level=station.warning_level,
            danger_level=station.danger_level
        )
        return {
            "station_id": station.station_id,
            "station_name": station.station_name,
            "river": station.river,
            "basin": station.basin,
            "district": station.district,
            "state": station.state,
            "warning_level": station.warning_level,
            "danger_level": station.danger_level,
            "water_level": wl,
            "discharge": q,
            "data_freshness": freshness,
            "data_age": age_str,
            "prediction": {
                "risk": result["risk"],
                "confidence": result["confidence"],
                "override_applied": result["override_applied"],
                "override_reason": result["override_reason"],
                "explanation": "; ".join(result["reasons"]),
                "prediction_time": format_observation_timestamp(now),
                "model_version": "RandomForest_v2.0"
            }
        }


@router.post("/evaluate")
def evaluate_custom_scenario(request: CustomEvaluationRequest, db: Session = Depends(get_db)):
    """
    On-demand risk assessment using the Random Forest model and hybrid safety layer.
    Ideal for testing scenarios (e.g. what happens if upstream rainfall increases to 150mm).
    """
    warning_level = request.warning_level
    danger_level = request.danger_level

    if request.station_id and (not warning_level or not danger_level):
        st = db.query(Station).filter(Station.station_id == request.station_id).first()
        if st:
            warning_level = warning_level or st.warning_level
            danger_level = danger_level or st.danger_level

    result = predict_flood_risk(
        water_level=request.water_level,
        discharge=request.discharge,
        water_level_change_6h=request.water_level_change_6h,
        rainfall_24h=request.rainfall_24h,
        upstream_rainfall=request.upstream_rainfall,
        warning_level=warning_level,
        danger_level=danger_level
    )

    return result