import os
import json
import pandas as pd
import numpy as np
import joblib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load model, encoder, and metadata
model_path = os.path.join(BASE_DIR, "flood_model.pkl")
encoder_path = os.path.join(BASE_DIR, "label_encoder.pkl")
meta_path = os.path.join(BASE_DIR, "model_metadata.json")

model = joblib.load(model_path)
encoder = joblib.load(encoder_path)

if os.path.exists(meta_path):
    with open(meta_path, "r") as f:
        metadata = json.load(f)
else:
    metadata = {"features": []}

FEATURE_NAMES = metadata.get("features", [
    "water_level", "water_level_change_1h", "water_level_change_6h", "water_level_change_24h",
    "discharge", "discharge_change", "rainfall_1h", "rainfall_6h", "rainfall_24h",
    "upstream_rainfall", "upstream_water_level", "temperature", "humidity",
    "warning_level_ratio", "danger_level_ratio"
])


def predict_flood_risk(
    water_level: float,
    rainfall: float = 0.0,
    humidity: float = 70.0,
    temperature: float = 28.0,
    discharge: float = 50.0,
    water_level_change_1h: float = 0.0,
    water_level_change_6h: float = 0.0,
    water_level_change_24h: float = 0.0,
    discharge_change: float = 0.0,
    rainfall_1h: float = 0.0,
    rainfall_6h: float = 0.0,
    rainfall_24h: float = 0.0,
    upstream_rainfall: float = 0.0,
    upstream_water_level: float = 0.0,
    warning_level: float | None = None,
    danger_level: float | None = None,
) -> dict:
    """
    Run Hybrid Flood Risk Engine:
    1. Random Forest predictive classification across 15 hydrological features.
    2. Official hydrological threshold safety layer (takes precedence when danger levels are breached).
    3. Explainability generator providing data-grounded reasons for the assessment.
    """
    # Fallbacks for rainfall accumulations if only general rainfall is provided
    if rainfall_24h == 0.0 and rainfall > 0.0:
        rainfall_24h = rainfall
    if rainfall_1h == 0.0 and rainfall > 0.0:
        rainfall_1h = round(rainfall / 8.0, 1)
    if rainfall_6h == 0.0 and rainfall > 0.0:
        rainfall_6h = round(rainfall / 2.0, 1)
    if upstream_water_level == 0.0:
        upstream_water_level = water_level

    # Compute station-specific ratios taking Mean Sea Level (MSL) datums into account
    if danger_level and danger_level > 50.0 and warning_level and warning_level > 50.0:
        # Gauge is referenced to Mean Sea Level (e.g. 300m - 600m MSL)
        if water_level >= warning_level:
            span = max(danger_level - warning_level, 1.0)
            warning_level_ratio = min(1.2, 1.0 + (water_level - warning_level) / span)
            danger_level_ratio = min(1.2, round(water_level / danger_level, 3))
        else:
            diff_below_warn = warning_level - water_level
            warning_level_ratio = max(0.1, round(1.0 - (diff_below_warn / 10.0), 3))
            danger_level_ratio = max(0.1, round(1.0 - ((danger_level - water_level) / 10.0), 3))
    else:
        # Standard relative river stage (0m - 20m)
        warning_level_ratio = round(water_level / warning_level, 3) if warning_level and warning_level > 0 else 0.5
        danger_level_ratio = round(water_level / danger_level, 3) if danger_level and danger_level > 0 else 0.5

    input_data = pd.DataFrame([{
        "water_level": water_level,
        "water_level_change_1h": water_level_change_1h,
        "water_level_change_6h": water_level_change_6h,
        "water_level_change_24h": water_level_change_24h,
        "discharge": discharge,
        "discharge_change": discharge_change,
        "rainfall_1h": rainfall_1h,
        "rainfall_6h": rainfall_6h,
        "rainfall_24h": rainfall_24h,
        "upstream_rainfall": upstream_rainfall,
        "upstream_water_level": upstream_water_level,
        "temperature": temperature,
        "humidity": humidity,
        "warning_level_ratio": warning_level_ratio,
        "danger_level_ratio": danger_level_ratio
    }])[FEATURE_NAMES]

    # --- Step 1: Model Prediction ---
    encoded_pred = model.predict(input_data)[0]
    probabilities = model.predict_proba(input_data)[0]

    predicted_risk = encoder.inverse_transform([encoded_pred])[0]
    confidence = float(probabilities[encoded_pred])

    # --- Step 2: Hybrid Official Threshold Safety Layer ---
    final_risk = predicted_risk
    override_applied = False
    override_reason = None

    if danger_level and danger_level > 0 and water_level >= danger_level:
        final_risk = "EXTREME"
        confidence = max(confidence, 0.98)
        override_applied = True
        override_reason = f"Water level ({water_level:.2f} m) has crossed official station danger level ({danger_level:.2f} m)."

    elif warning_level and warning_level > 0 and water_level >= warning_level and predicted_risk in ("LOW", "MEDIUM"):
        final_risk = "HIGH"
        confidence = max(confidence, 0.90)
        override_applied = True
        override_reason = f"Water level ({water_level:.2f} m) has exceeded official station warning level ({warning_level:.2f} m)."

    elif warning_level and warning_level > 0 and (warning_level - water_level) > 1.5 and water_level_change_6h < 0.4 and rainfall_24h < 50.0 and upstream_rainfall < 50.0:
        # Station is safely below warning level by over 1.5m with calm weather
        final_risk = "LOW"
        confidence = max(confidence, 0.95)

    # --- Step 3: Explainable Risk Reasons ---
    reasons = []

    if override_applied and override_reason:
        reasons.append(override_reason)

    if danger_level and danger_level > 0:
        if water_level >= danger_level:
            reasons.append(f"Water level ({water_level:.2f} m) has breached official danger mark ({danger_level:.2f} m).")
        elif warning_level and water_level >= warning_level:
            reasons.append(f"Water level ({water_level:.2f} m) has exceeded official warning mark ({warning_level:.2f} m).")
        elif warning_level and (warning_level - water_level) <= 1.0:
            reasons.append(f"Water level is approaching warning threshold ({warning_level:.2f} m). Buffer is only {(warning_level - water_level):.2f} m.")
        elif warning_level:
            reasons.append(f"Water level is safely {(warning_level - water_level):.2f} m below warning threshold ({warning_level:.2f} m).")
    else:
        reasons.append("Official station-specific warning/danger threshold is currently unlisted by CWC.")

    if water_level_change_6h > 0.5:
        reasons.append(f"River level has risen sharply by {water_level_change_6h:+.2f} m over the past 6 hours.")
    elif water_level_change_24h > 1.0:
        reasons.append(f"24-hour river trend shows strong increase of {water_level_change_24h:+.2f} m.")
    elif water_level_change_6h < -0.3:
        reasons.append(f"River level is receding ({water_level_change_6h:.2f} m in last 6h).")

    if upstream_rainfall >= 50.0:
        reasons.append(f"Heavy rainfall detected in upstream basin catchments ({upstream_rainfall:.1f} mm).")
    elif upstream_rainfall >= 20.0:
        reasons.append(f"Moderate upstream catchment rainfall ({upstream_rainfall:.1f} mm).")

    if rainfall_24h >= 64.5:
        reasons.append(f"Heavy 24-hour local rainfall ({rainfall_24h:.1f} mm).")
    elif rainfall_24h >= 20.0:
        reasons.append(f"Significant local precipitation in past 24 hours ({rainfall_24h:.1f} mm).")

    if discharge > 200.0:
        reasons.append(f"High discharge volume flowing through station ({discharge:.1f} m³/s).")

    if not reasons:
        reasons.append("River water levels and upstream weather metrics remain within standard seasonal baseline.")

    return {
        "risk": final_risk,
        "confidence": round(confidence, 2),
        "predicted_risk": predicted_risk,
        "override_applied": override_applied,
        "override_reason": override_reason,
        "reasons": reasons,
        "features": {
            "water_level": water_level,
            "discharge": discharge,
            "rainfall_24h": rainfall_24h,
            "upstream_rainfall": upstream_rainfall,
            "danger_level_ratio": danger_level_ratio,
            "warning_level_ratio": warning_level_ratio,
            "rate_of_rise_6h": water_level_change_6h
        }
    }