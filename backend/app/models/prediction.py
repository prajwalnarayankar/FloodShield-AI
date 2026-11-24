from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.database.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=True, index=True)
    prediction_time = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Feature inputs
    water_level = Column(Float, nullable=True)
    discharge = Column(Float, nullable=True)
    rainfall_1h = Column(Float, nullable=True)
    rainfall_24h = Column(Float, nullable=True)
    rainfall = Column(Float, nullable=True)  # legacy field
    humidity = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    upstream_rainfall = Column(Float, nullable=True)

    # Prediction outputs
    flood_risk = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, EXTREME
    risk_level = Column(String(20), nullable=True)   # alias for flood_risk
    confidence = Column(Float, nullable=False)
    model_version = Column(String(30), default="RandomForest_v2.0")
    data_timestamp = Column(DateTime(timezone=True), nullable=True)
    data_freshness = Column(String(20), default="RECENT")
    
    # Explainability & Safety
    override_applied = Column(Boolean, default=False)
    override_reason = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=True)

    # Optional legacy association
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_station_prediction_time", "station_id", "prediction_time"),
    )