import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import get_settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_content: str) -> tuple[bool, str | None]:
    settings = get_settings()
    if not settings.mail_username or not settings.mail_password:
        logger.warning("Mail credentials not configured; skipping email send to %s", to_email)
        return False, "Mail credentials not configured"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.mail_from_name} <{settings.mail_from}>"
    message["To"] = to_email
    message.attach(MIMEText(html_content, "html"))

    try:
        if settings.mail_ssl_tls:
            server = smtplib.SMTP_SSL(settings.mail_server, settings.mail_port, timeout=15)
        else:
            server = smtplib.SMTP(settings.mail_server, settings.mail_port, timeout=15)

        with server:
            if settings.mail_starttls and not settings.mail_ssl_tls:
                server.starttls()
            server.login(settings.mail_username, settings.mail_password)
            server.sendmail(settings.mail_from, [to_email], message.as_string())
        return True, None
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
