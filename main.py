from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
from datetime import datetime

from app.core.config import config
from app.core.security import (
    add_cors_middleware, 
    add_security_headers_middleware, 
    add_request_validation_middleware
)
from app.middleware.security_middleware import security_middleware_function
from app.api.v1.api import api_router
from app.core.database import engine, Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=config.PROJECT_NAME,
    description="AppointmentTech - Multi-tenant Business Management Platform",
    version=config.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add security middleware (applied to ALL requests)
# app.middleware("http")(security_middleware_function)

# Add enhanced security middleware
add_cors_middleware(app)
add_security_headers_middleware(app)
add_request_validation_middleware(app)

# Mount static files for uploads
app.mount("/api/v1/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include API router (preserving existing structure)
app.include_router(api_router, prefix="/api/v1")

# Request/Response middleware for logging with enhanced security
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses with enhanced security tracking"""
    start_time = time.time()
    
    # Get request ID for tracking
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log request with security info
    logger.info(f"Request: {request.method} {request.url} - ID: {request_id} - IP: {request.client.host}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response with security info
    logger.info(f"Response: {response.status_code} - {process_time:.4f}s - ID: {request_id}")
    
    # Add processing time to response headers
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Exception handlers with enhanced security
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with enhanced security logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail} - ID: {request_id} - IP: {request.client.host}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "request_id": request_id
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions with enhanced security logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"Validation Error: {exc.errors()} - ID: {request_id} - IP: {request.client.host}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "message": "Validation error",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "request_id": request_id
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions with enhanced security logging"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"General Exception: {str(exc)} - ID: {request_id} - IP: {request.client.host}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "request_id": request_id
        }
    )

# Startup event with enhanced security
@app.on_event("startup")
async def startup_event():
    """Application startup event with enhanced security logging"""
    logger.info("Starting AppointmentTech API with enhanced security...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
    
    logger.info("AppointmentTech API started successfully with enhanced security features")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down AppointmentTech API...")

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "AppointmentTech API",
        "version": config.VERSION,
        "status": "active",
        "security": "enhanced",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "api": "/api/v1",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": "AppointmentTech API is running with enhanced security",
        "timestamp": datetime.utcnow().isoformat(),
        "version": config.VERSION,
        "security_features": [
            "Enhanced JWT tokens",
            "Rate limiting with IP blocking",
            "Security headers",
            "Request validation",
            "CSRF protection",
            "Device fingerprinting",
            "Suspicious activity detection",
            "Security event logging"
        ]
    }

# Database health check endpoint
@app.get("/health/database", tags=["Health"])
async def database_health_check():
    """
    Database health check endpoint
    """
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        # Test database connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
        
        return {
            "status": "healthy",
            "message": "Database connection successful",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "MySQL",
            "connection": "active"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "Database connection failed",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "MySQL",
            "connection": "failed",
            "error": str(e),
            "solution": "Please ensure MySQL server is running and accessible"
        }

# API information endpoint
@app.get("/api", tags=["API Info"])
async def api_info():
    """
    API information endpoint
    """
    return {
        "name": "AppointmentTech API",
        "version": config.VERSION,
        "description": "Multi-tenant Business Management Platform with Enhanced Security",
        "security_level": "enhanced",
        "endpoints": {
            "users": "/api/v1/users",
            "business": "/api/v1/business",
            "auth": "/api/v1/auth",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "features": [
            "User Management",
            "Business Management", 
            "Location Management",
            "Hostel Management",
            "Hospital Management",
            "Garage Management",
            "Food Catering Management",
            "Audit Logging",
            "Notifications",
            "Payment Transactions",
            "Enhanced Security"
        ],
        "security_features": [
            "JWT Authentication",
            "Rate Limiting",
            "CSRF Protection",
            "Security Headers",
            "Request Validation",
            "Device Fingerprinting",
            "IP Blocking",
            "Audit Logging",
            "Suspicious Activity Detection",
            "Security Event Logging"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )