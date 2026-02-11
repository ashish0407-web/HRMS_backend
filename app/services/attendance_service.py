from datetime import datetime, date
from typing import List, Optional
from app.database import get_attendance_collection, get_employees_collection
from app.schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceSummary
from app.exceptions import NotFoundException, DuplicateException, DatabaseException, ValidationException
import logging

logger = logging.getLogger(__name__)


class AttendanceService:
    """Service class for attendance operations."""
    
    @staticmethod
    async def mark_attendance(attendance_data: AttendanceCreate) -> AttendanceResponse:
        """
        Mark attendance for an employee.
        
        Args:
            attendance_data: Attendance creation data
            
        Returns:
            Created attendance response
            
        Raises:
            NotFoundException: If employee not found
            DuplicateException: If attendance already marked for the date
        """
        employees_collection = get_employees_collection()
        attendance_collection = get_attendance_collection()
        
        employee_id = attendance_data.employee_id.upper()
        
        try:
            # Check if employee exists
            employee = await employees_collection.find_one({"employee_id": employee_id})
            if not employee:
                raise NotFoundException("Employee", employee_id)
            
            # Check for duplicate attendance
            existing = await attendance_collection.find_one({
                "employee_id": employee_id,
                "date": attendance_data.date
            })
            
            if existing:
                raise DuplicateException(
                    "Attendance record",
                    f"employee_id and date",
                    f"{employee_id} on {attendance_data.date}"
                )
            
            # Create attendance document
            attendance_doc = {
                "employee_id": employee_id,
                "date": attendance_data.date,
                "status": attendance_data.status,
                "created_at": datetime.utcnow()
            }
            
            # Insert document
            result = await attendance_collection.insert_one(attendance_doc)
            
            if not result.inserted_id:
                raise DatabaseException("Failed to mark attendance")
            
            logger.info(f"Attendance marked: {employee_id} on {attendance_data.date} - {attendance_data.status}")
            
            return AttendanceResponse(
                employee_id=attendance_doc["employee_id"],
                date=attendance_doc["date"],
                status=attendance_doc["status"],
                created_at=attendance_doc["created_at"]
            )
            
        except (NotFoundException, DuplicateException, DatabaseException):
            raise
        except Exception as e:
            logger.error(f"Error marking attendance: {e}")
            raise DatabaseException(f"Failed to mark attendance: {str(e)}")
    
    @staticmethod
    async def get_attendance_by_employee(employee_id: str) -> List[AttendanceResponse]:
        """
        Get all attendance records for an employee.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            List of attendance records
            
        Raises:
            NotFoundException: If employee not found
        """
        employees_collection = get_employees_collection()
        attendance_collection = get_attendance_collection()
        
        employee_id = employee_id.upper()
        
        try:
            # Check if employee exists
            employee = await employees_collection.find_one({"employee_id": employee_id})
            if not employee:
                raise NotFoundException("Employee", employee_id)
            
            # Fetch attendance records
            records = []
            cursor = attendance_collection.find({"employee_id": employee_id}).sort("date", -1)
            
            async for doc in cursor:
                records.append(AttendanceResponse(
                    employee_id=doc["employee_id"],
                    date=doc["date"],
                    status=doc["status"],
                    created_at=doc["created_at"]
                ))
            
            logger.info(f"Retrieved {len(records)} attendance records for {employee_id}")
            return records
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching attendance for {employee_id}: {e}")
            raise DatabaseException(f"Failed to fetch attendance: {str(e)}")
    
    @staticmethod
    async def get_attendance_by_date(target_date: str) -> List[AttendanceResponse]:
        """
        Get all attendance records for a specific date.
        
        Args:
            target_date: Date in YYYY-MM-DD format
            
        Returns:
            List of attendance records
        """
        attendance_collection = get_attendance_collection()
        
        try:
            # Validate date format
            try:
                datetime.strptime(target_date, "%Y-%m-%d")
            except ValueError:
                raise ValidationException("Date must be in YYYY-MM-DD format")
            
            # Fetch attendance records
            records = []
            cursor = attendance_collection.find({"date": target_date}).sort("employee_id", 1)
            
            async for doc in cursor:
                records.append(AttendanceResponse(
                    employee_id=doc["employee_id"],
                    date=doc["date"],
                    status=doc["status"],
                    created_at=doc["created_at"]
                ))
            
            logger.info(f"Retrieved {len(records)} attendance records for date {target_date}")
            return records
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Error fetching attendance for date {target_date}: {e}")
            raise DatabaseException(f"Failed to fetch attendance: {str(e)}")
    
    @staticmethod
    async def get_all_attendance(
        skip: int = 0,
        limit: int = 100
    ) -> List[AttendanceResponse]:
        """
        Get all attendance records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of attendance records
        """
        attendance_collection = get_attendance_collection()
        
        try:
            records = []
            cursor = attendance_collection.find({}).sort("date", -1).skip(skip).limit(limit)
            
            async for doc in cursor:
                records.append(AttendanceResponse(
                    employee_id=doc["employee_id"],
                    date=doc["date"],
                    status=doc["status"],
                    created_at=doc["created_at"]
                ))
            
            return records
            
        except Exception as e:
            logger.error(f"Error fetching all attendance: {e}")
            raise DatabaseException(f"Failed to fetch attendance: {str(e)}")
    
    @staticmethod
    async def get_employee_attendance_summary(employee_id: str) -> AttendanceSummary:
        """
        Get attendance summary for an employee.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Attendance summary
            
        Raises:
            NotFoundException: If employee not found
        """
        employees_collection = get_employees_collection()
        attendance_collection = get_attendance_collection()
        
        employee_id = employee_id.upper()
        
        try:
            # Check if employee exists
            employee = await employees_collection.find_one({"employee_id": employee_id})
            if not employee:
                raise NotFoundException("Employee", employee_id)
            
            # Count attendance records
            total_days = await attendance_collection.count_documents({"employee_id": employee_id})
            present_days = await attendance_collection.count_documents({
                "employee_id": employee_id,
                "status": "Present"
            })
            absent_days = total_days - present_days
            
            # Calculate percentage
            attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0.0
            
            return AttendanceSummary(
                employee_id=employee_id,
                total_days=total_days,
                present_days=present_days,
                absent_days=absent_days,
                attendance_percentage=round(attendance_percentage, 2)
            )
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching attendance summary for {employee_id}: {e}")
            raise DatabaseException(f"Failed to fetch attendance summary: {str(e)}")
    
    @staticmethod
    async def get_today_summary() -> dict:
        """
        Get today's attendance summary.
        
        Returns:
            Dictionary with today's attendance stats
        """
        employees_collection = get_employees_collection()
        attendance_collection = get_attendance_collection()
        
        today = date.today().strftime("%Y-%m-%d")
        
        try:
            # Get total employees
            total_employees = await employees_collection.count_documents({})
            
            # Get today's attendance counts
            present_today = await attendance_collection.count_documents({
                "date": today,
                "status": "Present"
            })
            
            absent_today = await attendance_collection.count_documents({
                "date": today,
                "status": "Absent"
            })
            
            not_marked = total_employees - present_today - absent_today
            
            return {
                "date": today,
                "total_employees": total_employees,
                "present": present_today,
                "absent": absent_today,
                "not_marked": not_marked
            }
            
        except Exception as e:
            logger.error(f"Error fetching today's summary: {e}")
            raise DatabaseException(f"Failed to fetch summary: {str(e)}")
    
    @staticmethod
    async def update_attendance(
        employee_id: str,
        target_date: str,
        new_status: str
    ) -> AttendanceResponse:
        """
        Update attendance status for a specific date.
        
        Args:
            employee_id: Employee ID
            target_date: Date in YYYY-MM-DD format
            new_status: New status ("Present" or "Absent")
            
        Returns:
            Updated attendance response
            
        Raises:
            NotFoundException: If attendance record not found
        """
        attendance_collection = get_attendance_collection()
        employee_id = employee_id.upper()
        
        try:
            # Validate status
            if new_status not in ["Present", "Absent"]:
                raise ValidationException("Status must be 'Present' or 'Absent'")
            
            # Check if attendance record exists
            existing = await attendance_collection.find_one({
                "employee_id": employee_id,
                "date": target_date
            })
            
            if not existing:
                raise NotFoundException(
                    "Attendance record",
                    f"{employee_id} on {target_date}"
                )
            
            # Update the record
            await attendance_collection.update_one(
                {"employee_id": employee_id, "date": target_date},
                {"$set": {"status": new_status}}
            )
            
            # Fetch updated record
            updated = await attendance_collection.find_one({
                "employee_id": employee_id,
                "date": target_date
            })
            
            logger.info(f"Attendance updated: {employee_id} on {target_date} - {new_status}")
            
            return AttendanceResponse(
                employee_id=updated["employee_id"],
                date=updated["date"],
                status=updated["status"],
                created_at=updated["created_at"]
            )
            
        except (NotFoundException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error updating attendance: {e}")
            raise DatabaseException(f"Failed to update attendance: {str(e)}")
    
    @staticmethod
    async def delete_attendance(employee_id: str, target_date: str) -> dict:
        """
        Delete an attendance record.
        
        Args:
            employee_id: Employee ID
            target_date: Date in YYYY-MM-DD format
            
        Returns:
            Deletion result
            
        Raises:
            NotFoundException: If attendance record not found
        """
        attendance_collection = get_attendance_collection()
        employee_id = employee_id.upper()
        
        try:
            # Check if record exists
            existing = await attendance_collection.find_one({
                "employee_id": employee_id,
                "date": target_date
            })
            
            if not existing:
                raise NotFoundException(
                    "Attendance record",
                    f"{employee_id} on {target_date}"
                )
            
            # Delete the record
            await attendance_collection.delete_one({
                "employee_id": employee_id,
                "date": target_date
            })
            
            logger.info(f"Attendance deleted: {employee_id} on {target_date}")
            
            return {
                "success": True,
                "message": f"Attendance record deleted successfully",
                "employee_id": employee_id,
                "date": target_date
            }
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting attendance: {e}")
            raise DatabaseException(f"Failed to delete attendance: {str(e)}")