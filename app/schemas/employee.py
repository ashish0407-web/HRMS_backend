from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime
from typing import Optional, List
import re


class EmployeeBase(BaseModel):
    """Base schema for employee data."""
    
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the employee"
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address"
    )
    department: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Department name"
    )
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate and clean full name."""
        # Remove extra whitespace
        v = " ".join(v.split())
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Full name can only contain letters, spaces, hyphens, and apostrophes")
        
        # Title case the name
        return v.title()
    
    @field_validator("department")
    @classmethod
    def validate_department(cls, v: str) -> str:
        """Validate and clean department name."""
        # Remove extra whitespace
        v = " ".join(v.split())
        
        # Title case
        return v.title()


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    
    employee_id: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Unique employee identifier"
    )
    
    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        """Validate employee ID format."""
        # Remove whitespace
        v = v.strip()
        
        # Check for valid format (alphanumeric, can include hyphens and underscores)
        if not re.match(r"^[a-zA-Z0-9\-_]+$", v):
            raise ValueError("Employee ID can only contain letters, numbers, hyphens, and underscores")
        
        # Convert to uppercase
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "full_name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering"
            }
        }


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee."""
    
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        description="Full name of the employee"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Valid email address"
    )
    department: Optional[str] = Field(
        None,
        min_length=2,
        max_length=50,
        description="Department name"
    )
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = " ".join(v.split())
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Full name can only contain letters, spaces, hyphens, and apostrophes")
        return v.title()
    
    @field_validator("department")
    @classmethod
    def validate_department(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = " ".join(v.split())
        return v.title()
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Smith",
                "email": "john.smith@company.com",
                "department": "Marketing"
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
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "full_name": "John Doe",
                "email": "john.doe@company.com",
                "department": "Engineering",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class EmployeeListResponse(BaseModel):
    """Schema for list of employees response."""
    
    success: bool = True
    message: str = "Employees retrieved successfully"
    data: List[EmployeeResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Employees retrieved successfully",
                "data": [
                    {
                        "employee_id": "EMP001",
                        "full_name": "John Doe",
                        "email": "john.doe@company.com",
                        "department": "Engineering",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1
            }
        }