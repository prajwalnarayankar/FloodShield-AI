from sqlalchemy.orm import Session

from app.models.prediction import Prediction
from app.ml.predict import predict_flood_risk


def predict_flood(
    db: Session,
    rainfall: float,
    water_level: float,
    humidity: float,
    temperature: float,
    user_id: int,
):

    # AI Model Prediction
    result = predict_flood_risk(
    water_level=water_level,
    rainfall=rainfall,
    humidity=humidity,
    temperature=temperature,
    )

    risk = result["risk"]
    confidence = float(result["confidence"])

    prediction = Prediction(
        rainfall=rainfall,
        water_level=water_level,
        humidity=humidity,
        temperature=temperature,
        flood_risk=risk,
        confidence=confidence,
        user_id=user_id,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction

def get_prediction_history(db: Session, user_id: int):
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )