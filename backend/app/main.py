"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from app.core.config import settings
from app.api import agents, campaigns, auth, tracking, analytics
# from app.api import automation, reddit, twitter
# from app.services.automation_scheduler import start_scheduler, stop_scheduler

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    print("🚀 Starting GrowthPilot API...")
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(campaigns.router)
app.include_router(tracking.router)
app.include_router(analytics.router)
# app.include_router(automation.router)
# app.include_router(reddit.router)
# app.include_router(twitter.router)

# Mount static files (frontend) - only if frontend directory exists
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to GrowthPilot API",
        "docs": "/docs",
        "health": "/health"
    }
