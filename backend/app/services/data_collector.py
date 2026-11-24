import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.services.nwic_service import sync_water_levels_to_db
from app.services.cwc_service import sync_discharge_to_db
from app.services.imd_service import sync_rainfall_to_db
from app.models.station import Station
from app.models.river_observation import RiverObservation
from app.models.rainfall import RainfallObservation
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.ml.predict import predict_flood_risk
from app.services.continuous_telemetry import ensure_continuous_yadgir_telemetry
from app.services.freshness_service import calculate_data_age

logger = logging.getLogger(__name__)


def run_full_data_sync(db: Session = None) -> dict:
    """
    Run complete background synchronization:
    1. Collect NWIC river water levels.
    2. Collect CWC discharge records.
    3. Collect CWC/IMD rainfall observations.
    4. Maintain 100% continuous live telemetry for Yadgir District network.
    5. Run ML predictions and evaluate safety triggers.
    """
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        logger.info("[Data Collector] Starting hydrological & meteorological synchronization for Yadgir District...")

        # 1. Sync water levels (gracefully catch network timeouts)
        try:
            wl_stats = sync_water_levels_to_db(db)
        except Exception as e:
            wl_stats = {"status": "OFFLINE_FALLBACK", "fetched": 0, "inserted": 0, "error": str(e)}
        logger.info(f"[Data Collector] Water levels: {wl_stats}")

        # 2. Sync discharge
        try:
            q_stats = sync_discharge_to_db(db)
        except Exception as e:
            q_stats = {"status": "OFFLINE_FALLBACK", "fetched": 0, "inserted": 0, "error": str(e)}
        logger.info(f"[Data Collector] Discharge: {q_stats}")

        # 3. Sync rainfall
        try:
            rain_stats = sync_rainfall_to_db(db)
        except Exception as e:
            rain_stats = {"status": "OFFLINE_FALLBACK", "fetched": 0, "inserted": 0, "error": str(e)}
        logger.info(f"[Data Collector] Rainfall: {rain_stats}")

        # 4. Guarantee 100% continuous, fresh live telemetry for Yadgir District
        yadgir_stats = ensure_continuous_yadgir_telemetry(db)
        logger.info(f"[Data Collector] Yadgir continuous telemetry: {yadgir_stats}")

        # 4. Generate/update station predictions
        stations = db.query(Station).all()
        predictions_updated = 0
        new_alerts = 0
        now = datetime.now(timezone.utc)

        for st in stations:
            latest_obs = db.query(RiverObservation).filter(
                RiverObservation.station_id == st.station_id
            ).order_by(RiverObservation.observation_time.desc()).first()

            if not latest_obs or latest_obs.water_level is None:
                continue

            # Prior observation for rate of rise
            prev_obs = db.query(RiverObservation).filter(
                RiverObservation.station_id == st.station_id,
                RiverObservation.observation_time < latest_obs.observation_time,
                RiverObservation.water_level.isnot(None)
            ).order_by(RiverObservation.observation_time.desc()).first()

            change_6h = round(latest_obs.water_level - prev_obs.water_level, 2) if prev_obs else 0.0

            # Find rainfall near station or in district
            latest_rain = db.query(RainfallObservation).filter(
                RainfallObservation.district == st.district
            ).order_by(RainfallObservation.observation_time.desc()).first()

            rain_24h = latest_rain.rainfall_24h if latest_rain else 0.0
            rain_1h = latest_rain.rainfall_1h if latest_rain else 0.0

            # Find upstream rainfall for basin
            upstream_rain_obs = db.query(RainfallObservation).filter(
                RainfallObservation.basin == st.basin,
                RainfallObservation.state != "Karnataka"
            ).order_by(RainfallObservation.observation_time.desc()).limit(10).all()

            up_rain = max([r.rainfall_24h for r in upstream_rain_obs if r.rainfall_24h], default=0.0)

            # Freshness
            _, _, freshness = calculate_data_age(latest_obs.observation_time, now)

            # Predict risk
            result = predict_flood_risk(
                water_level=latest_obs.water_level,
                discharge=latest_obs.discharge or 40.0,
                water_level_change_6h=change_6h,
                rainfall_24h=rain_24h,
                rainfall_1h=rain_1h,
                upstream_rainfall=up_rain,
                warning_level=st.warning_level,
                danger_level=st.danger_level
            )

            # Save prediction
            risk_str = str(result["risk"])
            pred_record = Prediction(
                station_id=st.station_id,
                water_level=latest_obs.water_level,
                discharge=latest_obs.discharge,
                rainfall_1h=rain_1h,
                rainfall_24h=rain_24h,
                rainfall=rain_24h,
                humidity=70.0,
                temperature=28.0,
                upstream_rainfall=up_rain,
                flood_risk=risk_str,
                risk_level=risk_str,
                confidence=float(result["confidence"]),
                model_version="RandomForest_v2.0",
                data_timestamp=latest_obs.observation_time,
                data_freshness=freshness,
                override_applied=bool(result["override_applied"]),
                override_reason=result["override_reason"],
                explanation="; ".join(result["reasons"])
            )
            db.add(pred_record)
            predictions_updated += 1

            # 5. Check if Alert should be raised
            if result["risk"] in ("HIGH", "EXTREME"):
                # Deduplication: check if active alert in last 6 hours exists
                six_hours_ago = now - timedelta(hours=6)
                recent_alert = db.query(Alert).filter(
                    Alert.station_id == st.station_id,
                    Alert.created_at >= six_hours_ago
                ).first()

                if not recent_alert:
                    alert_msg = f"{result['risk']} flood risk detected at station {st.station_name} on river {st.river} ({st.basin} Basin). Current level: {latest_obs.water_level:.2f}m. {result['reasons'][0] if result['reasons'] else ''}"
                    new_alert = Alert(
                        station_id=st.station_id,
                        risk_level=result["risk"],
                        message=alert_msg,
                        channel="SMS/EMAIL/WEB",
                        status="ACTIVE"
                    )
                    db.add(new_alert)
                    new_alerts += 1

        db.commit()
        logger.info(f"[Data Collector] Finished sync. Generated {predictions_updated} predictions, {new_alerts} alerts.")

        return {
            "status": "SUCCESS",
            "water_levels": wl_stats,
            "discharge": q_stats,
            "rainfall": rain_stats,
            "predictions_generated": predictions_updated,
            "alerts_created": new_alerts,
            "timestamp": now.isoformat()
        }

    except Exception as e:
        db.rollback()
        logger.error(f"[Data Collector] Sync failed: {e}", exc_info=True)
        return {
            "status": "ERROR",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    finally:
        if close_session:
            db.close()
