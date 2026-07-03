"""Weekly stock screening task"""
from datetime import datetime, timedelta
from database import SessionLocal
from models import Stock, WeeklyReport, StockStatus, PriceHistory
from services.weekly_screener import screener_service
from services.stock_data import stock_data_service


def run_weekly_screening():
    """Run weekly screening on the full universe"""
    print(f"[{datetime.now()}] Starting weekly screening...")

    db = SessionLocal()
    try:
        # Run screening
        results = screener_service.run_full_screen()

        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=6)

        for result in results:
            symbol = result["symbol"]

            # Find or create stock record
            stock = db.query(Stock).filter(Stock.symbol == symbol).first()

            if not stock:
                # Create new watching entry
                stock = Stock(
                    symbol=symbol,
                    name=result.get("name"),
                    sector=result.get("sector"),
                    status=StockStatus.WATCHING,
                    current_price=result.get("current_price"),
                    first_tracked_price=result.get("current_price"),
                )
                db.add(stock)
                db.commit()
                db.refresh(stock)

            # Update stock scores
            stock.fundamental_score = result.get("fundamental_score", 0)
            stock.technical_score = result.get("technical_score", 0)
            stock.overall_score = result.get("overall_score", 0)
            stock.pe_ratio = result.get("pe_ratio")
            stock.pb_ratio = result.get("pb_ratio")
            stock.roe = result.get("roe")
            stock.debt_equity = result.get("debt_equity")
            stock.eps_growth = result.get("eps_growth")
            stock.revenue_growth = result.get("revenue_growth")
            stock.profit_margin = result.get("profit_margin")
            stock.rsi_14 = result.get("rsi_14")
            stock.macd_signal = result.get("macd_signal")
            stock.trend_direction = result.get("trend_direction")
            stock.support_level = result.get("support_level")
            stock.resistance_level = result.get("resistance_level")
            stock.volatility = result.get("volatility")
            stock.sharpe_ratio = result.get("sharpe_ratio")
            stock.var_95 = result.get("var_95")
            stock.beta = result.get("beta")

            # Create weekly report
            report = WeeklyReport(
                stock_id=stock.id,
                week_start=week_start,
                week_end=week_end,
                week_open=result.get("current_price"),  # Simplified
                week_close=result.get("current_price"),
                weekly_fundamental_score=result.get("fundamental_score"),
                weekly_technical_score=result.get("technical_score"),
                weekly_sentiment_score=result.get("sentiment_score", 0),
                weekly_overall_score=result.get("overall_score"),
                recommendation=result.get("recommendation"),
                confidence=result.get("confidence"),
                reasoning=result.get("reasoning"),
            )
            db.add(report)

            # Update price history
            try:
                hist = stock_data_service.get_historical_data(symbol, period="1wk")
                if not hist.empty:
                    last_row = hist.iloc[-1]
                    ph = PriceHistory(
                        stock_id=stock.id,
                        date=datetime.now(),
                        open_price=last_row.get("open"),
                        high_price=last_row.get("high"),
                        low_price=last_row.get("low"),
                        close_price=last_row.get("close"),
                        volume=last_row.get("volume"),
                    )
                    db.add(ph)
            except Exception as e:
                print(f"  Price history error for {symbol}: {e}")

        db.commit()
        print(f"[{datetime.now()}] Weekly screening completed. {len(results)} stocks screened.")

    finally:
        db.close()
