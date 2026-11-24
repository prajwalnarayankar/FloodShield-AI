from fastapi import APIRouter

from app.services.weather_service import get_forecast, get_weather

router = APIRouter(
    prefix="/weather",
    tags=["Weather"],
)


@router.get("/forecast/{city}")
def forecast(city: str):
    return get_forecast(city)


@router.get("/{city}")
def weather(city: str):
    return get_weather(city)