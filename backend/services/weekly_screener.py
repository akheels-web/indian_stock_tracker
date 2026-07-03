"""Weekly stock screening service"""
import time
from typing import List, Dict
from datetime import datetime, timedelta
from config import get_settings
from services.stock_data import stock_data_service
from services.fundamental_analysis import fundamental_service
from services.technical_analysis import tech_service
from services.risk_assessment import risk_service

settings = get_settings()


class WeeklyScreenerService:
    """Screen stocks weekly for investment potential"""

    def screen_stock(self, symbol: str) -> Dict:
        """Run full screening on a single stock"""
        print(f"Screening {symbol}...")

        # Fetch data
        info = stock_data_service.get_stock_info(symbol)

        # If we got rate limited, info will have minimal data
        # Try again after a longer delay
        if not info.get("current_price"):
            print(f"  Rate limited on {symbol}, retrying after 5s...")
            time.sleep(5)
            info = stock_data_service.get_stock_info(symbol)

        hist = stock_data_service.get_historical_data(symbol, period="6mo")

        if hist.empty:
            print(f"  Warning: No historical data for {symbol}")
            # Return minimal result with whatever info we have
            return {
                "symbol": symbol,
                "name": info.get("name", symbol),
                "sector": info.get("sector", "Unknown"),
                "current_price": info.get("current_price"),
                "fundamental_score": 50.0,
                "technical_score": 50.0,
                "sentiment_score": 0.0,
                "overall_score": 35.0,
                "recommendation": "WATCH",
                "confidence": 0.3,
                "reasoning": "Limited data available due to API rate limiting",
                "pe_ratio": info.get("pe_ratio"),
                "pb_ratio": info.get("pb_ratio"),
                "roe": info.get("roe"),
                "debt_equity": info.get("debt_equity"),
                "eps_growth": info.get("eps_growth"),
                "revenue_growth": info.get("revenue_growth"),
                "profit_margin": info.get("profit_margin"),
            }

        # Calculate indicators
        tech_indicators = stock_data_service.calculate_technical_indicators(hist)
        risk_metrics = stock_data_service.calculate_risk_metrics(hist)

        # Score everything
        fundamental_result = fundamental_service.calculate_fundamental_score(info)
        technical_result = tech_service.calculate_technical_score(tech_indicators)

        # Sentiment placeholder (will be updated by daily scanner)
        sentiment_score = 0.0

        # Overall score
        overall = risk_service.calculate_overall_score(
            fundamental_result["fundamental_score"],
            technical_result["technical_score"],
            sentiment_score
        )

        # Determine recommendation
        if overall >= 75 and technical_result["technical_score"] >= 65:
            recommendation = "BUY"
            confidence = min(overall / 100, 0.95)
        elif overall >= 60:
            recommendation = "WATCH"
            confidence = overall / 100
        elif overall >= 40:
            recommendation = "HOLD"
            confidence = 0.5
        else:
            recommendation = "AVOID"
            confidence = 1 - (overall / 100)

        # Generate reasoning
        reasoning_parts = []
        if fundamental_result["fundamental_score"] >= 70:
            reasoning_parts.append("Strong fundamentals")
        if technical_result["technical_score"] >= 70:
            reasoning_parts.append("Positive technical setup")
        if fundamental_result["fundamental_score"] < 40:
            reasoning_parts.append("Weak fundamentals")
        if technical_result["technical_score"] < 40:
            reasoning_parts.append("Poor technical outlook")

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Mixed signals"

        return {
            "symbol": symbol,
            "name": info.get("name", symbol),
            "sector": info.get("sector", "Unknown"),
            "current_price": info.get("current_price") or tech_indicators.get("current_price"),
            "fundamental_score": fundamental_result["fundamental_score"],
            "technical_score": technical_result["technical_score"],
            "sentiment_score": sentiment_score,
            "overall_score": overall,
            "recommendation": recommendation,
            "confidence": round(confidence, 2),
            "reasoning": reasoning,
            "fundamental_details": fundamental_result,
            "technical_details": technical_result,
            "risk_metrics": risk_metrics,
            "pe_ratio": info.get("pe_ratio"),
            "pb_ratio": info.get("pb_ratio"),
            "roe": info.get("roe"),
            "debt_equity": info.get("debt_equity"),
            "eps_growth": info.get("eps_growth"),
            "revenue_growth": info.get("revenue_growth"),
            "profit_margin": info.get("profit_margin"),
            "rsi_14": tech_indicators.get("rsi_14"),
            "macd_signal": tech_indicators.get("macd_signal"),
            "trend_direction": tech_indicators.get("trend_direction"),
            "support_level": tech_indicators.get("support_level"),
            "resistance_level": tech_indicators.get("resistance_level"),
            "volatility": risk_metrics.get("volatility"),
            "sharpe_ratio": risk_metrics.get("sharpe_ratio"),
            "var_95": risk_metrics.get("var_95"),
            "beta": info.get("beta"),
        }

    def run_full_screen(self, universe: List[str] = None) -> List[Dict]:
        """Run screening on entire universe"""
        universe = universe or settings.DEFAULT_UNIVERSE
        results = []

        for symbol in universe:
            try:
                result = self.screen_stock(symbol)
                if "error" not in result:
                    results.append(result)
            except Exception as e:
                print(f"Error screening {symbol}: {e}")
                continue

        # Sort by overall score descending
        results.sort(key=lambda x: x.get("overall_score", 0), reverse=True)

        return results

    def get_top_picks(self, results: List[Dict], min_score: float = 65, 
                      limit: int = 10) -> List[Dict]:
        """Get top picks from screening results"""
        picks = [
            r for r in results 
            if r.get("overall_score", 0) >= min_score 
            and r.get("recommendation") in ["BUY", "WATCH"]
        ]
        return picks[:limit]


screener_service = WeeklyScreenerService()
