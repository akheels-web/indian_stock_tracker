"""Pydantic schemas for API"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models import StockStatus, AlertType, AlertSeverity


# ========== Stock Schemas ==========
class StockBase(BaseModel):
    symbol: str
    name: Optional[str] = None
    sector: Optional[str] = None


class StockCreate(StockBase):
    pass


class StockUpdate(BaseModel):
    status: Optional[StockStatus] = None
    stop_loss_price: Optional[float] = None
    target_price: Optional[float] = None
    alert_enabled: Optional[bool] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class StockResponse(StockBase):
    id: int
    status: StockStatus
    current_price: Optional[float] = None
    first_tracked_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_equity: Optional[float] = None
    fundamental_score: float
    technical_score: float
    sentiment_score: float
    overall_score: float
    volatility: Optional[float] = None
    stop_loss_price: Optional[float] = None
    target_price: Optional[float] = None
    alert_enabled: bool
    added_date: datetime
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class StockDetailResponse(StockResponse):
    news_articles: List["NewsArticleResponse"] = []
    price_history: List["PriceHistoryResponse"] = []
    alerts: List["AlertResponse"] = []

    class Config:
        from_attributes = True


# ========== News Schemas ==========
class NewsArticleBase(BaseModel):
    title: str
    url: Optional[str] = None
    source: Optional[str] = None


class NewsArticleResponse(NewsArticleBase):
    id: int
    stock_id: int
    published_at: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    confidence: Optional[float] = None
    summary: Optional[str] = None
    key_points: List[str] = []
    risk_flags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class SentimentTrend(BaseModel):
    date: str
    avg_sentiment: float
    article_count: int
    positive_count: int
    negative_count: int


# ========== Alert Schemas ==========
class AlertBase(BaseModel):
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    message: Optional[str] = None


class AlertResponse(AlertBase):
    id: int
    stock_id: int
    stock_symbol: str
    trigger_price: Optional[float] = None
    is_read: bool
    is_acknowledged: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertStats(BaseModel):
    total_alerts: int
    unread_count: int
    critical_count: int
    high_count: int
    by_type: dict


# ========== Dashboard Schemas ==========
class DashboardStats(BaseModel):
    total_stocks: int
    watching_count: int
    holding_count: int
    exited_count: int
    total_alerts: int
    unread_alerts: int
    critical_alerts: int
    avg_overall_score: float
    best_performer: Optional[str] = None
    worst_performer: Optional[str] = None


class WeeklyPick(BaseModel):
    stock: StockResponse
    recommendation: str
    confidence: float
    reasoning: str


class DashboardResponse(BaseModel):
    stats: DashboardStats
    weekly_picks: List[WeeklyPick]
    recent_alerts: List[AlertResponse]
    sentiment_overview: List[SentimentTrend]


# ========== Report Schemas ==========
class WeeklyReportResponse(BaseModel):
    id: int
    stock_id: int
    stock_symbol: str
    week_start: datetime
    week_end: datetime
    week_open: Optional[float] = None
    week_close: Optional[float] = None
    weekly_overall_score: float
    recommendation: str
    confidence: Optional[float] = None
    reasoning: Optional[str] = None
    news_count: int
    positive_news: int
    negative_news: int
    created_at: datetime

    class Config:
        from_attributes = True


# ========== Price History ==========
class PriceHistoryResponse(BaseModel):
    id: int
    stock_id: int
    date: datetime
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[int] = None

    class Config:
        from_attributes = True
