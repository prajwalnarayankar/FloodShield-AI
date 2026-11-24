from pydantic import BaseModel


class CityPrediction(BaseModel):
    city: str