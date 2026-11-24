from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.rainfall import RainfallObservation

# Hydrological basin upstream-downstream influence relationships
BASIN_UPSTREAM_MAPPING = {
    "Krishna & Bhima Basin (Yadgir District)": {
        "upstream_states": ["Maharashtra", "Telangana"],
        "upstream_catchments": ["Solapur / Ujjani Reservoir", "Upper Krishna Catchment", "Bhima Headwaters"],
        "affected_karnataka_districts": ["Yadgir (Focal Monitoring District)", "Shahapur Taluk", "Shorapur Taluk", "Hunsagi Taluk", "Gurmitkal Taluk"],
        "key_rivers": ["Bhima", "Krishna", "Hattikuni Stream", "Doranahalli Inflow"],
        "upstream_station_ids": ["CWC_KR_UJJANI", "CWC_KR_KUDACHI"],
        "downstream_station_ids": ["CWC_KR_YADGIR", "CWC_KR_NARAYANPUR", "CWC_YD_SHAHAPUR", "CWC_YD_SHORAPUR", "CWC_YD_GURMITKAL"],
        "travel_time_hours": "14 to 22 hours"
    },
    "Cauvery": {
        "upstream_states": ["Kerala"],
        "upstream_catchments": ["Wayanad Hills", "Kabini Catchment", "Western Ghats High Ranges"],
        "affected_karnataka_districts": ["Kodagu", "Mysuru", "Mandya", "Hassan", "Chamarajanagar", "Ramanagara"],
        "key_rivers": ["Cauvery", "Kabini", "Hemavathi", "Harangi", "Shimsha"],
        "upstream_station_ids": ["CWC_CV_WAYANAD"],
        "downstream_station_ids": ["CWC_CV_KABINI", "CWC_CV_HARANGI", "CWC_CV_KRS", "CWC_CV_TK_HALLI", "CWC_CV_AKKIHEBBAL", "CWC_CV_KM_VADI"],
        "travel_time_hours": "6 to 18 hours"
    },
    "West Flowing Rivers": {
        "upstream_states": ["Goa", "Maharashtra", "Kerala"],
        "upstream_catchments": ["Coastal Western Ghats Crests", "Castlerock / Goa Border"],
        "affected_karnataka_districts": ["Uttara Kannada", "Udupi", "Dakshina Kannada"],
        "key_rivers": ["Kali", "Sharavathi", "Netravati", "Swarna", "Aghanashini"],
        "upstream_station_ids": ["CWC_WF_MALAKKARA"],
        "downstream_station_ids": ["CWC_WF_YENNEHOLE", "CWC_WF_BANTWAL", "CWC_WF_GERUSOPPA", "CWC_WF_KADRA"],
        "travel_time_hours": "3 to 8 hours"
    },
    "Pennar": {
        "upstream_states": ["Andhra Pradesh"],
        "upstream_catchments": ["Nandi Hills & Eastern Catchments"],
        "affected_karnataka_districts": ["Chikkaballapur", "Kolar"],
        "key_rivers": ["Pennar", "Palar"],
        "upstream_station_ids": [],
        "downstream_station_ids": ["CWC_PN_CHINTAMANI"],
        "travel_time_hours": "6 to 12 hours"
    }
}


