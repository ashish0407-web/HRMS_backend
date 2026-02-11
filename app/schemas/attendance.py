from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date
from typing import List, Literal, Optional


class AttendanceBase(BaseModel):
    """Base schema for attendance data."""
    
    status: Literal["Present", "Absent"] = Field(
        ...,
        description="Attendance status"
    )


class AttendanceCreate(AttendanceBase):
    """Schema for marking attendance."""
    
    employee_id: str = Field(
        ...,
        min_length=2,
        max_length=20,
        description="Employee ID"
    )
    date: str = Field(
        ...,
        description="Date in YYYY-MM-DD format"
    )
    
    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: str) -> str:
        """Clean and validate employee ID."""
        return v.strip().upper()
    
    @field_validator("date")
    @classmethod
    def validate_date(cls, v: str) -> str:
        """Validate date format and ensure it's not in the future."""
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        # Check if date is not in the future
        if parsed_date > date.today():
            raise ValueError("Cannot mark attendance for future dates")
        
        return v
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Ensure status is properly capitalized."""
        return v.capitalize()
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "date": "2024-01-15",
                "status": "Present"
            }
        }


class AttendanceResponse(BaseModel):
    """Schema for attendance response."""
    
    employee_id: str
    date: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "date": "2024-01-15",
                "status": "Present",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class AttendanceListResponse(BaseModel):
    """Schema for list of attendance records response."""
    
    success: bool = True
    message: str = "Attendance records retrieved successfully"
    data: List[AttendanceResponse]
    total: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Attendance records retrieved successfully",
                "data": [
                    {
                        "employee_id": "EMP001",
                        "date": "2024-01-15",
                        "status": "Present",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total": 1
            }
        }


class AttendanceSummary(BaseModel):
    """Schema for attendance summary."""
    
    employee_id: str
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "total_days": 20,
                "present_days": 18,
                "absent_days": 2,
                "attendance_percentage": 90.0
            }
        }