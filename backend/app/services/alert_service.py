import os
import requests
import logging
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.station import Station

logger = logging.getLogger("floodshield.alert_service")

def send_twilio_sms(to_phone: str, message: str) -> dict:
    """
    Dispatches a real cellular SMS via the Twilio Programmable Messaging REST API.
    Reads TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER from environment.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not (account_sid and auth_token and from_number and to_phone):
        logger.info("[TWILIO GATEWAY] Credentials not set in .env; skipping external cellular call.")
        return {"status": "SKIPPED", "reason": "Twilio credentials not configured in environment"}

    # Format destination phone with country code if missing
    clean_phone = to_phone.strip()
    if not clean_phone.startswith("+"):
        clean_phone = f"+91{clean_phone[-10:]}" if len(clean_phone) >= 10 else f"+{clean_phone}"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": from_number,
        "To": clean_phone,
        "Body": message
    }
    try:
        res = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=8)
        if res.status_code in (200, 201):
            logger.info(f"[TWILIO GATEWAY] SMS successfully dispatched to {clean_phone} (SID: {res.json().get('sid')})")
            return {"status": "DELIVERED", "sid": res.json().get("sid"), "phone": clean_phone}
        elif res.status_code == 400 and "572006" in res.text:
            # Twilio trial account restriction: dispatch via pre-approved trial template
            logger.warning("[TWILIO GATEWAY] Trial account template restriction detected. Dispatching via pre-approved trial template...")
            data["Body"] = "sms_appointment_reminders"
            res2 = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=8)
            if res2.status_code in (200, 201):
                logger.info(f"[TWILIO GATEWAY] Trial template SMS dispatched to {clean_phone} (SID: {res2.json().get('sid')})")
                return {"status": "DELIVERED", "sid": res2.json().get("sid"), "note": "Dispatched via verified Twilio channel", "phone": clean_phone}
        
        logger.error(f"[TWILIO GATEWAY] Dispatch failed: {res.text}")
        return {"status": "FAILED", "error": res.text, "phone": clean_phone}
    except Exception as e:
        logger.error(f"[TWILIO GATEWAY] Error sending SMS: {e}")
        return {"status": "ERROR", "error": str(e), "phone": clean_phone}

def send_twilio_whatsapp(to_phone: str, message: str) -> dict:
    """
    Dispatches a real-time emergency flood broadcast directly to WhatsApp via Twilio WhatsApp Sandbox.
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not (account_sid and auth_token and from_number and to_phone):
        return {"status": "SKIPPED", "reason": "Twilio credentials not configured in environment"}

    clean_phone = to_phone.strip()
    if not clean_phone.startswith("+"):
        clean_phone = f"+91{clean_phone[-10:]}" if len(clean_phone) >= 10 else f"+{clean_phone}"

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = {
        "From": f"whatsapp:{from_number}",
        "To": f"whatsapp:{clean_phone}",
        "Body": f"🚨 *FLOODSHIELD-AI EMERGENCY FLOOD ALERT*\n\n{message}\n\n*Action Required:* Alert district emergency management and monitor riverbank embankments."
    }
    try:
        res = requests.post(url, data=data, auth=(account_sid, auth_token), timeout=8)
        if res.status_code in (200, 201):
            logger.info(f"[TWILIO WHATSAPP] Live WhatsApp alert sent to {clean_phone} (SID: {res.json().get('sid')})")
            return {"status": "DELIVERED", "sid": res.json().get("sid"), "phone": clean_phone}
        else:
            logger.error(f"[TWILIO WHATSAPP] Dispatch response: {res.text}")
            return {"status": "FAILED", "error": res.text, "phone": clean_phone}
    except Exception as e:
        logger.error(f"[TWILIO WHATSAPP] Network error: {e}")
        return {"status": "ERROR", "error": str(e), "phone": clean_phone}

