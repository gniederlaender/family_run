import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Email configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmx.at')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_SECURE = os.getenv('EMAIL_SECURE', 'false').lower() == 'true'
    EMAIL_USER = os.getenv('EMAIL_USER', 'gabor.niederlaender@gmx.at')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')

    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
