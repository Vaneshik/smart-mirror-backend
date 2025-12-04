from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.api.endpoints import llm, music

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title=settings.app_name, debug=settings.debug, docs_url="/docs", redoc_url="/redoc")

# Configure CORS for ROS client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(llm.router, prefix="/api")
app.include_router(music.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SmartMirror Backend API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("=" * 50)
    logger.info("SmartMirror Backend starting...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("SmartMirror Backend shutting down...")
