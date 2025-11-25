"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.services.scheduler import start_scheduler, stop_scheduler
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting application...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="AI-powered stock investment analysis API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Finance-Hub API",
        "version": settings.version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include routers
from app.api import portfolios, holdings, stocks, admin, predictions, scheduler, education, notifications, accuracy, news, backtest
from app.api.v1 import analytics, investment_insights

app.include_router(portfolios.router, prefix="/api/v1/portfolios", tags=["portfolios"])
app.include_router(holdings.router, prefix="/api/v1/holdings", tags=["holdings"])
app.include_router(stocks.router, prefix="/api/v1/stocks", tags=["stocks"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics", "portfolio-2.0"])
app.include_router(scheduler.router, prefix="/api/v1", tags=["scheduler"])
app.include_router(education.router, prefix="/api/v1/education", tags=["education"])
app.include_router(notifications.router, prefix="/api/v1", tags=["notifications"])
app.include_router(accuracy.router, prefix="/api/v1/accuracy", tags=["accuracy"])
app.include_router(news.router, prefix="/api/v1", tags=["news", "sentiment"])
app.include_router(backtest.router, prefix="/api/v1", tags=["backtest"])
app.include_router(investment_insights.router, prefix="/api/v1", tags=["investment-insights"])
