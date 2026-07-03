"""Real-time exit monitoring task"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from database import SessionLocal
from models import Stock, Alert, StockStatus, AlertType, AlertSeverity
from services.stock_data import stock_data_service
from services.risk_assessment import risk_service


def run_exit_monitor():
    """Monitor holding positions for exit signals"""
    print(f"[{datetime.now()}] Running exit monitor...")

    db = SessionLocal()
    try:
        holdings = db.query(Stock).filter(Stock.status == StockStatus.HOLDING).all()

        for stock in holdings:
            try:
                current_price = stock_data_service.get_current_price(stock.symbol)
                if not current_price:
                    continue

                stock.current_price = current_price

                # Update high/low
                if stock.highest_price is None or current_price > stock.highest_price:
                    stock.highest_price = current_price
                if stock.lowest_price is None or current_price < stock.lowest_price:
                    stock.lowest_price = current_price

                # Check exit conditions
                stock_data = {
                    "current_price": current_price,
                    "first_tracked_price": stock.first_tracked_price,
                    "sentiment_score": stock.sentiment_score,
                    "stop_loss_price": stock.stop_loss_price,
                    "target_price": stock.target_price,
                }

                alerts = risk_service.generate_all_alerts(stock_data)

                for alert_data in alerts:
                    # Skip if already active
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
                        trigger_price=current_price,
                    )
                    db.add(alert)

                    # Send notification for critical/high
                    if alert_data["severity"].value in ["critical", "high"]:
                        print(f"  🚨 EXIT ALERT: {stock.symbol} - {alert_data['title']}")

                db.commit()

            except Exception as e:
                print(f"  Error monitoring {stock.symbol}: {e}")
                continue

        print(f"[{datetime.now()}] Exit monitor completed")

    finally:
        db.close()
