"""Reports API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models import WeeklyReport, Stock, StockStatus
from schemas import WeeklyReportResponse

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/weekly", response_model=List[WeeklyReportResponse])
def get_weekly_reports(
    stock_id: Optional[int] = None,
    recommendation: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get weekly screening reports"""
    query = db.query(WeeklyReport)

    if stock_id:
        query = query.filter(WeeklyReport.stock_id == stock_id)
    if recommendation:
        query = query.filter(WeeklyReport.recommendation == recommendation.upper())
    if min_score:
        query = query.filter(WeeklyReport.weekly_overall_score >= min_score)

    reports = query.order_by(desc(WeeklyReport.week_start)).limit(100).all()

    return [
        {
            "id": r.id,
            "stock_id": r.stock_id,
            "stock_symbol": r.stock.symbol,
            "week_start": r.week_start,
            "week_end": r.week_end,
            "week_open": r.week_open,
            "week_close": r.week_close,
            "weekly_overall_score": r.weekly_overall_score,
            "recommendation": r.recommendation,
            "confidence": r.confidence,
            "reasoning": r.reasoning,
            "news_count": r.news_count,
            "positive_news": r.positive_news,
            "negative_news": r.negative_news,
            "created_at": r.created_at,
        }
        for r in reports
    ]


@router.get("/weekly/latest")
def get_latest_weekly_report(stock_id: int, db: Session = Depends(get_db)):
    """Get the latest weekly report for a stock"""
    report = db.query(WeeklyReport).filter(
        WeeklyReport.stock_id == stock_id
    ).order_by(desc(WeeklyReport.week_start)).first()

    if not report:
        raise HTTPException(status_code=404, detail="No weekly report found")

    return report


@router.get("/weekly/best-picks")
def get_best_weekly_picks(min_score: float = 70, db: Session = Depends(get_db)):
    """Get best picks from latest weekly screening"""
    latest_week = db.query(WeeklyReport).order_by(desc(WeeklyReport.week_start)).first()
    if not latest_week:
        return []

    week_start = latest_week.week_start

    reports = db.query(WeeklyReport).filter(
        WeeklyReport.week_start == week_start,
        WeeklyReport.weekly_overall_score >= min_score,
        WeeklyReport.recommendation.in_(["BUY", "WATCH"])
    ).order_by(desc(WeeklyReport.weekly_overall_score)).limit(15).all()

    return [
        {
            "symbol": r.stock.symbol,
            "name": r.stock.name,
            "sector": r.stock.sector,
            "score": r.weekly_overall_score,
            "recommendation": r.recommendation,
            "confidence": r.confidence,
            "reasoning": r.reasoning,
            "positive_news": r.positive_news,
            "negative_news": r.negative_news,
        }
        for r in reports
    ]


@router.get("/performance")
def get_portfolio_performance(db: Session = Depends(get_db)):
    """Get portfolio performance summary"""
    holding_stocks = db.query(Stock).filter(Stock.status == StockStatus.HOLDING).all()

    total_invested = sum(s.first_tracked_price or 0 for s in holding_stocks)
    total_current = sum(s.current_price or 0 for s in holding_stocks)

    performance = []
    for stock in holding_stocks:
        if stock.first_tracked_price and stock.current_price:
            pnl = ((stock.current_price - stock.first_tracked_price) / stock.first_tracked_price) * 100
            performance.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "entry": stock.first_tracked_price,
                "current": stock.current_price,
                "pnl_pct": round(pnl, 2),
                "stop_loss": stock.stop_loss_price,
                "target": stock.target_price,
            })

    return {
        "total_invested": round(total_invested, 2),
        "total_current": round(total_current, 2),
        "unrealized_pnl": round(total_current - total_invested, 2),
        "unrealized_pnl_pct": round(((total_current - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0,
        "holdings": performance,
    }