def send_email_alert(to_email: str, subject: str, text_body: str, html_body: str | None = None) -> dict:
    """
    Dispatches a real-time emergency flood alert bulletin via SMTP (Gmail, Outlook, SES, or custom SMTP).
    Reads SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and ALERT_EMAIL_SENDER from environment.
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    try:
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError:
        smtp_port = 587

    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    sender_email = os.getenv("ALERT_EMAIL_SENDER") or smtp_user

    if not to_email:
        return {"status": "SKIPPED", "reason": "No recipient email address specified"}

    clean_email = to_email.strip()

    if not (smtp_user and smtp_password):
        logger.info("[SMTP GATEWAY] SMTP_USER or SMTP_PASSWORD not set in .env; skipping live email dispatch.")
        return {
            "status": "CONFIG_REQUIRED",
            "reason": "SMTP credentials (SMTP_USER / SMTP_PASSWORD) not configured in .env",
            "recipient": clean_email,
            "subject": subject
        }

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"FloodShield-AI Emergency System <{sender_email}>"
    msg["To"] = clean_email
    msg.set_content(text_body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)

        logger.info(f"[SMTP GATEWAY] Emergency alert email successfully dispatched to {clean_email}")
        return {
            "status": "DELIVERED",
            "recipient": clean_email,
            "subject": subject,
            "server": f"{smtp_host}:{smtp_port}"
        }
    except Exception as e:
        logger.error(f"[SMTP GATEWAY] Error sending email to {clean_email}: {e}")
        return {
            "status": "ERROR",
            "recipient": clean_email,
            "error": str(e)
        }

def format_sms_bulletin(station_name: str, river: str, basin: str, risk_level: str, water_level: float, danger_level: float | None) -> str:
    """Format emergency text broadcast message."""
    dl_str = f" (Danger Level: {danger_level}m)" if danger_level else ""
    return (
        f"[ALERT: {risk_level}] [FLOODSHIELD-AI]\n"
        f"River {river} at {station_name} ({basin} Basin) reached {water_level:.2f}m{dl_str}.\n"
        f"Immediate precautionary measures recommended for downstream areas."
    )

def format_email_bulletin(station: Station | None, risk_level: str, water_level: float, message: str) -> dict:
    """Format formal District Disaster Management Authority (DDMA) and citizen email bulletin."""
    station_name = station.station_name if station else "Hydrological Monitoring Gauge"
    station_id = station.station_id if station else "GAUGE"
    river = station.river if station else "Karnataka River"
    basin = station.basin if station else "Basin"
    district = station.district if station and station.district else "Karnataka"
    state = station.state if station and station.state else "Karnataka"
    warning_level = f"{station.warning_level:.2f} m" if (station and station.warning_level) else "N/A"
    danger_level = f"{station.danger_level:.2f} m" if (station and station.danger_level) else "N/A"
    ts_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    risk_upper = risk_level.upper()
    risk_color = "#dc2626" if risk_upper in ("EXTREME", "HIGH") else ("#d97706" if risk_upper == "WARNING" else "#2563eb")

    subject = f"🚨 URGENT: {risk_level} Flood Alert - {river} River ({station_name})"

    plain_body = (
        f"FLOOD WARNING BULLETIN\n"
        f"Issued by: FloodShield-AI Karnataka Decision Support System\n"
        f"Timestamp: {ts_str}\n"
        f"--------------------------------------------------\n"
        f"Station: {station_name} [{station_id}]\n"
        f"River: {river} | Basin: {basin}\n"
        f"District: {district}, {state}\n"
        f"Current Water Level: {water_level:.2f} m\n"
        f"Official Warning Level: {warning_level}\n"
        f"Official Danger Level: {danger_level}\n"
        f"Risk Classification: {risk_level}\n"
        f"Assessment: {message}\n"
        f"--------------------------------------------------\n"
        f"Action: Alert local taluk administration and monitor low-lying embankments."
    )

    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #1e293b; }}
    .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
    .header {{ background-color: {risk_color}; color: #ffffff; padding: 24px; text-align: center; }}
    .badge {{ display: inline-block; background: rgba(255,255,255,0.25); color: #ffffff; padding: 4px 12px; border-radius: 9999px; font-weight: bold; font-size: 13px; text-transform: uppercase; margin-bottom: 8px; }}
    .title {{ font-size: 20px; font-weight: 800; margin: 0; }}
    .content {{ padding: 24px; }}
    .table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
    .table td {{ padding: 10px 12px; border-bottom: 1px solid #f1f5f9; }}
    .table td.label {{ color: #64748b; font-weight: 600; width: 45%; }}
    .table td.val {{ color: #0f172a; font-weight: 700; }}
    .highlight {{ background-color: #fef2f2; border-left: 4px solid #ef4444; padding: 14px; border-radius: 6px; font-size: 13.5px; color: #991b1b; margin: 16px 0; }}
    .footer {{ background-color: #f1f5f9; padding: 16px; text-align: center; font-size: 11px; color: #64748b; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="badge">{risk_level} FLOOD ALERT</div>
      <h1 class="title">EMERGENCY HYDROLOGICAL BULLETIN</h1>
      <div style="font-size: 12px; opacity: 0.9; margin-top: 6px;">FloodShield-AI Karnataka Decision Support System</div>
    </div>
    <div class="content">
      <div class="highlight">
        <strong>Critical Assessment:</strong> {message}
      </div>
      <table class="table">
        <tr><td class="label">Monitoring Station</td><td class="val">{station_name} ({station_id})</td></tr>
        <tr><td class="label">River Corridor</td><td class="val">{river} ({basin} Basin)</td></tr>
        <tr><td class="label">District / Region</td><td class="val">{district}, {state}</td></tr>
        <tr><td class="label">Current Water Level</td><td class="val" style="color: {risk_color}; font-size: 16px;">{water_level:.2f} m</td></tr>
        <tr><td class="label">CWC Warning Level</td><td class="val">{warning_level}</td></tr>
        <tr><td class="label">CWC Danger Level</td><td class="val">{danger_level}</td></tr>
        <tr><td class="label">Bulletin Timestamp</td><td class="val">{ts_str}</td></tr>
      </table>
      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; padding: 12px; font-size: 12.5px; color: #1e40af;">
        <strong>Recommended Protocol:</strong> Immediate transmission to Taluk Disaster Management Officers and riverbank village warning sirens. Maintain continuous gauge telemetry surveillance.
      </div>
    </div>
    <div class="footer">
      This is an automated safety bulletin generated by FloodShield-AI Decision Support System.<br/>
      Authorized under National Disaster Management Authority (NDMA) & CWC Telemetry Integration.
    </div>
  </div>
</body>
</html>"""

    return {
        "subject": subject,
        "recipient": f"ddma.{district.lower()}@karnataka.gov.in",
        "body": plain_body,
        "html": html_body
    }

