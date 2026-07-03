"""Settings and configuration endpoints"""
from fastapi import APIRouter
from config import get_settings

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/")
def get_settings_info():
    """Get current configuration (safe values only)"""
    settings = get_settings()
    return {
        "screening_criteria": {
            "min_roe": settings.MIN_ROE,
            "max_debt_equity": settings.MAX_DEBT_EQUITY,
            "min_eps_growth": settings.MIN_EPS_GROWTH,
            "max_pe": settings.MAX_PE,
        },
        "alert_thresholds": {
            "sentiment_exit": settings.SENTIMENT_EXIT_THRESHOLD,
            "stop_loss_pct": settings.STOP_LOSS_PCT,
            "target_gain_pct": settings.TARGET_GAIN_PCT,
        },
        "news_sources": settings.NEWS_SOURCES,
        "default_universe_size": len(settings.DEFAULT_UNIVERSE),
    }


@router.get("/universe")
def get_stock_universe():
    """Get the default stock universe"""
    settings = get_settings()
    return {"universe": settings.DEFAULT_UNIVERSE}
