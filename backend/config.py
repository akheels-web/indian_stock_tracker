"""Configuration management for Indian Stock Tracker"""
import os
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database - use separate vars to avoid URL encoding issues with special chars
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "stockuser"
    DB_PASSWORD: str = "stockpass"
    DB_NAME: str = "stocktracker"

    # Legacy DATABASE_URL support (URL-encoded)
    DATABASE_URL: str = ""

    REDIS_URL: str = "redis://localhost:6379"

    # API Keys
    NEWS_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    ALPHA_VANTAGE_KEY: str = ""

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    # App
    SECRET_KEY: str = "change-me"
    ENVIRONMENT: str = "development"

    # Screening Criteria (customizable)
    MIN_ROE: float = 15.0
    MAX_DEBT_EQUITY: float = 0.5
    MIN_EPS_GROWTH: float = 10.0
    MAX_PE: float = 30.0

    # Alert Thresholds
    SENTIMENT_EXIT_THRESHOLD: float = -0.6
    STOP_LOSS_PCT: float = 8.0
    TARGET_GAIN_PCT: float = 20.0

    # News Sources for India
    NEWS_SOURCES: list = [
        "moneycontrol.com",
        "economictimes.indiatimes.com",
        "business-standard.com",
        "livemint.com",
        "cnbc-tv18.com",
        "ndtv.com/business"
    ]

    # Nifty 50 Universe (can be expanded)
    DEFAULT_UNIVERSE: list = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
        "LT.NS", "BAJFINANCE.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS",
        "TITAN.NS", "SUNPHARMA.NS", "WIPRO.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
        "POWERGRID.NS", "NTPC.NS", "M&M.NS", "TATAMOTORS.NS", "ADANIENT.NS",
        "HCLTECH.NS", "TECHM.NS", "GRASIM.NS", "CIPLA.NS", "DRREDDY.NS",
        "JSWSTEEL.NS", "TATASTEEL.NS", "SBILIFE.NS", "HDFCLIFE.NS", "EICHERMOT.NS",
        "BRITANNIA.NS", "SHREECEM.NS", "COALINDIA.NS", "ONGC.NS", "BPCL.NS",
        "HEROMOTOCO.NS", "APOLLOHOSP.NS", "BAJAJFINSV.NS", "BAJAJ-AUTO.NS",
        "INDUSINDBK.NS", "DIVISLAB.NS", "HINDALCO.NS", "UPL.NS", "TATACONSUM.NS"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def get_database_url(self) -> str:
        """Build DATABASE_URL from separate components, properly URL-encoding the password"""
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # URL-encode password to handle special characters like @, :, /, etc.
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings():
    return Settings()