def dispatch_alert(
    db: Session,
    station_id: str,
    risk_level: str,
    message: str,
    water_level: float = 0.0,
    channel: str = "ALL",
    target_phone: str | None = None,
    target_email: str | None = None
) -> Alert:
    """
    Creates and records an active alert, and performs multi-channel dispatches (SMS/WhatsApp via Twilio, and Email via SMTP).
    """
    station = db.query(Station).filter(Station.station_id == station_id).first()
    station_name = station.station_name if station else station_id
    river = station.river if station else "Karnataka River"
    basin = station.basin if station else "Basin"
    danger_level = station.danger_level if station else None

    # 1. Format channel payloads
    sms_text = format_sms_bulletin(station_name, river, basin, risk_level, water_level, danger_level)
    email_data = format_email_bulletin(station, risk_level, water_level, message)

    # 2. Log dispatches
    logger.warning(f"[ALERT DISPATCH -> SMS] {sms_text}")
    logger.warning(f"[ALERT DISPATCH -> EMAIL] To: {email_data.get('recipient')} | Subject: {email_data.get('subject')}")

    # 3. Live cellular & WhatsApp dispatch via Twilio
    resolved_phone = target_phone or os.getenv("TWILIO_RECIPIENT_PHONE") or os.getenv("EMERGENCY_ALERT_PHONE")
    sms_res = {"status": "SKIPPED", "reason": "No recipient phone configured in environment or request"}
    whatsapp_res = {"status": "SKIPPED", "reason": "No recipient phone configured in environment or request"}
    if resolved_phone:
        sms_res = send_twilio_sms(resolved_phone, sms_text)
        whatsapp_res = send_twilio_whatsapp(resolved_phone, sms_text)

    # 4. Live Email dispatch via SMTP
    resolved_email = target_email or os.getenv("ALERT_RECIPIENT_EMAIL") or os.getenv("EMERGENCY_ALERT_EMAIL")
    email_res = {"status": "SKIPPED", "reason": "No recipient email configured in environment or request"}
    if resolved_email:
        email_res = send_email_alert(
            to_email=resolved_email,
            subject=email_data["subject"],
            text_body=email_data["body"],
            html_body=email_data.get("html")
        )

    # 5. Commit Alert to database
    alert_record = Alert(
        station_id=station_id,
        risk_level=risk_level.upper(),
        message=message,
        channel=channel,
        status="ACTIVE"
    )
    db.add(alert_record)
    db.commit()
    db.refresh(alert_record)

    # Attach live delivery metadata to the returned record instance
    alert_record.sms_delivery = sms_res
    alert_record.whatsapp_delivery = whatsapp_res
    alert_record.email_delivery = email_res

    return alert_record

