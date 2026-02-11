from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import Request
from typing import Any, Optional


class HRMSException(Exception):
    """Base exception for HRMS application."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundException(HRMSException):
    """Exception raised when a resource is not found."""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND
        )


class DuplicateException(HRMSException):
    """Exception raised when a duplicate resource is detected."""
    
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} with {field} '{value}' already exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ValidationException(HRMSException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class DatabaseException(HRMSException):
    """Exception raised for database errors."""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


async def hrms_exception_handler(request: Request, exc: HRMSException) -> JSONResponse:
    """Global exception handler for HRMS exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "details": exc.details
        }
    )