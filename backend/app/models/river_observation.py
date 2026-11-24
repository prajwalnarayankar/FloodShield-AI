from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.database.database import Base


class RiverObservation(Base):
    __tablename__ = "river_observations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=False, index=True)
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)
    received_time = Column(DateTime(timezone=True), server_default=func.now())
    water_level = Column(Float, nullable=True)  # in meters
    discharge = Column(Float, nullable=True)    # in m3/s
    source = Column(String(50), default="CWC/NWIC")
    data_quality = Column(String(30), default="VALID")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_station_obs_time", "station_id", "observation_time"),
    )
