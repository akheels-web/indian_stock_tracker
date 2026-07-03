"""Fundamental analysis scoring service"""
from typing import Dict, Optional
from config import get_settings

settings = get_settings()


class FundamentalAnalysisService:
    """Score fundamental metrics on a 0-100 scale"""

    def score_pe(self, pe: Optional[float], sector_avg_pe: float = 25.0) -> float:
        """P/E ratio scoring: lower is generally better (value), but too low may signal trouble"""
        if pe is None or pe <= 0:
            return 50

        if pe < 10:
            return 85  # Deep value
        elif pe < sector_avg_pe * 0.7:
            return 75
        elif pe < sector_avg_pe:
            return 65
        elif pe < sector_avg_pe * 1.3:
            return 50
        elif pe < sector_avg_pe * 1.8:
            return 35
        else:
            return 20  # Expensive

    def score_pb(self, pb: Optional[float]) -> float:
        """P/B ratio scoring"""
        if pb is None or pb <= 0:
            return 50

        if pb < 1:
            return 80
        elif pb < 2:
            return 70
        elif pb < 3:
            return 55
        elif pb < 5:
            return 40
        else:
            return 25

    def score_roe(self, roe: Optional[float]) -> float:
        """ROE scoring"""
        if roe is None:
            return 50

        if roe >= 25:
            return 95
        elif roe >= 20:
            return 85
        elif roe >= 15:
            return 75
        elif roe >= 10:
            return 60
        elif roe >= 5:
            return 40
        else:
            return 20

    def score_debt_equity(self, de: Optional[float]) -> float:
        """Debt/Equity scoring: lower is better"""
        if de is None:
            return 50

        if de < 0.2:
            return 90
        elif de < 0.5:
            return 75
        elif de < 1.0:
            return 60
        elif de < 1.5:
            return 40
        else:
            return 20  # High debt risk

    def score_eps_growth(self, growth: Optional[float]) -> float:
        """EPS growth scoring"""
        if growth is None:
            return 50

        if growth >= 50:
            return 95
        elif growth >= 30:
            return 85
        elif growth >= 20:
            return 75
        elif growth >= 10:
            return 60
        elif growth >= 0:
            return 45
        else:
            return 20  # Negative growth

    def score_revenue_growth(self, growth: Optional[float]) -> float:
        """Revenue growth scoring"""
        if growth is None:
            return 50

        if growth >= 30:
            return 90
        elif growth >= 20:
            return 80
        elif growth >= 15:
            return 70
        elif growth >= 10:
            return 55
        elif growth >= 5:
            return 40
        else:
            return 25

    def score_profit_margin(self, margin: Optional[float]) -> float:
        """Profit margin scoring"""
        if margin is None:
            return 50

        if margin >= 30:
            return 90
        elif margin >= 20:
            return 80
        elif margin >= 15:
            return 70
        elif margin >= 10:
            return 55
        elif margin >= 5:
            return 40
        else:
            return 25

    def calculate_fundamental_score(self, metrics: Dict) -> Dict:
        """Calculate overall fundamental score"""
        pe_score = self.score_pe(metrics.get("pe_ratio"))
        pb_score = self.score_pb(metrics.get("pb_ratio"))
        roe_score = self.score_roe(metrics.get("roe"))
        de_score = self.score_debt_equity(metrics.get("debt_equity"))
        eps_score = self.score_eps_growth(metrics.get("eps_growth"))
        rev_score = self.score_revenue_growth(metrics.get("revenue_growth"))
        margin_score = self.score_profit_margin(metrics.get("profit_margin"))

        # Weighted average
        weights = {
            "pe": 0.15, "pb": 0.10, "roe": 0.20, "de": 0.15,
            "eps": 0.15, "revenue": 0.10, "margin": 0.15
        }

        overall = (
            pe_score * weights["pe"] +
            pb_score * weights["pb"] +
            roe_score * weights["roe"] +
            de_score * weights["de"] +
            eps_score * weights["eps"] +
            rev_score * weights["revenue"] +
            margin_score * weights["margin"]
        )

        return {
            "pe_score": round(pe_score, 1),
            "pb_score": round(pb_score, 1),
            "roe_score": round(roe_score, 1),
            "de_score": round(de_score, 1),
            "eps_score": round(eps_score, 1),
            "revenue_score": round(rev_score, 1),
            "margin_score": round(margin_score, 1),
            "fundamental_score": round(overall, 1),
            "details": {
                "pe_ratio": metrics.get("pe_ratio"),
                "pb_ratio": metrics.get("pb_ratio"),
                "roe": metrics.get("roe"),
                "debt_equity": metrics.get("debt_equity"),
                "eps_growth": metrics.get("eps_growth"),
                "revenue_growth": metrics.get("revenue_growth"),
                "profit_margin": metrics.get("profit_margin"),
            }
        }


fundamental_service = FundamentalAnalysisService()
