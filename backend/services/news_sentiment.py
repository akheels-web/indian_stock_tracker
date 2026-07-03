"""News fetching and sentiment analysis service"""
import httpx
import feedparser
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
from config import get_settings

settings = get_settings()
analyzer = SentimentIntensityAnalyzer()

# Indian financial news RSS feeds
RSS_FEEDS = [
    "https://www.moneycontrol.com/rss/business.xml",
    "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
    "https://www.business-standard.com/rss/markets-106.rss",
    "https://www.livemint.com/rss/markets",
]

# Keywords that indicate risk/fishy situations
RISK_KEYWORDS = {
    "regulatory": ["sebi", "regulatory", "investigation", "probe", "violation", "penalty", "fine"],
    "legal": ["lawsuit", "litigation", "court", "legal", "fraud", "scam"],
    "financial": ["loss", "default", "bankruptcy", "insolvency", "debt", "write-off"],
    "management": ["resign", "quit", "ceo exit", "board", "corporate governance"],
    "earnings": ["miss", "below estimate", "profit warning", "guidance cut"],
    "operations": ["plant shutdown", "recall", "safety", "fire", "accident"],
}


class NewsSentimentService:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze_text(self, text: str) -> Dict:
        """Analyze sentiment of a text using VADER"""
        scores = self.analyzer.polarity_scores(text)

        if scores["compound"] >= 0.05:
            label = "positive"
        elif scores["compound"] <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "compound": round(scores["compound"], 4),
            "positive": round(scores["pos"], 4),
            "negative": round(scores["neg"], 4),
            "neutral": round(scores["neu"], 4),
            "label": label,
            "confidence": abs(scores["compound"]),
        }

    def detect_risk_flags(self, text: str) -> List[str]:
        """Detect risk flags in news text"""
        text_lower = text.lower()
        flags = []

        for category, keywords in RISK_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                flags.append(category)

        return flags

    def extract_key_points(self, text: str) -> List[str]:
        """Extract key points from news text using simple heuristics"""
        sentences = re.split(r'[.!?]+', text)
        key_points = []

        important_words = ["profit", "loss", "revenue", "growth", "decline", 
                          "acquisition", "merger", "dividend", "launch", "contract"]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and any(word in sentence.lower() for word in important_words):
                key_points.append(sentence)

        return key_points[:5]  # Top 5 key points

    async def fetch_news_api(self, query: str, days: int = 7) -> List[Dict]:
        """Fetch news from NewsAPI"""
        if not settings.NEWS_API_KEY:
            return []

        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{query} India stock market",
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": 20,
            "apiKey": settings.NEWS_API_KEY,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=30)
                data = response.json()

                articles = []
                for article in data.get("articles", []):
                    text = f"{article.get('title', '')} {article.get('description', '')}"
                    sentiment = self.analyze_text(text)

                    articles.append({
                        "title": article.get("title", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "Unknown"),
                        "published_at": article.get("publishedAt"),
                        "sentiment_score": sentiment["compound"],
                        "sentiment_label": sentiment["label"],
                        "confidence": sentiment["confidence"],
                        "summary": article.get("description", ""),
                        "key_points": self.extract_key_points(text),
                        "risk_flags": self.detect_risk_flags(text),
                    })

                return articles
            except Exception as e:
                print(f"NewsAPI error: {e}")
                return []

    def fetch_rss_news(self, symbol: str, company_name: str) -> List[Dict]:
        """Fetch news from RSS feeds"""
        articles = []
        search_terms = [symbol.replace(".NS", ""), company_name.split()[0]]

        for feed_url in RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:  # Top 10 per feed
                    title = entry.get("title", "")
                    summary = entry.get("summary", entry.get("description", ""))
                    text = f"{title} {summary}"

                    # Check if article mentions the company
                    if any(term.lower() in text.lower() for term in search_terms):
                        sentiment = self.analyze_text(text)

                        articles.append({
                            "title": title,
                            "url": entry.get("link", ""),
                            "source": feed.feed.get("title", "RSS"),
                            "published_at": entry.get("published", entry.get("updated")),
                            "sentiment_score": sentiment["compound"],
                            "sentiment_label": sentiment["label"],
                            "confidence": sentiment["confidence"],
                            "summary": summary[:500],
                            "key_points": self.extract_key_points(text),
                            "risk_flags": self.detect_risk_flags(text),
                        })
            except Exception as e:
                print(f"RSS fetch error for {feed_url}: {e}")
                continue

        return articles

    async def get_company_news(self, symbol: str, company_name: str) -> List[Dict]:
        """Get all news for a company from multiple sources"""
        # Try NewsAPI first
        api_news = await self.fetch_news_api(company_name)

        # Fallback to RSS
        rss_news = self.fetch_rss_news(symbol, company_name)

        # Combine and deduplicate
        all_news = api_news + rss_news
        seen_titles = set()
        unique_news = []

        for article in all_news:
            title_key = article["title"][:50].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(article)

        # Sort by date (newest first)
        unique_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        return unique_news[:20]  # Return top 20

    def calculate_daily_sentiment(self, articles: List[Dict]) -> Dict:
        """Calculate aggregate daily sentiment"""
        if not articles:
            return {"avg_score": 0, "label": "neutral", "article_count": 0}

        scores = [a["sentiment_score"] for a in articles]
        avg_score = sum(scores) / len(scores)

        positive = sum(1 for s in scores if s >= 0.05)
        negative = sum(1 for s in scores if s <= -0.05)
        neutral = len(scores) - positive - negative

        if avg_score >= 0.2:
            label = "very_positive"
        elif avg_score >= 0.05:
            label = "positive"
        elif avg_score <= -0.2:
            label = "very_negative"
        elif avg_score <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "avg_score": round(avg_score, 4),
            "label": label,
            "article_count": len(articles),
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
        }


news_service = NewsSentimentService()
