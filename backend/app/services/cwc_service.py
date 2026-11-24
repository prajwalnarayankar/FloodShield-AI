import requests
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models.river_observation import RiverObservation
from app.services.nwic_service import create_session, parse_nwic_datetime, STATION_NAME_MAP

logger = logging.getLogger(__name__)

NWIC_BASE_URL = "https://www.nwdp.nwic.gov.in/api/3/action/datastore_search"

DISCHARGE_RESOURCES = {
    "Karnataka": "8116803c-3edf-4c53-9840-19446ce857e7",
    "Maharashtra": "65e0ff3a-2b79-4e0b-b1ad-c2977cda9d09",
    "Kerala": "4c771ce1-6646-4dbc-9984-e40a3d5bd21f",
    "Telangana": "083774d3-ba42-44c5-977a-2965cb572354",
    "Andhra Pradesh": "7a94f96b-7df5-4285-839d-c2dc8ba08241",
}


def fetch_cwc_discharge(limit_per_state: int = 200) -> list[dict]:
    """Fetch CWC river discharge data (in m3/sec) from NWIC daily/telemetry discharge resources."""
    session = create_session()
    all_discharge_records = []

    for state, resource_id in DISCHARGE_RESOURCES.items():
        try:
            params = {
                "resource_id": resource_id,
                "sort": "_id desc",
                "limit": limit_per_state,
            }
            response = session.get(NWIC_BASE_URL, params=params, timeout=20)
            if response.status_code != 200:
                logger.warning(f"CWC discharge for {state} returned status {response.status_code}")
                continue

            data = response.json()
            if not data.get("success"):
                continue

            records = data.get("result", {}).get("records", [])
            for rec in records:
                station_raw = rec.get("Station")
                if not station_raw:
                    continue

                clean_name = station_raw.strip().lower()
                station_id = STATION_NAME_MAP.get(clean_name)
                if not station_id:
                    for alias, s_id in STATION_NAME_MAP.items():
                        if alias in clean_name or clean_name in alias:
                            station_id = s_id
                            break

                if not station_id:
                    continue

                # CWC discharge column
                discharge_val = (
                    rec.get("Manual Daily River Water Discharge (m3/sec)") or
                    rec.get("River Discharge Telemetry Hourly (m3/sec)")
                )
                if discharge_val in (None, "", "NaN", "nan", "-"):
                    continue

                try:
                    q = float(discharge_val)
                    if q < 0:
                        continue
                except (ValueError, TypeError):
                    continue

                obs_time = parse_nwic_datetime(rec.get("Data Acquisition Time"))
                if not obs_time:
                    continue

                all_discharge_records.append({
                    "station_id": station_id,
                    "station_name": station_raw,
                    "state": state,
                    "discharge": q,
                    "observation_time": obs_time,
                    "source": "CWC/NWIC",
                })

        except requests.RequestException as e:
            logger.error(f"Error fetching discharge for {state}: {e}")
            continue

    logger.info(f"[CWC Service] Collected {len(all_discharge_records)} discharge observations.")
    return all_discharge_records


def sync_discharge_to_db(db: Session) -> dict:
    """Sync discharge observations into PostgreSQL river_observations table."""
    records = fetch_cwc_discharge()
    updated_count = 0
    new_count = 0

    for item in records:
        # Check if an observation already exists on or near this timestamp for this station
        existing = db.query(RiverObservation).filter(
            RiverObservation.station_id == item["station_id"],
            RiverObservation.observation_time == item["observation_time"]
        ).first()

        if existing:
            existing.discharge = item["discharge"]
            updated_count += 1
        else:
            new_obs = RiverObservation(
                station_id=item["station_id"],
                observation_time=item["observation_time"],
                water_level=None,
                discharge=item["discharge"],
                source=item["source"],
                data_quality="VALID"
            )
            db.add(new_obs)
            new_count += 1

    if updated_count > 0 or new_count > 0:
        db.commit()

    return {
        "status": "SUCCESS" if records else "NO_DATA",
        "fetched": len(records),
        "updated": updated_count,
        "inserted": new_count
    }
