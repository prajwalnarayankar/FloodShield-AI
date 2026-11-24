from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from sqlalchemy.sql import func
from app.database.database import Base


class RainfallObservation(Base):
    __tablename__ = "rainfall_observations"

    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String(50), nullable=False, index=True)
    location_name = Column(String(100), nullable=True)
    state = Column(String(50), nullable=False, index=True)
    district = Column(String(100), index=True)
    basin = Column(String(100), index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)
    rainfall_1h = Column(Float, default=0.0)
    rainfall_6h = Column(Float, default=0.0)
    rainfall_24h = Column(Float, default=0.0)
    source = Column(String(50), default="CWC/IMD")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_loc_obs_time", "location_id", "observation_time"),
    )