def get_upstream_basin_status(db: Session) -> list[dict]:
    """
    Calculate comprehensive upstream hydrological conditions for each Karnataka basin.
    Returns upstream rainfall, upstream water levels, trends, and risk contribution.
    """
    basin_statuses = []

    for basin_name, mapping in BASIN_UPSTREAM_MAPPING.items():
        # 1. Calculate upstream rainfall from upstream states
        upstream_rain_records = db.query(RainfallObservation).filter(
            RainfallObservation.state.in_(mapping["upstream_states"]),
        ).order_by(RainfallObservation.observation_time.desc()).limit(50).all()

        if upstream_rain_records:
            recent_rain_24h = [r.rainfall_24h for r in upstream_rain_records if r.rainfall_24h is not None]
            avg_upstream_rain = round(sum(recent_rain_24h) / len(recent_rain_24h), 2) if recent_rain_24h else 0.0
            max_upstream_rain = max(recent_rain_24h) if recent_rain_24h else 0.0
        else:
            avg_upstream_rain = 0.0
            max_upstream_rain = 0.0

        # Upstream rainfall severity
        if max_upstream_rain >= 100 or avg_upstream_rain >= 50:
            rain_intensity = "HIGH"
        elif max_upstream_rain >= 40 or avg_upstream_rain >= 20:
            rain_intensity = "MODERATE"
        elif max_upstream_rain > 5:
            rain_intensity = "LIGHT"
        else:
            rain_intensity = "NORMAL"

        # 2. Upstream river levels and trends
        upstream_stations = db.query(Station).filter(
            Station.station_id.in_(mapping["upstream_station_ids"])
        ).all()

        upstream_wl_readings = []
        upstream_wl_trend = "STABLE"

        for st in upstream_stations:
            recent_obs = db.query(RiverObservation).filter(
                RiverObservation.station_id == st.station_id,
                RiverObservation.water_level.isnot(None)
            ).order_by(RiverObservation.observation_time.desc()).limit(5).all()

            if len(recent_obs) >= 2:
                latest_wl = recent_obs[0].water_level
                prev_wl = recent_obs[1].water_level
                diff = latest_wl - prev_wl
                if diff > 0.3:
                    upstream_wl_trend = "RISING"
                elif diff < -0.3:
                    upstream_wl_trend = "FALLING"
                upstream_wl_readings.append(latest_wl)
            elif recent_obs:
                upstream_wl_readings.append(recent_obs[0].water_level)

        # 3. Downstream Karnataka river status
        downstream_stations = db.query(Station).filter(
            Station.station_id.in_(mapping["downstream_station_ids"])
        ).all()

        downstream_levels = []
        downstream_trend = "STABLE"
        near_danger_count = 0

        for st in downstream_stations:
            recent_obs = db.query(RiverObservation).filter(
                RiverObservation.station_id == st.station_id,
                RiverObservation.water_level.isnot(None)
            ).order_by(RiverObservation.observation_time.desc()).limit(2).all()

            if recent_obs:
                cur_wl = recent_obs[0].water_level
                downstream_levels.append(cur_wl)
                if st.danger_level and cur_wl >= (st.danger_level * 0.9):
                    near_danger_count += 1
                if len(recent_obs) >= 2:
                    if (cur_wl - recent_obs[1].water_level) > 0.3:
                        downstream_trend = "RISING"

        # 4. Overall basin condition
        if rain_intensity == "HIGH" and (upstream_wl_trend == "RISING" or downstream_trend == "RISING"):
            overall_condition = "CRITICAL WATCH"
            risk_contribution = "HIGH"
        elif rain_intensity in ("HIGH", "MODERATE") or upstream_wl_trend == "RISING" or near_danger_count > 0:
            overall_condition = "ELEVATED ATTENTION"
            risk_contribution = "MEDIUM"
        else:
            overall_condition = "NORMAL / STABLE"
            risk_contribution = "LOW"

        basin_statuses.append({
            "basin": basin_name,
            "upstream_states": mapping["upstream_states"],
            "upstream_catchments": mapping["upstream_catchments"],
            "affected_karnataka_districts": mapping["affected_karnataka_districts"],
            "key_rivers": mapping["key_rivers"],
            "upstream_rainfall_intensity": rain_intensity,
            "avg_upstream_rainfall_24h": avg_upstream_rain,
            "max_upstream_rainfall_24h": max_upstream_rain,
            "upstream_river_trend": upstream_wl_trend,
            "downstream_river_trend": downstream_trend,
            "near_danger_stations": near_danger_count,
            "travel_time_hours": mapping["travel_time_hours"],
            "overall_condition": overall_condition,
            "risk_contribution": risk_contribution
        })

    return basin_statuses
