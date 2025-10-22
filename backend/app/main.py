"""Main FastAPI application."""
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from app.core.config import settings
from app.core.database import engine, Base
from app.api import agents, campaigns, auth, tracking, analytics, automation
# from app.api import reddit, twitter
# from app.services.automation_scheduler import start_scheduler, stop_scheduler

# Load environment variables from .env file
load_dotenv()

# Import all models to ensure they are registered with Base
from app.models.campaign import Campaign
from app.models.automation_job import AutomationJob
from app.models.user import User
from app.models.campaign_interaction import CampaignInteraction
from app.models.link_click import LinkClick


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting GrowthPilot API...")

    # Create database tables
    print("📊 Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

    # start_scheduler()
    yield
    # Shutdown
    print("🛑 Shutting down GrowthPilot API...")
    # stop_scheduler()


# Create FastAPI app
app = FastAPI(
    title="GrowthPilot API",
    description="AI-Powered SaaS Outreach Automation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
# Allow all origins for development, same origin in production serves both
allowed_origins = ["*"]  # Simplified since frontend and backend are served together
print(f"🌐 CORS: Allowing all origins (frontend served by backend)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints (must be defined BEFORE static files)
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


# Include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(campaigns.router)
app.include_router(tracking.router)
app.include_router(analytics.router)
app.include_router(automation.router)
# app.include_router(reddit.router)
# app.include_router(twitter.router)

# Mount static files (frontend) at root - must be LAST
# This serves frontend at root, but API routes take precedence
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    print(f"✅ Frontend mounted at root from: {frontend_path}")
