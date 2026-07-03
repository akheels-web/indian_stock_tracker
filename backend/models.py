"""SQLAlchemy models for Indian Stock Tracker"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class AlertType(str, enum.Enum):
    EXIT_STOP_LOSS = "exit_stop_loss"
    EXIT_SENTIMENT = "exit_sentiment"
    EXIT_FUNDAMENTAL = "exit_fundamental"
    TARGET_REACHED = "target_reached"
    WEEKLY_PICK = "weekly_pick"
    NEWS_ALERT = "news_alert"
    RISK_WARNING = "risk_warning"


class AlertSeverity(str, enum.Enum):
    CRITICAL = "critical"      # Immediate exit required
    HIGH = "high"              # Strong consideration to exit
    MEDIUM = "medium"          # Monitor closely
    LOW = "low"                # Informational


class StockStatus(str, enum.Enum):
    WATCHING = "watching"      # In weekly screener, not yet invested
    HOLDING = "holding"        # Currently invested
    EXITED = "exited"          # Sold/Exited
    REJECTED = "rejected"      # Failed screening


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200))
    exchange = Column(String(10), default="NSE")
    sector = Column(String(100))

    # Tracking status
    status = Column(Enum(StockStatus), default=StockStatus.WATCHING)
    added_date = Column(DateTime(timezone=True), server_default=func.now())
    first_tracked_price = Column(Float)
    current_price = Column(Float)
    highest_price = Column(Float)
    lowest_price = Column(Float)

    # Fundamental scores (updated weekly)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    roe = Column(Float)
    debt_equity = Column(Float)
    eps_growth = Column(Float)
    revenue_growth = Column(Float)
    profit_margin = Column(Float)

    # Technical scores
    rsi_14 = Column(Float)
    macd_signal = Column(String(20))
    trend_direction = Column(String(20))
    support_level = Column(Float)
    resistance_level = Column(Float)

    # Composite scores
    fundamental_score = Column(Float, default=0.0)   # 0-100
    technical_score = Column(Float, default=0.0)       # 0-100
    sentiment_score = Column(Float, default=0.0)       # -1 to +1
    overall_score = Column(Float, default=0.0)         # 0-100

    # Risk metrics
    volatility = Column(Float)
    sharpe_ratio = Column(Float)
    var_95 = Column(Float)  # Value at Risk
    beta = Column(Float)

    # Alert settings
    stop_loss_price = Column(Float)
    target_price = Column(Float)
    alert_enabled = Column(Boolean, default=True)

    # Metadata
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text)
    tags = Column(JSON, default=list)

    # Relationships
    news_articles = relationship("NewsArticle", back_populates="stock", cascade="all, delete-orphan")
    price_history = relationship("PriceHistory", back_populates="stock", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="stock", cascade="all, delete-orphan")
    weekly_reports = relationship("WeeklyReport", back_populates="stock", cascade="all, delete-orphan")


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000))
    source = Column(String(200))
    published_at = Column(DateTime(timezone=True))

    # Sentiment analysis
    sentiment_score = Column(Float)       # -1.0 to +1.0
    sentiment_label = Column(String(20))  # positive, negative, neutral
    confidence = Column(Float)            # 0.0 to 1.0

    # AI analysis
    summary = Column(Text)
    key_points = Column(JSON, default=list)
    risk_flags = Column(JSON, default=list)  # e.g., ["regulatory", "lawsuit", "earnings_miss"]

    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_processed = Column(Boolean, default=False)

    stock = relationship("Stock", back_populates="news_articles")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Integer)

    stock = relationship("Stock", back_populates="price_history")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String(300), nullable=False)
    message = Column(Text)

    # Context data
    trigger_price = Column(Float)
    trigger_sentiment = Column(Float)
    trigger_news_id = Column(Integer, ForeignKey("news_articles.id"))

    # Status
    is_read = Column(Boolean, default=False)
    is_acknowledged = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    stock = relationship("Stock", back_populates="alerts")


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    week_start = Column(DateTime(timezone=True), nullable=False)
    week_end = Column(DateTime(timezone=True), nullable=False)

    # Weekly performance
    week_open = Column(Float)
    week_close = Column(Float)
    week_high = Column(Float)
    week_low = Column(Float)
    volume_avg = Column(Float)

    # Weekly scores
    weekly_fundamental_score = Column(Float)
    weekly_technical_score = Column(Float)
    weekly_sentiment_score = Column(Float)
    weekly_overall_score = Column(Float)

    # Recommendation
    recommendation = Column(String(20))  # BUY, HOLD, SELL, WATCH
    confidence = Column(Float)
    reasoning = Column(Text)

    # News summary for the week
    news_count = Column(Integer, default=0)
    positive_news = Column(Integer, default=0)
    negative_news = Column(Integer, default=0)
    neutral_news = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    stock = relationship("Stock", back_populates="weekly_reports")


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False)  # running, success, failed
    message = Column(Text)
    details = Column(JSON)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_trace = Column(Text)
