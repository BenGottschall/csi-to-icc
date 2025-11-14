"""
Main FastAPI application for CSI to ICC Code Mapping.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import codes

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="CSI to ICC Code Mapping API",
    description="API for mapping CSI MasterFormat codes to ICC building code sections",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(codes.router, prefix="/api", tags=["codes"])


@app.get("/")
def read_root():
    """Root endpoint with API information."""
    return {
        "message": "CSI to ICC Code Mapping API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
