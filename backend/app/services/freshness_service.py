from datetime import datetime, timezone, timedelta
from typing import Literal

FreshnessStatus = Literal["RECENT", "STALE", "UNAVAILABLE"]

# Configurable thresholds
HOURLY_TELEMETRY_FRESHNESS_HOURS = 48  # Within 48 hours is considered RECENT for CWC telemetry
DAILY_DISCHARGE_FRESHNESS_HOURS = 72    # Within 72 hours is considered RECENT for manual daily discharge


def calculate_data_age(obs_time: datetime | None, now: datetime | None = None) -> tuple[float | None, str, FreshnessStatus]:
    """
    Calculate observation age in hours, human-readable age string, and freshness status.
    Returns: (age_in_hours, human_readable_age, freshness_status)
    """
    if not obs_time:
        return None, "No observation available", "UNAVAILABLE"

    if now is None:
        now = datetime.now(timezone.utc)

    # Ensure tz-aware comparison
    if obs_time.tzinfo is None:
        # Assume local IST (+05:30) or UTC; convert to UTC
        obs_time_utc = obs_time.replace(tzinfo=timezone(timedelta(hours=5, minutes=30))).astimezone(timezone.utc)
    else:
        obs_time_utc = obs_time.astimezone(timezone.utc)

    diff = now - obs_time_utc
    age_seconds = diff.total_seconds()

    if age_seconds < 0:
        # Clock skew / slightly in the future
        age_hours = 0.0
        human_age = "Just now"
        status: FreshnessStatus = "RECENT"
        return age_hours, human_age, status

    age_hours = round(age_seconds / 3600.0, 1)

    if age_hours < 1:
        minutes = max(1, int(age_seconds / 60))
        human_age = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif age_hours < 24:
        hrs = int(age_hours)
        human_age = f"{hrs} hour{'s' if hrs != 1 else ''} ago"
    elif age_hours < 48:
        human_age = "1 day ago"
    elif age_hours < 720:
        days = int(age_hours / 24)
        human_age = f"{days} days ago"
    else:
        months = int(age_hours / 720)
        human_age = f"{months} month{'s' if months != 1 else ''} ago ({obs_time.strftime('%b %Y')})"

    if age_hours <= HOURLY_TELEMETRY_FRESHNESS_HOURS:
        status = "RECENT"
    else:
        status = "STALE"

    return age_hours, human_age, status


def format_observation_timestamp(dt: datetime | None) -> str:
    """Format timestamp cleanly as 'DD Mon YYYY HH:MM IST'."""
    if not dt:
        return "N/A"
    return dt.strftime("%d %b %Y %H:%M")
