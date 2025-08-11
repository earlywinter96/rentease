from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv()

class Config:
    # General
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")

    # Prefer a single URL if set (overrides parts)
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Individual parts with safe defaults
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD_RAW = os.getenv("DB_PASSWORD", "")       # raw value from .env
    DB_PASSWORD = quote_plus(DB_PASSWORD_RAW)            # encode once
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")               # ensure string default
    DB_NAME = os.getenv("DB_NAME", "rentease")

    # Final URI
    SQLALCHEMY_DATABASE_URI = (
        DATABASE_URL
        if DATABASE_URL
        else f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Print for debugging (optional)
    print("DB URI:", SQLALCHEMY_DATABASE_URI)
