# Authentication helpers: OTP generation, expiry, email delivery, password reset

import random
import time
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


def is_expired(created_at: float, max_age_sec: int = 300) -> bool:
    return (time.time() - float(created_at or 0)) > max_age_sec


def _send_email(app, recipient: str, subject: str, html_body: str, plain_body: str) -> bool:
    """Core email sender — returns True on success."""
    if not app.config.get("MAIL_ENABLED"):
        return False
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = app.config.get("MAIL_FROM") or app.config["MAIL_USERNAME"]
    msg["To"]      = recipient
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body,  "html"))
    try:
        with smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"], timeout=12) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            smtp.sendmail(msg["From"], [recipient], msg.as_string())
        logger.info("Email sent to %s | subject: %s", recipient, subject)
        return True
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP auth failed. Use a Gmail App Password, not your account password.")
        return False
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)
        return False


def send_otp_email(app, recipient: str, otp: str) -> bool:
    """
    Send login OTP to the staff member's own registered email address.
    recipient must be user["username"] — never a hardcoded address.
    """
    html_body = f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:460px;margin:0 auto;
                padding:36px;background:#0c1929;border-radius:16px;
                border:1px solid rgba(201,168,76,.25);">
      <p style="font-family:Georgia,serif;font-size:22px;color:#e3c77a;margin:0 0 4px;">Grand Prestige Hotel</p>
      <p style="font-size:11px;color:#8a99b3;letter-spacing:.1em;text-transform:uppercase;margin:0 0 28px;">Secure Staff Portal</p>
      <p style="font-size:14px;color:#c8bfa3;margin:0 0 18px;">Your one-time login code:</p>
      <div style="text-align:center;padding:20px 0;">
        <span style="font-size:42px;font-weight:900;letter-spacing:14px;color:#e3c77a;font-family:monospace;">{otp}</span>
      </div>
      <p style="font-size:13px;color:#8a99b3;margin:18px 0 0;">
        This code expires in <strong style="color:#e8a830;">5 minutes</strong>. Do not share it with anyone.</p>
      <hr style="border:none;border-top:1px solid rgba(201,168,76,.18);margin:24px 0;"/>
      <p style="font-size:11px;color:#555;">If you did not request this code, contact your system administrator.</p>
    </div>
    """
    plain_body = f"Grand Prestige Hotel — Your login OTP: {otp}. Expires in 5 minutes."
    return _send_email(app, recipient, "Your Login Code — Grand Prestige Hotel", html_body, plain_body)


def send_password_reset_otp(app, recipient: str, otp: str) -> bool:
    """Send a password-reset OTP to the staff member's registered email."""
    html_body = f"""
    <div style="font-family:'DM Sans',Arial,sans-serif;max-width:460px;margin:0 auto;
                padding:36px;background:#0c1929;border-radius:16px;
                border:1px solid rgba(201,168,76,.25);">
      <p style="font-family:Georgia,serif;font-size:22px;color:#e3c77a;margin:0 0 4px;">Grand Prestige Hotel</p>
      <p style="font-size:11px;color:#8a99b3;letter-spacing:.1em;text-transform:uppercase;margin:0 0 28px;">Password Reset</p>
      <p style="font-size:14px;color:#c8bfa3;margin:0 0 18px;">Use the code below to reset your password:</p>
      <div style="text-align:center;padding:20px 0;">
        <span style="font-size:42px;font-weight:900;letter-spacing:14px;color:#e3c77a;font-family:monospace;">{otp}</span>
      </div>
      <p style="font-size:13px;color:#8a99b3;margin:18px 0 0;">
        This code expires in <strong style="color:#e8a830;">5 minutes</strong>. Do not share it with anyone.</p>
      <hr style="border:none;border-top:1px solid rgba(201,168,76,.18);margin:24px 0;"/>
      <p style="font-size:11px;color:#555;">If you did not request a password reset, ignore this email.</p>
    </div>
    """
    plain_body = f"Grand Prestige Hotel — Your password reset OTP: {otp}. Expires in 5 minutes."
    return _send_email(app, recipient, "Password Reset Code — Grand Prestige Hotel", html_body, plain_body)
