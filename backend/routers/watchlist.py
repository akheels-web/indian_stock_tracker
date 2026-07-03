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
def add_stock(symbol: str, db: Session = Depends(get_db)):
    """Add a new stock to tracking - fetches data synchronously"""
    symbol = symbol.upper().strip()

    # Ensure .NS suffix
    if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
        symbol = symbol + ".NS"

    # Check if already exists
    existing = db.query(Stock).filter(Stock.symbol == symbol).first()
    if existing:
        return {"message": "Stock already tracked", "stock_id": existing.id}

    # Fetch data synchronously
    print(f"Fetching data for {symbol}...")
    info = stock_data_service.get_stock_info(symbol)

    if not info or not info.get("name"):
        raise HTTPException(status_code=400, detail=f"Could not fetch stock data for {symbol}. Check symbol format.")

    # Run screening to get scores
    print(f"Running screening for {symbol}...")
    try:
        screen_result = screener_service.screen_stock(symbol)
    except Exception as e:
        print(f"Screening failed for {symbol}: {e}")
        screen_result = {}

    stock = Stock(
        symbol=symbol,
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
        fundamental_score=screen_result.get("fundamental_score", 0),
        technical_score=screen_result.get("technical_score", 0),
        overall_score=screen_result.get("overall_score", 0),
        rsi_14=screen_result.get("rsi_14"),
        macd_signal=screen_result.get("macd_signal"),
        trend_direction=screen_result.get("trend_direction"),
        support_level=screen_result.get("support_level"),
        resistance_level=screen_result.get("resistance_level"),
        volatility=screen_result.get("volatility"),
        sharpe_ratio=screen_result.get("sharpe_ratio"),
        var_95=screen_result.get("var_95"),
    )

    db.add(stock)
    db.commit()
    db.refresh(stock)

    return {"message": "Stock added successfully", "stock_id": stock.id, "name": stock.name, "price": stock.current_price}


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
