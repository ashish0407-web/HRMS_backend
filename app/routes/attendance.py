from fastapi import APIRouter, status, Query
from typing import Optional
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceListResponse,
    AttendanceSummary
)
from app.services.attendance_service import AttendanceService

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post(
    "",
    response_model=AttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Mark attendance",
    description="Mark attendance for an employee on a specific date."
)
async def mark_attendance(attendance: AttendanceCreate):
    """
    Mark attendance for an employee:
    
    - **employee_id**: ID of the employee
    - **date**: Date in YYYY-MM-DD format (cannot be future date)
    - **status**: Either "Present" or "Absent"
    
    Note: Only one attendance record per employee per date is allowed.
    """
    return await AttendanceService.mark_attendance(attendance)


@router.get(
    "",
    response_model=AttendanceListResponse,
    summary="Get attendance records",
    description="Get attendance records with optional date filter."
)
async def get_attendance(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return")
):
    """
    Retrieve attendance records with optional filtering.
    
    - **date**: Filter by specific date (YYYY-MM-DD)
    - **skip**: Pagination offset
    - **limit**: Maximum number of records
    """
    if date:
        records = await AttendanceService.get_attendance_by_date(date)
    else:
        records = await AttendanceService.get_all_attendance(skip=skip, limit=limit)
    
    return AttendanceListResponse(
        success=True,
        message=f"Retrieved {len(records)} attendance records",
        data=records,
        total=len(records)
    )


@router.get(
    "/employee/{employee_id}",
    response_model=AttendanceListResponse,
    summary="Get employee attendance",
    description="Get all attendance records for a specific employee."
)
async def get_employee_attendance(employee_id: str):
    """
    Get all attendance records for a specific employee.
    
    - **employee_id**: The employee ID
    """
    records = await AttendanceService.get_attendance_by_employee(employee_id)
    
    return AttendanceListResponse(
        success=True,
        message=f"Retrieved {len(records)} attendance records for {employee_id.upper()}",
        data=records,
        total=len(records)
    )


@router.get(
    "/employee/{employee_id}/summary",
    response_model=AttendanceSummary,
    summary="Get attendance summary",
    description="Get attendance summary statistics for an employee."
)
async def get_employee_attendance_summary(employee_id: str):
    """
    Get attendance summary for an employee including:
    
    - Total days
    - Present days
    - Absent days
    - Attendance percentage
    """
    return await AttendanceService.get_employee_attendance_summary(employee_id)


@router.get(
    "/today/summary",
    summary="Get today's summary",
    description="Get today's attendance summary across all employees."
)
async def get_today_summary():
    """
    Get today's attendance summary including:
    
    - Total employees
    - Present count
    - Absent count
    - Not marked count
    """
    return await AttendanceService.get_today_summary()


@router.put(
    "/employee/{employee_id}/date/{date}",
    response_model=AttendanceResponse,
    summary="Update attendance",
    description="Update attendance status for a specific employee and date."
)
async def update_attendance(
    employee_id: str,
    date: str,
    status: str = Query(..., description="New status: 'Present' or 'Absent'")
):
    """
    Update an existing attendance record.
    
    - **employee_id**: The employee ID
    - **date**: The date (YYYY-MM-DD)
    - **status**: New status ('Present' or 'Absent')
    """
    return await AttendanceService.update_attendance(employee_id, date, status)


@router.delete(
    "/employee/{employee_id}/date/{date}",
    status_code=status.HTTP_200_OK,
    summary="Delete attendance record",
    description="Delete a specific attendance record."
)
async def delete_attendance(employee_id: str, date: str):
    """
    Delete an attendance record.
    
    - **employee_id**: The employee ID
    - **date**: The date (YYYY-MM-DD)
    """
    return await AttendanceService.delete_attendance(employee_id, date)