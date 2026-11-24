"""
Comprehensive Automated Verification Test for all FloodShield-AI Endpoints.
Tests database queries, route handlers, predictions, and safety overrides.
"""
import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.database import SessionLocal
from app.api.dashboard import get_dashboard_summary
from app.api.stations import get_all_stations, get_station_detail
from app.api.rivers import get_all_rivers, get_river_detail
from app.api.observations import get_latest_observations
from app.api.rainfall import get_rainfall_summary, get_weather_warnings
from app.api.upstream import get_upstream_conditions
from app.api.prediction import get_all_predictions, evaluate_custom_scenario, CustomEvaluationRequest
from app.api.alerts import get_alerts, trigger_test_alert, TestAlertRequest
from app.api.data_management import data_health

def run_tests():
    db = SessionLocal()
    passed = 0
    failed = 0

    print("==================================================")
    print(" FLOODSHIELD-AI END-TO-END ENDPOINT VERIFICATION ")
    print("==================================================")

    # 1. Dashboard Summary
    try:
        res = get_dashboard_summary(db)
        print(f"[PASS] 1. Dashboard Summary: Total Stations={res['total_stations']}, Recent={res['recent_stations']}, Low={res['low_risk']}, Med={res['medium_risk']}, High={res['high_risk']}, Extreme={res['extreme_risk']}, Alerts={res['active_alerts']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 1. Dashboard Summary: {e}")
        failed += 1

    # 2. List Stations
    station_id_to_test = None
    try:
        res = get_all_stations(db=db)
        print(f"[PASS] 2. List Stations: Retrieved {len(res)} stations.")
        if res:
            station_id_to_test = res[0]["station_id"]
            print(f"       Sample Station: {res[0]['station_name']} ({res[0]['river']} - {res[0]['basin']}) -> Risk: {res[0]['risk']}, Freshness: {res[0]['freshness']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 2. List Stations: {e}")
        failed += 1

    # 3. Station Detail
    if station_id_to_test:
        try:
            res = get_station_detail(station_id=station_id_to_test, db=db)
            print(f"[PASS] 3. Station Detail ({station_id_to_test}): Name={res['station']['station_name']}, Timeseries points={len(res['timeseries'])}, Prediction Risk={res['prediction']['risk']}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] 3. Station Detail: {e}")
            failed += 1

    # 4. List Rivers
    river_to_test = None
    try:
        res = get_all_rivers(db=db)
        print(f"[PASS] 4. List Rivers: Found {len(res)} unique rivers.")
        if res:
            river_to_test = res[0]["river"]
            print(f"       Sample Rivers: {[r['river'] for r in res[:5]]}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 4. List Rivers: {e}")
        failed += 1

    # 5. River Detail
    if river_to_test:
        try:
            res = get_river_detail(river_name=river_to_test, db=db)
            print(f"[PASS] 5. River Detail ({river_to_test}): River={res['river']}, Stations count={len(res['stations'])}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] 5. River Detail: {e}")
            failed += 1

    # 6. Latest Observations
    try:
        res = get_latest_observations(db=db)
        print(f"[PASS] 6. Latest Observations: {len(res)} observations retrieved.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 6. Latest Observations: {e}")
        failed += 1

    # 7. Rainfall Summary
    try:
        res = get_rainfall_summary(db=db)
        print(f"[PASS] 7. Rainfall Telemetry: {len(res)} stations with rainfall data.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 7. Rainfall Telemetry: {e}")
        failed += 1

    # 8. IMD Warnings
    try:
        res = get_weather_warnings()
        print(f"[PASS] 8. IMD Weather Warnings: {len(res)} active warnings/advisories.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 8. IMD Weather Warnings: {e}")
        failed += 1

    # 9. Upstream Conditions
    try:
        res = get_upstream_conditions(db=db)
        print(f"[PASS] 9. Upstream Basin Intelligence: {len(res)} major basins evaluated.")
        for b in res:
            print(f"       Basin: {b['basin']} | Upstream States: {b['upstream_states']} | Upstream Rain: {b['avg_upstream_rainfall_24h']}mm | River Trend: {b['upstream_river_trend']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 9. Upstream Basin Intelligence: {e}")
        failed += 1

    # 10. List Predictions
    try:
        res = get_all_predictions(db=db)
        print(f"[PASS] 10. List Predictions: {len(res)} model predictions in database.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 10. List Predictions: {e}")
        failed += 1

    # 11. Custom Scenario Evaluation (Viva Simulator & Safety Override Test)
    try:
        # Scenario A: Normal safe water level
        safe_scenario = CustomEvaluationRequest(
            water_level=355.0,
            warning_level=359.0,
            danger_level=361.0,
            rainfall_24h=10.0,
            upstream_rainfall=15.0,
            water_level_change_6h=0.1,
            discharge=50.0
        )
        res_safe = evaluate_custom_scenario(safe_scenario)
        print(f"[PASS] 11a. Viva Simulator (Normal Flow): Risk={res_safe['risk']}, Confidence={res_safe['confidence']:.2f}, Override={res_safe['override_applied']}")

        # Scenario B: Danger Level Exceeded (Safety Override MUST trigger)
        danger_scenario = CustomEvaluationRequest(
            water_level=362.5, # > 361.0 Danger Level!
            warning_level=359.0,
            danger_level=361.0,
            rainfall_24h=120.0,
            upstream_rainfall=180.0,
            water_level_change_6h=0.8,
            discharge=850.0
        )
        res_danger = evaluate_custom_scenario(danger_scenario)
        assert res_danger['risk'] == "EXTREME", f"Expected EXTREME, got {res_danger['risk']}"
        assert res_danger['override_applied'] == True, "Expected safety override to be applied!"
        print(f"[PASS] 11b. Safety Override Test (Danger Level Breached): Risk={res_danger['risk']}, Override={res_danger['override_applied']}, Reason='{res_danger['override_reason']}'")
        passed += 2
    except Exception as e:
        print(f"[FAIL] 11. Custom Scenario Evaluation: {e}")
        failed += 1

    # 12. Alerts
    try:
        res = get_alerts(db=db)
        print(f"[PASS] 12a. Hydrological Alerts: {len(res)} alerts registered.")
        
        # Test trigger alert
        test_alert_res = trigger_test_alert(
            req=TestAlertRequest(station_id="CWC_KR_KUDACHI", risk_level="EXTREME"),
            db=db
        )
        assert test_alert_res["status"] == "SUCCESS"
        print(f"[PASS] 12b. Trigger Test Alert: Dispatched alert ID {test_alert_res['alert']['id']} for {test_alert_res['alert']['station_name']} ({test_alert_res['alert']['risk_level']})")
        print(f"       SMS Broadcast: {test_alert_res['dispatched_channels']['sms_payload'].splitlines()[0]}")
        print(f"       Email Recipient: {test_alert_res['dispatched_channels']['email_payload']['recipient']}")
        passed += 2
    except Exception as e:
        print(f"[FAIL] 12. Hydrological Alerts: {e}")
        failed += 1

    # 13. Data Health
    try:
        res = data_health(db=db)
        print(f"[PASS] 13. Data Health Audit: {len(res)} sources audited.")
        for src in res:
            print(f"       Source: {src['source']} ({src['type']}) -> Status: {src['status']}, Total: {src['records_stored']}, Age: {src['data_age']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] 13. Data Health Audit: {e}")
        failed += 1

    db.close()
    print("==================================================")
    print(f" TOTAL TESTS: {passed + failed} | PASSED: {passed} | FAILED: {failed} ")
    print("==================================================")
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
