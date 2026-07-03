"""Technical analysis scoring service"""
from typing import Dict


class TechnicalAnalysisService:
    """Score technical indicators on a 0-100 scale"""

    def score_rsi(self, rsi: float) -> float:
        """RSI scoring: 30-70 is neutral zone, <30 oversold (buy), >70 overbought (sell)"""
        if rsi is None:
            return 50
        if rsi < 30:
            return 80  # Oversold - potential buy
        elif rsi < 40:
            return 70
        elif rsi < 50:
            return 60
        elif rsi < 60:
            return 50
        elif rsi < 70:
            return 40
        else:
            return 20  # Overbought - caution

    def score_macd(self, macd_signal: str) -> float:
        """MACD signal scoring"""
        scores = {
            "bullish_crossover": 90,
            "bullish": 70,
            "bearish_crossover": 20,
            "bearish": 30,
        }
        return scores.get(macd_signal, 50)

    def score_trend(self, trend: str) -> float:
        """Trend direction scoring"""
        scores = {
            "strong_uptrend": 90,
            "uptrend": 70,
            "sideways": 50,
            "downtrend": 30,
            "strong_downtrend": 10,
        }
        return scores.get(trend, 50)

    def score_moving_averages(self, current_price: float, sma_20: float, 
                               sma_50: float, sma_200: float) -> float:
        """Score based on price vs moving averages"""
        if not all([current_price, sma_20, sma_50, sma_200]):
            return 50

        score = 50

        # Price above all MAs = bullish
        if current_price > sma_20 > sma_50 > sma_200:
            score = 90
        elif current_price > sma_20 > sma_50:
            score = 75
        elif current_price > sma_50:
            score = 60
        # Price below all MAs = bearish
        elif current_price < sma_20 < sma_50 < sma_200:
            score = 10
        elif current_price < sma_20 < sma_50:
            score = 25
        elif current_price < sma_50:
            score = 40

        return score

    def score_bollinger(self, current_price: float, bb_upper: float, bb_lower: float) -> float:
        """Bollinger Bands scoring"""
        if not all([current_price, bb_upper, bb_lower]) or bb_upper == bb_lower:
            return 50

        position = (current_price - bb_lower) / (bb_upper - bb_lower)

        if position < 0.1:
            return 85  # Near lower band - potential bounce
        elif position < 0.3:
            return 70
        elif position < 0.7:
            return 50  # Middle zone
        elif position < 0.9:
            return 35
        else:
            return 20  # Near upper band - potential reversal

    def calculate_technical_score(self, indicators: Dict) -> Dict:
        """Calculate overall technical score from indicators"""
        rsi_score = self.score_rsi(indicators.get("rsi_14"))
        macd_score = self.score_macd(indicators.get("macd_signal", ""))
        trend_score = self.score_trend(indicators.get("trend_direction", ""))
        ma_score = self.score_moving_averages(
            indicators.get("current_price"),
            indicators.get("sma_20"),
            indicators.get("sma_50"),
            indicators.get("sma_200"),
        )
        bb_score = self.score_bollinger(
            indicators.get("current_price"),
            indicators.get("bb_upper"),
            indicators.get("bb_lower"),
        )

        # Weighted average
        weights = {"rsi": 0.20, "macd": 0.20, "trend": 0.25, "ma": 0.20, "bb": 0.15}
        overall = (
            rsi_score * weights["rsi"] +
            macd_score * weights["macd"] +
            trend_score * weights["trend"] +
            ma_score * weights["ma"] +
            bb_score * weights["bb"]
        )

        return {
            "rsi_score": round(rsi_score, 1),
            "macd_score": round(macd_score, 1),
            "trend_score": round(trend_score, 1),
            "ma_score": round(ma_score, 1),
            "bb_score": round(bb_score, 1),
            "technical_score": round(overall, 1),
            "details": {
                "rsi": indicators.get("rsi_14"),
                "macd_signal": indicators.get("macd_signal"),
                "trend": indicators.get("trend_direction"),
                "sma_20": indicators.get("sma_20"),
                "sma_50": indicators.get("sma_50"),
                "sma_200": indicators.get("sma_200"),
                "bb_upper": indicators.get("bb_upper"),
                "bb_lower": indicators.get("bb_lower"),
            }
        }


tech_service = TechnicalAnalysisService()
