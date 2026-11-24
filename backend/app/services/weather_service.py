import os
from collections import defaultdict
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(city: str):
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException:
        return {"error": "Weather service is unavailable"}

    if response.status_code != 200:
        return {"error": "City not found"}

    data = response.json()
    rainfall = data.get("rain", {}).get("1h", 0)

    return {
        "city": data["name"],
        "temperature": round(data["main"]["temp"], 1),
        "humidity": data["main"]["humidity"],
        "rainfall": rainfall,
        "wind_speed": data["wind"]["speed"],
        "weather": data["weather"][0]["description"],
        "latitude": data["coord"]["lat"],
        "longitude": data["coord"]["lon"],
    }

def get_forecast(city: str):
    url = (
        "https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException:
        return {"error": "Forecast service is unavailable"}

    if response.status_code != 200:
        return {"error": "City not found"}

    data = response.json()
    offset = data["city"].get("timezone", 0)
    hourly = []
    daily_groups = defaultdict(list)

    for item in data["list"]:
        local_time = datetime.fromtimestamp(
            item["dt"] + offset,
            tz=timezone.utc,
        )

        daily_groups[local_time.date()].append((local_time, item))

        if len(hourly) < 6:
            hourly.append({
                "time": local_time.strftime("%I %p").lstrip("0").lower(),
                "temperature": round(item["main"]["temp"]),
                "rain_chance": round(item.get("pop", 0) * 100),
                "weather": item["weather"][0]["description"],
            })

    daily = []
    for entries in list(daily_groups.values())[:7]:
        times, items = zip(*entries)
        daily.append({
            "day": times[0].strftime("%a"),
            "high": round(max(item["main"]["temp_max"] for item in items)),
            "low": round(min(item["main"]["temp_min"] for item in items)),
            "weather": items[len(items) // 2]["weather"][0]["description"],
        })

    return {
        "city": data["city"]["name"],
        "hourly": hourly,
        "daily": daily,
    }