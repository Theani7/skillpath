"""SMTP email sending for OTP verification and password resets.

Uses the Python standard library (`smtplib`) so no extra dependencies are
needed. Configured for Gmail SMTP with a Google App Password:

    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=465            # 465 = SSL (default), 587 = STARTTLS
    SMTP_USERNAME=you@gmail.com
    SMTP_PASSWORD=xxxx xxxx xxxx xxxx   # Google App Password, not the normal login
    SMTP_FROM_NAME=SkillPath
    SMTP_STARTTLS=false
"""

import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger("resume-analyzer")

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USERNAME)
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "SkillPath")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "").lower() in ("1", "true", "yes")


def email_configured() -> bool:
    return bool(SMTP_USERNAME and SMTP_PASSWORD)


def _render_template(title: str, heading: str, code: str, hint: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<body style="margin:0;padding:0;background:#f4f6f9;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:32px 16px;">
    <tr><td align="center">
      <table role="presentation" width="520" cellpadding="0" cellspacing="0" style="max-width:520px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e7ecf2;">
        <tr>
          <td style="padding:28px 32px;background:#0f1c2e;">
            <span style="color:#ffffff;font-size:20px;font-weight:800;letter-spacing:-0.3px;">Skill<span style="color:#ff6b35;">Path</span></span>
          </td>
        </tr>
        <tr>
          <td style="padding:32px;">
            <h1 style="margin:0 0 8px;font-size:18px;color:#0f172a;">{heading}</h1>
            <p style="margin:0 0 24px;font-size:14px;color:#64748b;line-height:1.6;">{hint}</p>
            <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 auto 24px;">
              <tr>
                <td style="background:#fff7f0;border:1px dashed #ff6b35;border-radius:12px;padding:14px 32px;letter-spacing:10px;font-size:28px;font-weight:800;color:#0f172a;">{code}</td>
              </tr>
            </table>
            <p style="margin:0;font-size:12px;color:#94a3b8;line-height:1.6;">This code expires in 10 minutes. If you didn't request it, you can safely ignore this email.</p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 32px;background:#f8fafc;border-top:1px solid #e7ecf2;">
            <p style="margin:0;font-size:12px;color:#94a3b8;">© {os.getenv("SMTP_FROM_NAME", "SkillPath")} · Skill gap analysis, career coaching, and learning roadmaps.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email(to_email: str, subject: str, html_body: str) -> bool:
    """Send an HTML email over SMTP. Returns True on success."""
    if not email_configured():
        logger.warning(
            "SMTP not configured (SMTP_USERNAME / SMTP_PASSWORD missing) – email to %s not sent.",
            to_email,
        )
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if SMTP_STARTTLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.ehlo()
                server.starttls(context=ssl.create_default_context())
                server.ehlo()
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_email], msg.as_string())
        else:
            with smtplib.SMTP_SSL(
                SMTP_HOST, SMTP_PORT, timeout=30, context=ssl.create_default_context()
            ) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(SMTP_FROM, [to_email], msg.as_string())
        logger.info("Email sent to %s (subject: %s)", to_email, subject)
        return True
    except Exception as e:
        logger.error("SMTP send failed to %s: %s", to_email, e)
        return False


def send_otp_email(to_email: str, otp: str, purpose: str) -> bool:
    """Send a styled OTP email. `purpose` is 'register' or 'password_reset'."""
    if purpose == "password_reset":
        subject = "Your SkillPath password reset code"
        heading = "Reset your password"
        hint = (
            "We received a request to reset your SkillPath password. "
            "Enter the code below to choose a new password."
        )
    else:
        subject = "Verify your SkillPath email"
        heading = "Verify your email address"
        hint = (
            "Welcome to SkillPath! Enter the code below to activate your account "
            "and start analyzing your resume."
        )
    return send_email(to_email, subject, _render_template(subject, heading, otp, hint))
