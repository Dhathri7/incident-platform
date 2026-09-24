import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import init_db, get_settings
from app.routers import auth, incidents, audit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan event handler."""
    # Startup
    logger.info("Starting up application...")
    await init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="AI Incident Management Platform",
    description="An AI-powered incident management system with RAG capabilities",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "version": "1.0.0",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to AI Incident Management Platform",
        "docs": "/docs",
        "openapi_schema": "/openapi.json",
    }


# TODO: Import and include routers in Phase 2

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
app.include_router(audit.router, prefix="/audit-logs", tags=["Audit"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
    )