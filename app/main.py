from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import connect_to_database, close_database_connection
from app.routes import employees_router, attendance_router
from app.exceptions import HRMSException, hrms_exception_handler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    # Startup
    logger.info("Starting HRMS Lite API...")
    await connect_to_database()
    logger.info("Application started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HRMS Lite API...")
    await close_database_connection()
    logger.info("Application shut down successfully!")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
## HRMS Lite API

A lightweight HR Management System for managing employees and tracking attendance.

### Features:
- **Employee Management**: Add, view, update, and delete employees
- **Attendance Tracking**: Mark and track daily attendance
- **Attendance Reports**: View attendance summaries and statistics

### API Sections:
- **Employees**: Manage employee records
- **Attendance**: Track and manage attendance
    """,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handler
app.add_exception_handler(HRMSException, hrms_exception_handler)


# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "details": str(exc) if settings.debug else None
        }
    )


# Include routers
app.include_router(employees_router)
app.include_router(attendance_router)


# Health check endpoints
@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API information."""
    return {
        "success": True,
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/api/info", tags=["Health"])
async def api_info():
    """Get API information and available endpoints."""
    return {
        "success": True,
        "api_name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "employees": {
                "create": "POST /employees",
                "list": "GET /employees",
                "get": "GET /employees/{employee_id}",
                "update": "PUT /employees/{employee_id}",
                "delete": "DELETE /employees/{employee_id}"
            },
            "attendance": {
                "mark": "POST /attendance",
                "list": "GET /attendance",
                "by_employee": "GET /attendance/employee/{employee_id}",
                "summary": "GET /attendance/employee/{employee_id}/summary",
                "today": "GET /attendance/today/summary",
                "update": "PUT /attendance/employee/{employee_id}/date/{date}",
                "delete": "DELETE /attendance/employee/{employee_id}/date/{date}"
            }
        }
    }