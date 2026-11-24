from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class Station(Base):
    __tablename__ = "stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), unique=True, index=True, nullable=False)
    station_name = Column(String(100), nullable=False)
    river = Column(String(100), nullable=False)
    basin = Column(String(100), nullable=False, index=True)
    state = Column(String(50), nullable=False, index=True)
    district = Column(String(100))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    source = Column(String(50), default="CWC/NWIC")
    warning_level = Column(Float, nullable=True)
    danger_level = Column(Float, nullable=True)
    zero_gauge_rl = Column(Float, nullable=True)
    is_upstream = Column(String(10), default="No")  # "Yes" for upstream boundary stations affecting Karnataka
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
