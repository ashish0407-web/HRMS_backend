from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime, date


class AttendanceCreate(BaseModel):
    """Schema for marking attendance."""
    employee_id: str = Field(..., min_length=1, description="Employee ID")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    status: Literal["Present", "Absent"] = Field(..., description="Attendance status")
    
    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    
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
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "date": "2024-01-15",
                "status": "Present",
                "created_at": "2024-01-15T10:30:00"
            }
        }


class AttendanceList(BaseModel):
    """Schema for list of attendance records."""
    attendance_records: list[AttendanceResponse]
    total: int