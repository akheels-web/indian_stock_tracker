# 🇮🇳 Indian Stock Tracker

A complete, self-hosted platform for tracking Indian stock market investments with AI-powered screening, daily news sentiment analysis, and intelligent exit alerts.

## ✨ Features

### 1. Weekly Stock Screening
- Automatically screens Nifty 50 + custom universe every Sunday
- Scores stocks on **Fundamental** (P/E, ROE, Debt/Equity, EPS growth) and **Technical** (RSI, MACD, Trend, MAs) metrics
- Ranks stocks with overall score (0-100) and recommendation (BUY / WATCH / HOLD / AVOID)
- Identifies companies with good investment potential

### 2. Continuous Tracking
- Tracks all stocks from the moment you add them
- Maintains price history, high/low tracking, and performance metrics
- Portfolio view showing entry price, current price, stop-loss, and target
- Status management: Watching → Holding → Exited

### 3. Daily News Sentiment Scoring
- Scans news from MoneyControl, Economic Times, Business Standard, LiveMint daily at 8 AM IST
- Uses VADER sentiment analysis to score each article (-1 to +1)
- Detects risk flags: regulatory, legal, fraud, earnings miss, management changes
- Aggregate daily sentiment score per stock
- Stores all articles with summaries and key points

### 4. Intelligent Exit Alerts
Monitors your holdings and alerts you when:
- **Stop Loss Hit**: Price drops 8% below entry (configurable)
- **Target Reached**: Price hits 20% above entry (configurable)
- **Sentiment Crash**: News sentiment drops below -0.6
- **Fundamental Deterioration**: P/E > 50, Debt/Equity > 2, ROE < 5%, EPS growth < -20%
- **Critical News Flags**: Regulatory issues, lawsuits, fraud, bankruptcy mentions
- **High Volatility**: Annualized volatility > 50%

Alert severity levels: **Critical** (exit now), **High** (strong consider exit), **Medium** (monitor), **Low** (info)

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   React UI      │────▶│  FastAPI Backend  │────▶│   PostgreSQL    │
│   (Port 3000)   │     │   (Port 8000)     │     │   (Port 5432)   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  APScheduler   │
                        │  (Tasks)         │
                        └──────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ Weekly      │    │ Daily News  │    │ Exit        │
    │ Screener    │    │ Scanner     │    │ Monitor     │
    │ (Sun 6PM)   │    │ (Daily 8AM) │    │ (Hourly)    │
    └─────────────┘    └─────────────┘    └─────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ Yahoo       │    │ NewsAPI +   │    │ Yahoo       │
    │ Finance     │    │ RSS Feeds   │    │ Finance     │
    │ (Prices)    │    │ (Articles)  │    │ (Prices)    │
    └─────────────┘    └─────────────┘    └─────────────┘
```

## 🚀 Quick Start (Proxmox)

### Prerequisites
- Proxmox VE with an LXC container or VM
- Docker & Docker Compose installed
- At least 2GB RAM, 10GB disk

### 1. Clone & Configure
```bash
git clone <repo-url> indian-stock-tracker
cd indian-stock-tracker
cp .env.example .env
# Edit .env with your API keys
```

### 2. Get Free API Keys
| Service | URL | Free Tier |
|---------|-----|-----------|
| NewsAPI | https://newsapi.org | 100 requests/day |
| Groq | https://console.groq.com | Generous free tier |
| Alpha Vantage | https://www.alphavantage.co | 25 requests/day |

### 3. Deploy
```bash
docker-compose up -d
```

### 4. Access
- **Dashboard**: http://your-proxmox-ip:3000
- **API Docs**: http://your-proxmox-ip:8000/docs
- **Database**: Port 5432 (internal)

### 5. First Run
```bash
# Trigger weekly screening manually
docker exec stock_tracker_scheduler python -c "from tasks.weekly_screener_task import run_weekly_screening; run_weekly_screening()"

