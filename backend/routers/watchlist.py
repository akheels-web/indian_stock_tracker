"""Watchlist and stock management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from database import get_db
from models import Stock, StockStatus, PriceHistory
from schemas import StockCreate, StockUpdate, StockResponse, StockDetailResponse
from services.stock_data import stock_data_service
from services.weekly_screener import screener_service
from services.news_sentiment import news_service

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])


@router.get("/stocks", response_model=List[StockResponse])
def get_stocks(
    status: Optional[StockStatus] = None,
    sector: Optional[str] = None,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get all tracked stocks with optional filters"""
    query = db.query(Stock)

    if status:
        query = query.filter(Stock.status == status)
    if sector:
        query = query.filter(Stock.sector == sector)
    if min_score:
        query = query.filter(Stock.overall_score >= min_score)

    stocks = query.order_by(desc(Stock.overall_score)).all()
    return stocks


@router.get("/stocks/{stock_id}", response_model=StockDetailResponse)
def get_stock_detail(stock_id: int, db: Session = Depends(get_db)):
    """Get detailed view of a single stock"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@router.post("/stocks")
def add_stock(symbol: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Add a new stock to tracking"""
    # Check if already exists
    existing = db.query(Stock).filter(Stock.symbol == symbol.upper()).first()
    if existing:
        return {"message": "Stock already tracked", "stock": existing}

    # Fetch initial data
    info = stock_data_service.get_stock_info(symbol.upper())
    if not info.get("name"):
        raise HTTPException(status_code=400, detail="Could not fetch stock data")

    stock = Stock(
        symbol=symbol.upper(),
        name=info.get("name"),
        sector=info.get("sector"),
        status=StockStatus.WATCHING,
        current_price=info.get("current_price"),
        first_tracked_price=info.get("current_price"),
        pe_ratio=info.get("pe_ratio"),
        pb_ratio=info.get("pb_ratio"),
        roe=info.get("roe"),
        debt_equity=info.get("debt_equity"),
        eps_growth=info.get("eps_growth"),
        revenue_growth=info.get("revenue_growth"),
        profit_margin=info.get("profit_margin"),
        beta=info.get("beta"),
    )

    db.add(stock)
    db.commit()
    db.refresh(stock)

    # Run full screening in background
    background_tasks.add_task(run_screening_for_stock, stock.id, symbol.upper())

    return {"message": "Stock added successfully", "stock_id": stock.id}


@router.put("/stocks/{stock_id}")
def update_stock(stock_id: int, update: StockUpdate, db: Session = Depends(get_db)):
    """Update stock settings"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(stock, field, value)

    db.commit()
    db.refresh(stock)
    return stock


@router.delete("/stocks/{stock_id}")
def remove_stock(stock_id: int, db: Session = Depends(get_db)):
    """Remove a stock from tracking"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    db.delete(stock)
    db.commit()
    return {"message": "Stock removed"}


@router.post("/stocks/{stock_id}/buy")
def mark_as_bought(stock_id: int, buy_price: float, db: Session = Depends(get_db)):
    """Mark a stock as bought/invested"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    stock.status = StockStatus.HOLDING
    stock.first_tracked_price = buy_price
    stock.stop_loss_price = buy_price * 0.92  # 8% stop loss
    stock.target_price = buy_price * 1.20      # 20% target
    stock.highest_price = buy_price
    stock.lowest_price = buy_price

    db.commit()
    return {"message": f"Marked {stock.symbol} as HOLDING at ₹{buy_price}"}


@router.post("/stocks/{stock_id}/sell")
def mark_as_sold(stock_id: int, sell_price: float, db: Session = Depends(get_db)):
    """Mark a stock as sold/exited"""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    stock.status = StockStatus.EXITED
    stock.current_price = sell_price

    db.commit()
    return {"message": f"Marked {stock.symbol} as EXITED at ₹{sell_price}"}


@router.get("/stocks/{stock_id}/price-history")
def get_price_history(stock_id: int, days: int = 90, db: Session = Depends(get_db)):
    """Get price history for charting"""
    history = db.query(PriceHistory).filter(
        PriceHistory.stock_id == stock_id
    ).order_by(PriceHistory.date).all()

    return [
        {
            "date": h.date.isoformat(),
            "open": h.open_price,
            "high": h.high_price,
            "low": h.low_price,
            "close": h.close_price,
            "volume": h.volume,
        }
        for h in history
    ]


@router.get("/sectors")
def get_sectors(db: Session = Depends(get_db)):
    """Get list of all sectors in watchlist"""
    sectors = db.query(Stock.sector).distinct().all()
    return [s[0] for s in sectors if s[0]]


# Background task helper
async def run_screening_for_stock(stock_id: int, symbol: str):
    """Run screening for a newly added stock"""
    import asyncio
    from database import SessionLocal

    await asyncio.sleep(1)  # Let the transaction complete

    db = SessionLocal()
    try:
        result = screener_service.screen_stock(symbol)

        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if stock:
            stock.fundamental_score = result.get("fundamental_score", 0)
            stock.technical_score = result.get("technical_score", 0)
            stock.overall_score = result.get("overall_score", 0)
            stock.rsi_14 = result.get("rsi_14")
            stock.macd_signal = result.get("macd_signal")
            stock.trend_direction = result.get("trend_direction")
            stock.support_level = result.get("support_level")
            stock.resistance_level = result.get("resistance_level")
            stock.volatility = result.get("volatility")
            stock.sharpe_ratio = result.get("sharpe_ratio")
            stock.var_95 = result.get("var_95")
            db.commit()
    finally:
        db.close()
