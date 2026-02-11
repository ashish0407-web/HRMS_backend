from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class EmployeeCreate(BaseModel):
    """Schema for creating a new employee."""
    employee_id: str = Field(..., min_length=1, max_length=50, description="Unique employee ID")
    full_name: str = Field(..., min_length=1, max_length=100, description="Employee full name")
    email: EmailStr = Field(..., description="Employee email address")
    department: str = Field(..., min_length=1, max_length=50, description="Department name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "full_name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering"
            }
        }


class EmployeeResponse(BaseModel):
    """Schema for employee response."""
    employee_id: str
    full_name: str
    email: str
    department: str
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "full_name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class EmployeeList(BaseModel):
    """Schema for list of employees."""
    employees: list[EmployeeResponse]
    total: int