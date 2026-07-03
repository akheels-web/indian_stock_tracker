"""Daily news scanning and sentiment update task"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Stock, NewsArticle, StockStatus
from services.news_sentiment import news_service
from services.risk_assessment import risk_service
from services.stock_data import stock_data_service


async def run_daily_news_scan():
    """Scan news for all tracked stocks and update sentiment"""
    print(f"[{datetime.now()}] Starting daily news scan...")

    db = SessionLocal()
    try:
        # Get all active stocks
        stocks = db.query(Stock).filter(
            Stock.status.in_([StockStatus.WATCHING, StockStatus.HOLDING])
        ).all()

        for stock in stocks:
            try:
                print(f"  Scanning news for {stock.symbol}...")

                # Fetch news
                articles = await news_service.get_company_news(stock.symbol, stock.name or stock.symbol)

                if not articles:
                    continue

                # Save articles and calculate sentiment
                total_sentiment = 0
                positive_count = 0
                negative_count = 0

                for article_data in articles:
                    # Check if article already exists
                    existing = db.query(NewsArticle).filter(
                        NewsArticle.title == article_data["title"],
                        NewsArticle.stock_id == stock.id
                    ).first()

                    if existing:
                        continue

                    article = NewsArticle(
                        stock_id=stock.id,
                        title=article_data["title"],
                        url=article_data.get("url"),
                        source=article_data.get("source"),
                        published_at=article_data.get("published_at"),
                        sentiment_score=article_data.get("sentiment_score"),
                        sentiment_label=article_data.get("sentiment_label"),
                        confidence=article_data.get("confidence"),
                        summary=article_data.get("summary"),
                        key_points=article_data.get("key_points", []),
                        risk_flags=article_data.get("risk_flags", []),
                        is_processed=True,
                    )
                    db.add(article)

                    total_sentiment += article_data.get("sentiment_score", 0)
                    if article_data.get("sentiment_label") == "positive":
                        positive_count += 1
                    elif article_data.get("sentiment_label") == "negative":
                        negative_count += 1

                # Update stock sentiment score
                if articles:
                    avg_sentiment = total_sentiment / len(articles)
                    stock.sentiment_score = round(avg_sentiment, 4)

                # Update current price
                current_price = stock_data_service.get_current_price(stock.symbol)
                if current_price:
                    stock.current_price = current_price

                    # Update high/low tracking
                    if stock.highest_price is None or current_price > stock.highest_price:
                        stock.highest_price = current_price
                    if stock.lowest_price is None or current_price < stock.lowest_price:
                        stock.lowest_price = current_price

                db.commit()

                # Check for alerts
                await check_and_create_alerts(db, stock, articles)

            except Exception as e:
                print(f"  Error processing {stock.symbol}: {e}")
                continue

        print(f"[{datetime.now()}] Daily news scan completed")

    finally:
        db.close()


async def check_and_create_alerts(db: Session, stock, articles):
    """Check conditions and create alerts"""
    from models import Alert

    stock_data = {
        "current_price": stock.current_price,
        "first_tracked_price": stock.first_tracked_price,
        "sentiment_score": stock.sentiment_score,
        "previous_sentiment": stock.sentiment_score,
        "pe_ratio": stock.pe_ratio,
        "debt_equity": stock.debt_equity,
        "roe": stock.roe,
        "eps_growth": stock.eps_growth,
        "volatility": stock.volatility,
    }

    alerts = risk_service.generate_all_alerts(stock_data, articles)

    for alert_data in alerts:
        # Check if similar alert already exists and active
        existing = db.query(Alert).filter(
            Alert.stock_id == stock.id,
            Alert.alert_type == alert_data["type"],
            Alert.is_active == True
        ).first()

        if existing:
            continue

        alert = Alert(
            stock_id=stock.id,
            alert_type=alert_data["type"],
            severity=alert_data["severity"],
            title=alert_data["title"],
            message=alert_data["message"],
            trigger_price=alert_data.get("trigger_price"),
            trigger_sentiment=alert_data.get("trigger_sentiment"),
        )
        db.add(alert)

    db.commit()

    # Send Telegram notification for critical/high alerts
    critical_alerts = [a for a in alerts if a["severity"].value in ["critical", "high"]]
    if critical_alerts:
        await send_telegram_alert(stock, critical_alerts)


async def send_telegram_alert(stock, alerts):
    """Send alert via Telegram"""
    from config import get_settings
    settings = get_settings()

    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return

    try:
        import httpx

        message = f"🚨 *ALERT: {stock.symbol}*\n\n"
        for alert in alerts:
            emoji = "🔴" if alert["severity"].value == "critical" else "🟠"
            message += f"{emoji} *{alert['title']}*\n"
            message += f"{alert['message']}\n\n"

        message += f"Current Price: ₹{stock.current_price}\n"
        message += f"Sentiment: {stock.sentiment_score:.2f}"

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": settings.TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
        }

        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, timeout=30)

    except Exception as e:
        print(f"Telegram send error: {e}")
