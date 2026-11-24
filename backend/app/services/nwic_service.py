import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
import logging
from sqlalchemy.orm import Session
from app.models.station import Station
from app.models.river_observation import RiverObservation

logger = logging.getLogger(__name__)

NWIC_BASE_URL = "https://www.nwdp.nwic.gov.in/api/3/action/datastore_search"

# Verified NWIC / CWC Water Level Telemetry Hourly resources (2026-2030)
WATER_LEVEL_RESOURCES = {
    "Krishna": "d80798b9-4b11-4626-8b63-964202ba7216",
    "Cauvery": "d027c5ac-379d-4ac2-8ced-97b02b6edbc0",
    "West Flowing": "88d6f0d7-52a9-46cd-a030-a7b39076083e",
    "East Flowing": "dc45c606-eaed-4e9e-a4f0-84152ff13e10",
    "Pennar": "2ef9e34a-4a1b-4fe9-a542-9f7623289f47",
}

# Mapping normalized station names / identifiers to database station_ids
STATION_NAME_MAP = {
    "yadgir": "CWC_KR_YADGIR",
    "almatti": "CWC_KR_ALMATTI",
    "almatti dam": "CWC_KR_ALMATTI",
    "narayanpur": "CWC_KR_NARAYANPUR",
    "narayanpur dam": "CWC_KR_NARAYANPUR",
    "kudachi": "CWC_KR_KUDACHI",
    "tungabhadra dam": "CWC_KR_TUNGABHADRA",
    "hospet": "CWC_KR_TUNGABHADRA",
    "shimoga": "CWC_KR_SHIMOGA",
    "ujjani reservoir": "CWC_KR_UJJANI",
    "ujjani": "CWC_KR_UJJANI",
    "kolhapur": "CWC_KR_KOLHAPUR",
    "rajapur weir": "CWC_KR_KOLHAPUR",
    "wadenepally": "CWC_KR_WADENEPALLY",
    "t.k.halli": "CWC_CV_TK_HALLI",
    "tk halli": "CWC_CV_TK_HALLI",
    "t.k. halli": "CWC_CV_TK_HALLI",
    "akkihebbal": "CWC_CV_AKKIHEBBAL",
    "k.m. vadi": "CWC_CV_KM_VADI",
    "km vadi": "CWC_CV_KM_VADI",
    "kabini dam": "CWC_CV_KABINI",
    "kabini": "CWC_CV_KABINI",
    "harangi dam": "CWC_CV_HARANGI",
    "harangi": "CWC_CV_HARANGI",
    "krishna raja sagara": "CWC_CV_KRS",
    "krs": "CWC_CV_KRS",
    "wayanad": "CWC_CV_WAYANAD",
    "mananthavady": "CWC_CV_WAYANAD",
    "upper anicut": "CWC_CV_UPPER_ANICUT",
    "yennehole": "CWC_WF_YENNEHOLE",
    "karkal": "CWC_WF_YENNEHOLE",
    "bantwal": "CWC_WF_BANTWAL",
    "gerusoppa": "CWC_WF_GERUSOPPA",
    "kadra": "CWC_WF_KADRA",
    "malakkara": "CWC_WF_MALAKKARA",
    "chintamani": "CWC_PN_CHINTAMANI",
}


def create_session() -> requests.Session:
    """Create requests session with retry strategy."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def parse_nwic_datetime(dt_str: str) -> datetime | None:
    """Safely parse NWIC DD-MM-YYYY HH:MM or ISO strings."""
    if not dt_str:
        return None
    for fmt in ("%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(dt_str.strip(), fmt)
        except ValueError:
            continue
    return None


def fetch_nwic_water_levels(limit_per_resource: int = 200) -> list[dict]:
    """
    Fetch latest river water levels across all configured NWIC basins.
    Sorts by _id desc to circumvent the text-string sort bug on acquisition times.
    """
    session = create_session()
    all_observations = []

    for basin_name, resource_id in WATER_LEVEL_RESOURCES.items():
        try:
            params = {
                "resource_id": resource_id,
                "sort": "_id desc",
                "limit": limit_per_resource,
            }
            response = session.get(NWIC_BASE_URL, params=params, timeout=20)
            if response.status_code != 200:
                logger.warning(f"NWIC resource {basin_name} returned status {response.status_code}")
                continue

            data = response.json()
            if not data.get("success"):
                logger.warning(f"NWIC API returned non-success for {basin_name}")
                continue

            records = data.get("result", {}).get("records", [])
            for rec in records:
                station_raw = rec.get("Station")
                if not station_raw:
                    continue

                clean_name = station_raw.strip().lower()
                station_id = STATION_NAME_MAP.get(clean_name)
                if not station_id:
                    # Partial matching
                    for alias, s_id in STATION_NAME_MAP.items():
                        if alias in clean_name or clean_name in alias:
                            station_id = s_id
                            break

                if not station_id:
                    continue

                wl_val = rec.get("River Water Level Telemetry Hourly (meter)")
                if wl_val in (None, "", "NaN", "nan", "-"):
                    continue

                try:
                    wl = float(wl_val)
                    if wl <= 0 or wl > 4000:
                        continue
                except (ValueError, TypeError):
                    continue

                obs_time = parse_nwic_datetime(rec.get("Data Acquisition Time"))
                if not obs_time:
                    continue

                all_observations.append({
                    "station_id": station_id,
                    "station_name": station_raw,
                    "river": rec.get("River"),
                    "basin": rec.get("Basin") or basin_name,
                    "state": rec.get("State"),
                    "water_level": wl,
                    "observation_time": obs_time,
                    "source": "CWC/NWIC",
                    "data_quality": "VALID"
                })

        except requests.RequestException as e:
            logger.error(f"Error fetching NWIC {basin_name}: {e}")
            continue

    logger.info(f"[NWIC Service] Collected {len(all_observations)} water level observations.")
    return all_observations


def sync_water_levels_to_db(db: Session) -> dict:
    """Fetch recent observations from NWIC and persist newest into PostgreSQL."""
    observations = fetch_nwic_water_levels()
    new_records_count = 0
    updated_stations = set()

    for obs in observations:
        # Check if record already exists for this station and observation time
        existing = db.query(RiverObservation).filter(
            RiverObservation.station_id == obs["station_id"],
            RiverObservation.observation_time == obs["observation_time"]
        ).first()

        if not existing:
            rec = RiverObservation(
                station_id=obs["station_id"],
                observation_time=obs["observation_time"],
                water_level=obs["water_level"],
                discharge=None,  # Discharge will be populated from discharge resources
                source=obs["source"],
                data_quality=obs["data_quality"]
            )
            db.add(rec)
            new_records_count += 1
            updated_stations.add(obs["station_id"])

    if new_records_count > 0:
        db.commit()

    return {
        "status": "SUCCESS" if observations else "NO_DATA",
        "fetched": len(observations),
        "inserted": new_records_count,
        "stations_updated": len(updated_stations)
    }
