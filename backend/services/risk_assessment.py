"""Risk assessment and alert generation service"""
from typing import Dict, Optional, List
from datetime import datetime
from config import get_settings
from models import AlertType, AlertSeverity, StockStatus

settings = get_settings()


class RiskAssessmentService:
    """Generate alerts based on risk conditions"""

    def check_stop_loss(self, current_price: float, entry_price: float, 
                        stop_loss_pct: float = None) -> Optional[Dict]:
        """Check if stop loss is hit"""
        if not entry_price or entry_price <= 0:
            return None

        stop_pct = stop_loss_pct or settings.STOP_LOSS_PCT
        stop_price = entry_price * (1 - stop_pct / 100)

        if current_price <= stop_price:
            return {
                "type": AlertType.EXIT_STOP_LOSS,
                "severity": AlertSeverity.CRITICAL,
                "title": f"STOP LOSS HIT",
                "message": f"Price ₹{current_price:.2f} dropped below stop loss ₹{stop_price:.2f} ({stop_pct}% below entry ₹{entry_price:.2f})",
                "trigger_price": current_price,
            }
        return None

    def check_target_reached(self, current_price: float, entry_price: float,
                             target_pct: float = None) -> Optional[Dict]:
        """Check if target gain is reached"""
        if not entry_price or entry_price <= 0:
            return None

        target = target_pct or settings.TARGET_GAIN_PCT
        target_price = entry_price * (1 + target / 100)

        if current_price >= target_price:
            return {
                "type": AlertType.TARGET_REACHED,
                "severity": AlertSeverity.MEDIUM,
                "title": f"TARGET REACHED",
                "message": f"Price ₹{current_price:.2f} hit target ₹{target_price:.2f} ({target}% above entry ₹{entry_price:.2f}). Consider booking profits.",
                "trigger_price": current_price,
            }
        return None

    def check_sentiment_crash(self, current_sentiment: float, 
                              previous_sentiment: float = None) -> Optional[Dict]:
        """Check if sentiment crashed below threshold"""
        threshold = settings.SENTIMENT_EXIT_THRESHOLD

        if current_sentiment <= threshold:
            return {
                "type": AlertType.EXIT_SENTIMENT,
                "severity": AlertSeverity.HIGH,
                "title": "SENTIMENT CRASH ALERT",
                "message": f"News sentiment dropped to {current_sentiment:.2f} (below threshold {threshold}). Negative news flow detected. Consider exiting position.",
                "trigger_sentiment": current_sentiment,
            }

        # Also check for sudden drop
        if previous_sentiment and (previous_sentiment - current_sentiment) > 0.5:
            return {
                "type": AlertType.EXIT_SENTIMENT,
                "severity": AlertSeverity.HIGH,
                "title": "SENTIMENT DROP ALERT",
                "message": f"News sentiment crashed from {previous_sentiment:.2f} to {current_sentiment:.2f}. Significant negative shift detected.",
                "trigger_sentiment": current_sentiment,
            }

        return None

    def check_fundamental_deterioration(self, stock_data: Dict) -> Optional[Dict]:
        """Check if fundamentals have deteriorated"""
        flags = []

        if stock_data.get("pe_ratio") and stock_data["pe_ratio"] > 50:
            flags.append(f"P/E ratio extremely high at {stock_data['pe_ratio']:.1f}")

        if stock_data.get("debt_equity") and stock_data["debt_equity"] > 2.0:
            flags.append(f"Debt/Equity dangerously high at {stock_data['debt_equity']:.2f}")

        if stock_data.get("roe") and stock_data["roe"] < 5:
            flags.append(f"ROE very low at {stock_data['roe']:.1f}%")

        if stock_data.get("eps_growth") and stock_data["eps_growth"] < -20:
            flags.append(f"EPS growth severely negative at {stock_data['eps_growth']:.1f}%")

        if flags:
            return {
                "type": AlertType.EXIT_FUNDAMENTAL,
                "severity": AlertSeverity.HIGH,
                "title": "FUNDAMENTAL DETERIORATION",
                "message": "; ".join(flags) + ". Fundamentals have weakened significantly.",
            }
        return None

    def check_risk_flags_in_news(self, articles: List[Dict]) -> Optional[Dict]:
        """Check for critical risk flags in recent news"""
        critical_flags = ["regulatory", "legal", "fraud", "scam", "bankruptcy", "insolvency"]

        flagged_articles = []
        for article in articles:
            risk_flags = article.get("risk_flags", [])
            if any(flag in critical_flags for flag in risk_flags):
                flagged_articles.append(article)

        if flagged_articles:
            titles = [a["title"][:60] for a in flagged_articles[:3]]
            return {
                "type": AlertType.RISK_WARNING,
                "severity": AlertSeverity.CRITICAL,
                "title": "CRITICAL RISK FLAGS IN NEWS",
                "message": f"Detected {len(flagged_articles)} articles with critical risk flags: {' | '.join(titles)}",
            }
        return None

    def check_volatility_spike(self, current_volatility: float, 
                                avg_volatility: float = None) -> Optional[Dict]:
        """Check for unusual volatility"""
        if not current_volatility:
            return None

        if current_volatility > 50:  # Very high volatility
            return {
                "type": AlertType.RISK_WARNING,
                "severity": AlertSeverity.MEDIUM,
                "title": "HIGH VOLATILITY WARNING",
                "message": f"Volatility spiked to {current_volatility:.1f}%. Unusual price swings detected.",
            }
        return None

    def generate_all_alerts(self, stock_data: Dict, articles: List[Dict] = None) -> List[Dict]:
        """Generate all applicable alerts for a stock"""
        alerts = []

        # Stop loss check
        alert = self.check_stop_loss(
            stock_data.get("current_price", 0),
            stock_data.get("first_tracked_price", 0)
        )
        if alert:
            alerts.append(alert)

        # Target check
        alert = self.check_target_reached(
            stock_data.get("current_price", 0),
            stock_data.get("first_tracked_price", 0)
        )
        if alert:
            alerts.append(alert)

        # Sentiment check
        alert = self.check_sentiment_crash(
            stock_data.get("sentiment_score", 0),
            stock_data.get("previous_sentiment")
        )
        if alert:
            alerts.append(alert)

        # Fundamental check
        alert = self.check_fundamental_deterioration(stock_data)
        if alert:
            alerts.append(alert)

        # News risk flags
        if articles:
            alert = self.check_risk_flags_in_news(articles)
            if alert:
                alerts.append(alert)

        # Volatility check
        alert = self.check_volatility_spike(stock_data.get("volatility"))
        if alert:
            alerts.append(alert)

        return alerts

    def calculate_overall_score(self, fundamental: float, technical: float, 
                                 sentiment: float) -> float:
        """Calculate weighted overall investment score"""
        # Sentiment is -1 to +1, convert to 0-100
        sentiment_100 = (sentiment + 1) * 50

        weights = {"fundamental": 0.40, "technical": 0.35, "sentiment": 0.25}

        overall = (
            fundamental * weights["fundamental"] +
            technical * weights["technical"] +
            sentiment_100 * weights["sentiment"]
        )

        return round(overall, 1)


risk_service = RiskAssessmentService()
