"""APScheduler task runner"""
import sys
import os

# Add /app to Python path so imports work when running from tasks/ directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks.daily_news_scanner import run_daily_news_scan
from tasks.weekly_screener_task import run_weekly_screening
from tasks.exit_monitor import run_exit_monitor


def run_async_task(coro):
    """Helper to run async tasks in sync scheduler"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)


def main():
    scheduler = BlockingScheduler(timezone="Asia/Kolkata")

    # Weekly screening: Every Sunday at 6:00 PM IST
    scheduler.add_job(
        run_weekly_screening,
        CronTrigger(day_of_week="sun", hour=18, minute=0),
        id="weekly_screening",
        name="Weekly Stock Screening",
        replace_existing=True,
    )

    # Daily news scan: Every day at 8:00 AM IST
    scheduler.add_job(
        lambda: run_async_task(run_daily_news_scan()),
        CronTrigger(hour=8, minute=0),
        id="daily_news_scan",
        name="Daily News & Sentiment Scan",
        replace_existing=True,
    )

    # Exit monitor: Every hour during market hours (9:15 AM - 3:30 PM IST)
    scheduler.add_job(
        run_exit_monitor,
        CronTrigger(hour="9-15", minute="0,30"),
        id="exit_monitor",
        name="Exit Signal Monitor",
        replace_existing=True,
    )

    # Also run exit monitor at market close (3:30 PM)
    scheduler.add_job(
        run_exit_monitor,
        CronTrigger(hour=15, minute=30),
        id="exit_monitor_close",
        name="Exit Monitor - Market Close",
        replace_existing=True,
    )

    print("=" * 60)
    print("  Indian Stock Tracker - Scheduler Started")
    print("=" * 60)
    print("  Weekly Screening: Every Sunday 6:00 PM IST")
    print("  Daily News Scan:  Every day 8:00 AM IST")
    print("  Exit Monitor:     Every 30 min (9:15 AM - 3:30 PM IST)")
    print("=" * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler stopped")


if __name__ == "__main__":
    main()
