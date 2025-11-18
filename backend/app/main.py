"""
Career Fair Copilot - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import get_settings
from .database import init_db, engine, Base
from .routes import companies, booths, routing, users

# Import models to ensure they're registered with SQLAlchemy
from .models import company, booth, user, itinerary

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="API for Career Fair Copilot - Your intelligent career fair companion",
    debug=settings.debug,
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
app.include_router(companies.router, prefix=f"{settings.api_v1_prefix}/companies", tags=["companies"])
app.include_router(booths.router, prefix=f"{settings.api_v1_prefix}/booths", tags=["booths"])
app.include_router(routing.router, prefix=f"{settings.api_v1_prefix}/routing", tags=["routing"])
app.include_router(users.router, prefix=f"{settings.api_v1_prefix}/users", tags=["users"])


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Career Fair Copilot API",
        "version": settings.version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