# Trigger daily news scan
docker exec stock_tracker_scheduler python -c "import asyncio; from tasks.daily_news_scanner import run_daily_news_scan; asyncio.run(run_daily_news_scan())"
```

## 📊 Dashboard Pages

| Page | Description |
|------|-------------|
| **Dashboard** | Overview stats, weekly top picks, recent alerts, sentiment trend chart |
| **Watchlist** | All tracked stocks with scores, filters by status, add new stocks |
| **Stock Detail** | Individual stock view: scores, news articles, alerts, fundamentals |
| **Alerts** | All alerts with severity filtering, acknowledge/resolve actions |
| **Reports** | Weekly screening history, portfolio P&L tracking |
| **Settings** | Screening criteria, alert thresholds, news sources |

## 🔔 Telegram Alerts Setup (Optional)

1. Message [@BotFather](https://t.me/botfather) on Telegram, create a bot, get token
2. Message [@userinfobot](https://t.me/userinfobot) to get your chat ID
3. Add to `.env`:
```
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```
4. Restart: `docker-compose restart backend scheduler`

You'll receive instant alerts for:
- Critical exit signals
- High-severity risk warnings
- Target reached notifications

## ⚙️ Customization

### Adjust Screening Criteria
Edit `backend/config.py`:
```python
MIN_ROE = 15.0           # Minimum Return on Equity
MAX_DEBT_EQUITY = 0.5    # Maximum Debt/Equity ratio
MIN_EPS_GROWTH = 10.0    # Minimum EPS growth %
MAX_PE = 30.0            # Maximum P/E ratio
```

### Adjust Alert Thresholds
```python
SENTIMENT_EXIT_THRESHOLD = -0.6   # Exit if sentiment below this
STOP_LOSS_PCT = 8.0               # 8% stop loss
TARGET_GAIN_PCT = 20.0            # 20% profit target
```

### Add Custom Stocks
Use the "Add Stock" button in the Watchlist page, or edit `DEFAULT_UNIVERSE` in `config.py`.

## 🗓️ Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| Weekly Screening | Every Sunday 6:00 PM IST | Screens full universe, updates scores |
| Daily News Scan | Every day 8:00 AM IST | Fetches news, calculates sentiment, checks alerts |
| Exit Monitor | Every 30 min (market hours) | Monitors holdings for exit signals |
| Exit Monitor | 3:30 PM IST | Final check at market close |

## 🛡️ Data Privacy

- **Fully self-hosted** — all data stays on your Proxmox
- No data sent to external services except:
  - Yahoo Finance (stock prices)
  - NewsAPI (news headlines)
  - Your Telegram bot (alerts only, if configured)
- Database runs locally in Docker
- No analytics, no tracking, no cloud dependencies

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/full` | GET | Complete dashboard data |
| `/api/watchlist/stocks` | GET | List all stocks |
| `/api/watchlist/stocks` | POST | Add new stock |
| `/api/watchlist/stocks/{id}` | GET | Stock detail |
| `/api/watchlist/stocks/{id}/buy` | POST | Mark as bought |
| `/api/alerts/` | GET | List alerts |
| `/api/alerts/stats` | GET | Alert statistics |
| `/api/reports/weekly` | GET | Weekly reports |
| `/api/reports/performance` | GET | Portfolio performance |

Full API docs at `/docs` (Swagger UI).

## 🔧 Troubleshooting

**"No data available" for a stock**
- Check symbol format: must be `.NS` suffix (e.g., `RELIANCE.NS`)
- Yahoo Finance may not have data for delisted/suspended stocks

**NewsAPI rate limit exceeded**
- Free tier is 100 requests/day
- The tool falls back to RSS feeds automatically

**High memory usage**
- The scheduler loads historical data for screening
- Consider reducing `DEFAULT_UNIVERSE` size

**Database connection errors**
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check `.env` DB credentials match docker-compose

## 📜 License

MIT License — use freely, modify as needed.

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is **NOT financial advice**.
- All recommendations are algorithmic and should be verified
- Past performance does not guarantee future results
- Always do your own research before trading
- The developers are not responsible for any trading losses

---

**Built for Indian investors who want data-driven decisions.** 🇮🇳
