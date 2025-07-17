import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import BackgroundTasks
from app.core.config import (
    SMTP_HOST, SMTP_PORT, EMAIL_USER, EMAIL_PASS,
    EMAILS_FROM_EMAIL, EMAILS_FROM_NAME,
    CLIENT_URL, RESET_PASSWORD_TOKEN_EXPIRE_HOURS,
)

def send_email(msg: MIMEMultipart) -> None:
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def send_reset_password_email(
    email_to: str, token: str, background_tasks: BackgroundTasks
) -> None:
    link = f"{CLIENT_URL}/auth/reset-password?token={token}"
    html = f"""
      <p>Nhấn vào link dưới để đặt lại mật khẩu (hết hạn sau {RESET_PASSWORD_TOKEN_EXPIRE_HOURS}h):</p>
      <a href="{link}">{link}</a>
      <p>Nếu không phải bạn, bỏ qua email này.</p>
    """
    msg = MIMEMultipart()
    msg["From"]    = f"{EMAILS_FROM_NAME} <{EMAILS_FROM_EMAIL}>"
    msg["To"]      = email_to
    msg["Subject"] = "Đặt lại mật khẩu Habit Tracker"
    msg.attach(MIMEText(html, "html"))
    background_tasks.add_task(send_email, msg)