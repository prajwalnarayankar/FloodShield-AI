from sqlalchemy import text
from app.database.database import Base, engine, SessionLocal
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.rainfall import RainfallObservation
from app.models.weather import WeatherObservation
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.user import User
from app.services.continuous_telemetry import (
    YADGIR_DISTRICT_STATIONS,
    seed_yadgir_stations,
    ensure_continuous_yadgir_telemetry
)

OFFICIAL_STATIONS = YADGIR_DISTRICT_STATIONS


def upgrade_schema_if_needed():
    """Add new columns to existing tables if they already exist."""
    if engine.name == "sqlite":
        return

    with engine.connect() as conn:
        alter_queries = [
            "ALTER TABLE predictions ALTER COLUMN rainfall DROP NOT NULL",
            "ALTER TABLE predictions ALTER COLUMN water_level DROP NOT NULL",
            "ALTER TABLE predictions ALTER COLUMN humidity DROP NOT NULL",
            "ALTER TABLE predictions ALTER COLUMN temperature DROP NOT NULL",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS station_id VARCHAR(50)",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS prediction_time TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS discharge DOUBLE PRECISION",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS rainfall_1h DOUBLE PRECISION",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS rainfall_24h DOUBLE PRECISION",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS upstream_rainfall DOUBLE PRECISION",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20)",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS model_version VARCHAR(30) DEFAULT 'RandomForest_v2.0'",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS data_timestamp TIMESTAMP WITH TIME ZONE",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS data_freshness VARCHAR(20) DEFAULT 'RECENT'",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS override_applied BOOLEAN DEFAULT FALSE",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS override_reason VARCHAR(255)",
            "ALTER TABLE predictions ADD COLUMN IF NOT EXISTS explanation TEXT",
        ]
        for query in alter_queries:
            try:
                conn.execute(text(query))
            except Exception as e:
                print(f"Schema alter note: {e}")
        conn.commit()


def seed_stations():
    """Ensure all official CWC monitoring stations in Yadgir District network exist in database."""
    db = SessionLocal()
    try:
        active_ids = [s["station_id"] for s in OFFICIAL_STATIONS]
        legacy = db.query(Station).filter(~Station.station_id.in_(active_ids)).all()
        for leg in legacy:
            db.query(RiverObservation).filter(RiverObservation.station_id == leg.station_id).delete()
            db.query(Prediction).filter(Prediction.station_id == leg.station_id).delete()
            db.query(Alert).filter(Alert.station_id == leg.station_id).delete()
            db.delete(leg)
        db.commit()

        seed_yadgir_stations(db)
        print(f"[InitDB] Seeded/verified {len(OFFICIAL_STATIONS)} Yadgir District monitoring stations.")
    except Exception as e:
        db.rollback()
        print(f"[InitDB Error] Could not seed stations: {e}")
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    upgrade_schema_if_needed()
    seed_stations()
    db = SessionLocal()
    try:
        result = ensure_continuous_yadgir_telemetry(db)
        print(f"[InitDB] Continuous Yadgir telemetry ensured: {result['status']}, {result['stations_monitored']} stations active.")
    except Exception as e:
        db.rollback()
        print(f"[InitDB Error] Could not ensure continuous telemetry: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()