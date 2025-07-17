import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
RESET_PASSWORD_TOKEN_EXPIRE_HOURS = int(os.getenv("RESET_PASSWORD_TOKEN_EXPIRE_HOURS", "1"))

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAILS_FROM_EMAIL = EMAIL_USER
EMAILS_FROM_NAME = os.getenv("EMAILS_FROM_NAME", "HabitTracker Support")

CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:8000")