import requests
from math import radians, sin, cos, sqrt, atan2


NWIC_API_URL = (
    "https://www.nwdp.nwic.gov.in/api/3/action/datastore_search"
)


RESOURCES = {
    "Cauvery": "d027c5ac-379d-4ac2-8ced-97b02b6edbc0",
    "Krishna": "d80798b9-4b11-4626-8b63-964202ba7216",
    "West": "88d6f0d7-52a9-46cd-a030-a7b39076083e",
    "East": "dc45c606-eaed-4e9e-a4f0-84152ff13e10",
}


# =========================================================
# GET WATER LEVEL FOR ONE RIVER
# =========================================================

def get_water_level(river_name: str):
    """
    Fetch Karnataka river water-level data from NWIC/CWC
    for one river resource.
    """

    resource_id = RESOURCES.get(river_name)

    if not resource_id:
        print(f"Invalid river name: {river_name}")
        return []

    params = {
        "resource_id": resource_id,
        "filters": '{"State":"Karnataka"}',
        "limit": 100,
        "sort": '"Data Acquisition Time" desc',
    }

    try:
        response = requests.get(
            NWIC_API_URL,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("success"):
            print(f"NWIC API error for {river_name}")
            return []

        records = data.get("result", {}).get("records", [])

        results = []

        for record in records:

            water_level = record.get(
                "River Water Level Telemetry Hourly (meter)"
            )

            if water_level in [None, "", "NaN", "nan"]:
                continue

            try:
                water_level = float(water_level)
            except (ValueError, TypeError):
                continue

            latitude = record.get("Latitude")
            longitude = record.get("Longitude")

            if latitude in [None, ""] or longitude in [None, ""]:
                continue

            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (ValueError, TypeError):
                continue

            results.append(
                {
                    "station": record.get("Station"),
                    "river": record.get("River") or river_name,
                    "district": record.get("District"),
                    "basin": record.get("Basin"),
                    "latitude": latitude,
                    "longitude": longitude,
                    "water_level": water_level,
                    "timestamp": record.get(
                        "Data Acquisition Time"
                    ),
                }
            )

        return results

    except requests.RequestException as error:
        print(
            f"NWIC API ERROR ({river_name}):",
            error,
        )
        return []


# =========================================================
# GET ALL KARNATAKA RIVER DATA
# =========================================================

def get_all_karnataka_water_levels():
    """
    Fetch water-level data from all configured
    Karnataka NWIC river resources.
    """

    all_data = []

    for river_name in RESOURCES:
        river_data = get_water_level(river_name)

        if river_data:
            all_data.extend(river_data)

    print(
        f"NWIC: fetched {len(all_data)} Karnataka station records"
    )

    return all_data


# =========================================================
# FIND NEAREST STATION
# =========================================================

def find_nearest_station(
    river_data,
    city_latitude,
    city_longitude,
):
    """
    Find the NWIC station geographically closest
    to the searched city using the Haversine formula.
    """

    nearest_station = None
    minimum_distance = float("inf")

    try:
        city_lat = float(city_latitude)
        city_lon = float(city_longitude)
    except (TypeError, ValueError):
        return None

    R = 6371.0

    for station in river_data:

        try:
            station_lat = float(
                station["latitude"]
            )

            station_lon = float(
                station["longitude"]
            )

        except (TypeError, ValueError, KeyError):
            continue

        lat1 = radians(city_lat)
        lon1 = radians(city_lon)

        lat2 = radians(station_lat)
        lon2 = radians(station_lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            sin(dlat / 2) ** 2
            + cos(lat1)
            * cos(lat2)
            * sin(dlon / 2) ** 2
        )

        c = 2 * atan2(
            sqrt(a),
            sqrt(1 - a),
        )

        distance = R * c

        if distance < minimum_distance:

            minimum_distance = distance

            nearest_station = station.copy()

            nearest_station["distance_km"] = round(
                distance,
                2,
            )

    return nearest_station