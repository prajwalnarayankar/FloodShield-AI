from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from app.database.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(50), ForeignKey("stations.station_id"), nullable=False, index=True)
    risk_level = Column(String(20), nullable=False)  # HIGH, EXTREME
    message = Column(Text, nullable=False)
    channel = Column(String(30), default="ALL")      # SMS, EMAIL, WEB, ALL
    status = Column(String(30), default="ACTIVE")    # ACTIVE, RESOLVED, COOLED_DOWN
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
