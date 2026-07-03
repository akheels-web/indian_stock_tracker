"""Dashboard API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from datetime import datetime, timedelta

from database import get_db
from models import Stock, Alert, WeeklyReport, NewsArticle, StockStatus, AlertSeverity
from schemas import DashboardResponse, DashboardStats, WeeklyPick, AlertStats, SentimentTrend

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    total = db.query(Stock).count()
    watching = db.query(Stock).filter(Stock.status == StockStatus.WATCHING).count()
    holding = db.query(Stock).filter(Stock.status == StockStatus.HOLDING).count()
    exited = db.query(Stock).filter(Stock.status == StockStatus.EXITED).count()

    total_alerts = db.query(Alert).count()
    unread = db.query(Alert).filter(Alert.is_read == False).count()
    critical = db.query(Alert).filter(Alert.severity == AlertSeverity.CRITICAL, Alert.is_active == True).count()

    avg_score = db.query(func.avg(Stock.overall_score)).scalar() or 0

    # Best/worst performers among tracked stocks
    best = db.query(Stock).filter(Stock.status.in_([StockStatus.WATCHING, StockStatus.HOLDING]))             .order_by(desc(Stock.overall_score)).first()
    worst = db.query(Stock).filter(Stock.status.in_([StockStatus.WATCHING, StockStatus.HOLDING]))              .order_by(Stock.overall_score).first()

    return DashboardStats(
        total_stocks=total,
        watching_count=watching,
        holding_count=holding,
        exited_count=exited,
        total_alerts=total_alerts,
        unread_alerts=unread,
        critical_alerts=critical,
        avg_overall_score=round(avg_score, 1),
        best_performer=best.symbol if best else None,
        worst_performer=worst.symbol if worst else None,
    )


@router.get("/weekly-picks")
def get_weekly_picks(db: Session = Depends(get_db)):
    """Get current weekly top picks"""
    stocks = db.query(Stock).filter(
        Stock.status == StockStatus.WATCHING,
        Stock.overall_score >= 65
    ).order_by(desc(Stock.overall_score)).limit(10).all()

    picks = []
    for stock in stocks:
        latest_report = db.query(WeeklyReport).filter(
            WeeklyReport.stock_id == stock.id
        ).order_by(desc(WeeklyReport.week_start)).first()

        picks.append({
            "stock": {
                "id": stock.id,
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector,
                "current_price": stock.current_price,
                "overall_score": stock.overall_score,
                "fundamental_score": stock.fundamental_score,
                "technical_score": stock.technical_score,
                "sentiment_score": stock.sentiment_score,
            },
            "recommendation": latest_report.recommendation if latest_report else "WATCH",
            "confidence": latest_report.confidence if latest_report else 0.5,
            "reasoning": latest_report.reasoning if latest_report else "Under review",
        })

    return picks


@router.get("/recent-alerts")
def get_recent_alerts(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent alerts"""
    alerts = db.query(Alert).filter(Alert.is_active == True)               .order_by(desc(Alert.created_at)).limit(limit).all()

    return [
        {
            "id": a.id,
            "stock_id": a.stock_id,
            "stock_symbol": a.stock.symbol,
            "alert_type": a.alert_type.value,
            "severity": a.severity.value,
            "title": a.title,
            "message": a.message,
            "is_read": a.is_read,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.get("/sentiment-trend")
def get_sentiment_trend(days: int = 7, db: Session = Depends(get_db)):
    """Get sentiment trend over last N days"""
    from_date = datetime.now() - timedelta(days=days)

    # Group by date
    results = db.query(
        func.date(NewsArticle.created_at).label("date"),
        func.avg(NewsArticle.sentiment_score).label("avg_sentiment"),
        func.count(NewsArticle.id).label("count"),
        func.sum(func.case((NewsArticle.sentiment_score >= 0.05, 1), else_=0)).label("positive"),
        func.sum(func.case((NewsArticle.sentiment_score <= -0.05, 1), else_=0)).label("negative"),
    ).filter(NewsArticle.created_at >= from_date)     .group_by(func.date(NewsArticle.created_at))     .order_by("date").all()

    return [
        {
            "date": str(r.date),
            "avg_sentiment": round(r.avg_sentiment or 0, 3),
            "article_count": r.count,
            "positive_count": r.positive or 0,
            "negative_count": r.negative or 0,
        }
        for r in results
    ]


@router.get("/full", response_model=DashboardResponse)
def get_full_dashboard(db: Session = Depends(get_db)):
    """Get complete dashboard data"""
    return DashboardResponse(
        stats=get_dashboard_stats(db),
        weekly_picks=get_weekly_picks(db),
        recent_alerts=get_recent_alerts(db=db),
        sentiment_overview=get_sentiment_trend(db=db),
    )
