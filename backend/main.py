"""Main FastAPI application for Indian Stock Tracker"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time

from database import init_db
from routers import dashboard, watchlist, alerts, reports, settings

# Initialize database on startup
init_db()

app = FastAPI(
    title="Indian Stock Tracker",
    description="AI-powered stock screening, sentiment analysis, and alert system for Indian markets",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Include routers
app.include_router(dashboard.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)
app.include_router(reports.router)
app.include_router(settings.router)


@app.get("/")
def root():
    return {
        "app": "Indian Stock Tracker",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "dashboard": "/api/dashboard/full",
            "watchlist": "/api/watchlist/stocks",
            "alerts": "/api/alerts/",
            "reports": "/api/reports/weekly",
            "settings": "/api/settings/",
        }
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
