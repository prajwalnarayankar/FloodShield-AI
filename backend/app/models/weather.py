from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from app.database.database import Base


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    location = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    observation_time = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    precipitation = Column(Float, default=0.0)
    wind_speed = Column(Float, nullable=True)
    weather_condition = Column(String(100), nullable=True)
    source = Column(String(50), default="IMD/OpenWeather")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
