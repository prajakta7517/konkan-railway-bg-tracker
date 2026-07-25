import json
import logging
import urllib.error
import urllib.request

from app.config import get_settings

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_email(to_email: str, subject: str, html_content: str) -> tuple[bool, str | None]:
    settings = get_settings()
    if not settings.brevo_api_key:
        logger.warning("Brevo API key not configured; skipping email send to %s", to_email)
        return False, "Brevo API key not configured"

    payload = {
        "sender": {"name": settings.mail_from_name, "email": settings.mail_from},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_content,
    }
    request = urllib.request.Request(
        BREVO_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "api-key": settings.brevo_api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=15):
            return True, None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logger.error("Brevo API error sending to %s: %s %s", to_email, exc.code, body)
        return False, f"Brevo API error {exc.code}: {body}"
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to send email to %s", to_email)
        return False, str(exc)


def send_password_reset_email(to_email: str, reset_url: str) -> tuple[bool, str | None]:
    subject = "Password Reset — Konkan Railway Corporation Limited"
    html_content = f"""
    <p>A password reset was requested for your Konkan Railway Corporation Limited account.</p>
    <p><a href="{reset_url}">Click here to reset your password</a>. This link expires in 30 minutes.</p>
    <p>If you did not request this, you can safely ignore this email.</p>
    """
    return send_email(to_email, subject, html_content)


def send_bg_expiry_email(
    to_email: str,
    assigned_to: str,
    bg_number: str,
    name_of_work: str,
    contractor_name: str,
    expiry_date: str,
    days_left: int,
) -> tuple[bool, str | None]:
    subject = f"[Action Required] Bank Guarantee {bg_number} expires in {days_left} day(s)"
    html_content = f"""
    <p>Dear {assigned_to},</p>
    <p>This is a reminder that the following Bank Guarantee is expiring soon:</p>
    <table cellpadding="6" cellspacing="0" border="1" style="border-collapse:collapse">
      <tr><td><b>BG Number</b></td><td>{bg_number}</td></tr>
      <tr><td><b>Name of Work</b></td><td>{name_of_work}</td></tr>
      <tr><td><b>Contractor</b></td><td>{contractor_name}</td></tr>
      <tr><td><b>Expiry Date</b></td><td>{expiry_date}</td></tr>
      <tr><td><b>Days Remaining</b></td><td>{days_left}</td></tr>
    </table>
    <p>Please take necessary action (renewal / extension) before the expiry date.</p>
    <p>— Konkan Railway Corporation Limited (automated notification)</p>
    """
    return send_email(to_email, subject, html_content)
