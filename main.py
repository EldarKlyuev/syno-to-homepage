"""
Synology API Proxy - FastAPI application entry point.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from api.v1 import filestation, virtualization
from core.config import settings

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Proxy API for Synology File Station and Virtualization APIs",
    version="1.0.0",
    debug=settings.DEBUG,
)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "HTTPException"
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": type(exc).__name__
            }
        }
    )


# Include API routers
app.include_router(
    filestation.router,
    prefix=settings.API_V1_PREFIX,
)

app.include_router(
    virtualization.router,
    prefix=settings.API_V1_PREFIX,
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_PREFIX,
        "endpoints": {
            "file_station": f"{settings.API_V1_PREFIX}/filestation",
            "virtualization": f"{settings.API_V1_PREFIX}/virtualization"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "synology_url": settings.SYNOLOGY_URL
    }
