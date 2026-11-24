from pydantic import BaseModel
from datetime import datetime


class PredictionCreate(BaseModel):
    rainfall: float
    water_level: float
    humidity: float
    temperature: float


class PredictionResponse(PredictionCreate):
    id: int
    flood_risk: str
    confidence: float
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True