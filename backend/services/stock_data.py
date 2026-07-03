"""Stock data fetching service using yfinance with rate limiting"""
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from functools import lru_cache
import time
from config import get_settings

settings = get_settings()

# Global rate limiter state
_last_request_time = 0
_min_delay = 2.0  # 2 seconds between requests to avoid 429


class StockDataService:
    def __init__(self):
        self.cache = {}
        self._last_request = 0

    def _rate_limit(self):
        """Enforce minimum delay between Yahoo Finance requests"""
        elapsed = time.time() - self._last_request
        if elapsed < _min_delay:
            time.sleep(_min_delay - elapsed)
        self._last_request = time.time()

    def _ensure_suffix(self, symbol: str) -> str:
        """Ensure symbol has exchange suffix"""
        symbol = symbol.upper().strip()
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            symbol = symbol + ".NS"
        return symbol

    def get_stock_info(self, symbol: str) -> Dict:
        """Fetch comprehensive stock info from Yahoo Finance with rate limiting"""
        symbol = self._ensure_suffix(symbol)

        self._rate_limit()

        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("longName", info.get("shortName", symbol)),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "pb_ratio": info.get("priceToBook"),
                "roe": info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else None,
                "debt_equity": info.get("debtToEquity", 0) / 100 if info.get("debtToEquity") else None,
                "eps_growth": info.get("earningsGrowth", 0) * 100 if info.get("earningsGrowth") else None,
                "revenue_growth": info.get("revenueGrowth", 0) * 100 if info.get("revenueGrowth") else None,
                "profit_margin": info.get("profitMargins", 0) * 100 if info.get("profitMargins") else None,
                "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
                "beta": info.get("beta"),
                "dividend_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else None,
            }
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            # Return minimal data so the app doesn't crash
            return {
                "symbol": symbol,
                "name": symbol.replace(".NS", "").replace(".BO", ""),
                "sector": "Unknown",
                "current_price": None,
            }

    def get_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Fetch historical OHLCV data with rate limiting"""
        symbol = self._ensure_suffix(symbol)

        self._rate_limit()

        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            df.reset_index(inplace=True)
            df.columns = [c.lower().replace(" ", "_") for c in df.columns]
            return df
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price with rate limiting"""
        symbol = self._ensure_suffix(symbol)

        self._rate_limit()

        try:
            ticker = yf.Ticker(symbol)
            return ticker.info.get("currentPrice") or ticker.info.get("regularMarketPrice")
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return None

    def batch_get_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get prices for multiple stocks with rate limiting"""
        prices = {}
        for symbol in symbols:
            price = self.get_current_price(symbol)
            if price:
                prices[symbol] = price
        return prices

    def calculate_technical_indicators(self, df: pd.DataFrame) -> Dict:
        """Calculate key technical indicators"""
        if df.empty or len(df) < 50:
            return {}

        close = df["close"]
        high = df["high"]
        low = df["low"]

        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9).mean()

        # Moving Averages
        sma_20 = close.rolling(window=20).mean()
        sma_50 = close.rolling(window=50).mean()
        sma_200 = close.rolling(window=200).mean()

        # Bollinger Bands
        bb_middle = sma_20
        bb_std = close.rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)

        # ATR
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()

        # Support/Resistance (simple approach)
        recent = df.tail(20)
        support = recent["low"].min()
        resistance = recent["high"].max()

        # Trend direction
        if close.iloc[-1] > sma_50.iloc[-1] > sma_200.iloc[-1]:
            trend = "strong_uptrend"
        elif close.iloc[-1] > sma_50.iloc[-1]:
            trend = "uptrend"
        elif close.iloc[-1] < sma_50.iloc[-1] < sma_200.iloc[-1]:
            trend = "strong_downtrend"
        elif close.iloc[-1] < sma_50.iloc[-1]:
            trend = "downtrend"
        else:
            trend = "sideways"

        # MACD signal
        if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
            macd_signal = "bullish_crossover"
        elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
            macd_signal = "bearish_crossover"
        elif macd.iloc[-1] > signal.iloc[-1]:
            macd_signal = "bullish"
        else:
            macd_signal = "bearish"

        return {
            "rsi_14": round(rsi.iloc[-1], 2) if not pd.isna(rsi.iloc[-1]) else None,
            "macd": round(macd.iloc[-1], 4) if not pd.isna(macd.iloc[-1]) else None,
            "macd_signal": macd_signal,
            "sma_20": round(sma_20.iloc[-1], 2) if not pd.isna(sma_20.iloc[-1]) else None,
            "sma_50": round(sma_50.iloc[-1], 2) if not pd.isna(sma_50.iloc[-1]) else None,
            "sma_200": round(sma_200.iloc[-1], 2) if not pd.isna(sma_200.iloc[-1]) else None,
            "bb_upper": round(bb_upper.iloc[-1], 2) if not pd.isna(bb_upper.iloc[-1]) else None,
            "bb_lower": round(bb_lower.iloc[-1], 2) if not pd.isna(bb_lower.iloc[-1]) else None,
            "atr_14": round(atr.iloc[-1], 2) if not pd.isna(atr.iloc[-1]) else None,
            "support_level": round(support, 2),
            "resistance_level": round(resistance, 2),
            "trend_direction": trend,
            "current_price": round(close.iloc[-1], 2),
        }

    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate risk metrics"""
        if df.empty or len(df) < 30:
            return {}

        close = df["close"]
        returns = close.pct_change().dropna()

        # Volatility (annualized)
        volatility = returns.std() * (252 ** 0.5) * 100

        # Sharpe Ratio (assuming 6% risk-free rate for India)
        risk_free_rate = 0.06 / 252
        excess_returns = returns - risk_free_rate
        sharpe = (excess_returns.mean() / returns.std()) * (252 ** 0.5) if returns.std() != 0 else 0

        # VaR 95%
        var_95 = returns.quantile(0.05) * 100

        # Max Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100

        return {
            "volatility": round(volatility, 2),
            "sharpe_ratio": round(sharpe, 2),
            "var_95": round(var_95, 2),
            "max_drawdown": round(max_drawdown, 2),
        }


stock_data_service = StockDataService()
