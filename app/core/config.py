import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

class Config:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "FastAPI Project")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+mysqlconnector://fastapi_db:fastapi123@localhost:3306/fastapidba")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "88AC1A95756D9259823CCA6E17145A0")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    try:
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    except ValueError:
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Default value if invalid
    
    CORS_ORIGINS: list = (
        os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
    )
    CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

    # SMTP Configuration
    SMTP_SENDER: str = os.getenv("SMTP_SENDER", "no-reply@example.com")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.example.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # Validate critical configurations
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the environment variables.")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in the environment variables.")

config = Config()

# Logging configuration (excluding sensitive data)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"Project Name: {config.PROJECT_NAME}")
logger.info(f"Version: {config.VERSION}")
logger.info(f"CORS Origins: {config.CORS_ORIGINS}")