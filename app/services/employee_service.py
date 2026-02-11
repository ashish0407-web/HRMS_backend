from datetime import datetime
from typing import List, Optional
from app.database import get_employees_collection, get_attendance_collection
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.exceptions import NotFoundException, DuplicateException, DatabaseException
import logging

logger = logging.getLogger(__name__)


class EmployeeService:
    """Service class for employee operations."""
    
    @staticmethod
    async def create_employee(employee_data: EmployeeCreate) -> EmployeeResponse:
        """
        Create a new employee.
        
        Args:
            employee_data: Employee creation data
            
        Returns:
            Created employee response
            
        Raises:
            DuplicateException: If employee_id or email already exists
            DatabaseException: If database operation fails
        """
        collection = get_employees_collection()
        
        try:
            # Check for duplicate employee_id
            existing_id = await collection.find_one({"employee_id": employee_data.employee_id})
            if existing_id:
                raise DuplicateException("Employee", "employee_id", employee_data.employee_id)
            
            # Check for duplicate email
            existing_email = await collection.find_one({"email": employee_data.email.lower()})
            if existing_email:
                raise DuplicateException("Employee", "email", employee_data.email)
            
            # Prepare document
            employee_doc = {
                "employee_id": employee_data.employee_id,
                "full_name": employee_data.full_name,
                "email": employee_data.email.lower(),  # Store email in lowercase
                "department": employee_data.department,
                "created_at": datetime.utcnow()
            }
            
            # Insert document
            result = await collection.insert_one(employee_doc)
            
            if not result.inserted_id:
                raise DatabaseException("Failed to create employee")
            
            logger.info(f"Employee created successfully: {employee_data.employee_id}")
            
            return EmployeeResponse(
                employee_id=employee_doc["employee_id"],
                full_name=employee_doc["full_name"],
                email=employee_doc["email"],
                department=employee_doc["department"],
                created_at=employee_doc["created_at"]
            )
            
        except (DuplicateException, DatabaseException):
            raise
        except Exception as e:
            logger.error(f"Error creating employee: {e}")
            raise DatabaseException(f"Failed to create employee: {str(e)}")
    
    @staticmethod
    async def get_all_employees() -> List[EmployeeResponse]:
        """
        Get all employees.
        
        Returns:
            List of employee responses
        """
        collection = get_employees_collection()
        
        try:
            employees = []
            cursor = collection.find({}).sort("created_at", -1)
            
            async for doc in cursor:
                employees.append(EmployeeResponse(
                    employee_id=doc["employee_id"],
                    full_name=doc["full_name"],
                    email=doc["email"],
                    department=doc["department"],
                    created_at=doc["created_at"]
                ))
            
            logger.info(f"Retrieved {len(employees)} employees")
            return employees
            
        except Exception as e:
            logger.error(f"Error fetching employees: {e}")
            raise DatabaseException(f"Failed to fetch employees: {str(e)}")
    
    @staticmethod
    async def get_employee_by_id(employee_id: str) -> EmployeeResponse:
        """
        Get employee by ID.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Employee response
            
        Raises:
            NotFoundException: If employee not found
        """
        collection = get_employees_collection()
        
        try:
            employee = await collection.find_one({"employee_id": employee_id.upper()})
            
            if not employee:
                raise NotFoundException("Employee", employee_id)
            
            return EmployeeResponse(
                employee_id=employee["employee_id"],
                full_name=employee["full_name"],
                email=employee["email"],
                department=employee["department"],
                created_at=employee["created_at"]
            )
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error fetching employee {employee_id}: {e}")
            raise DatabaseException(f"Failed to fetch employee: {str(e)}")
    
    @staticmethod
    async def update_employee(employee_id: str, update_data: EmployeeUpdate) -> EmployeeResponse:
        """
        Update an employee.
        
        Args:
            employee_id: Employee ID
            update_data: Update data
            
        Returns:
            Updated employee response
            
        Raises:
            NotFoundException: If employee not found
            DuplicateException: If new email already exists
        """
        collection = get_employees_collection()
        employee_id = employee_id.upper()
        
        try:
            # Check if employee exists
            existing = await collection.find_one({"employee_id": employee_id})
            if not existing:
                raise NotFoundException("Employee", employee_id)
            
            # Build update document
            update_doc = {}
            
            if update_data.full_name is not None:
                update_doc["full_name"] = update_data.full_name
            
            if update_data.email is not None:
                # Check for duplicate email
                email_lower = update_data.email.lower()
                existing_email = await collection.find_one({
                    "email": email_lower,
                    "employee_id": {"$ne": employee_id}
                })
                if existing_email:
                    raise DuplicateException("Employee", "email", update_data.email)
                update_doc["email"] = email_lower
            
            if update_data.department is not None:
                update_doc["department"] = update_data.department
            
            if not update_doc:
                # No updates provided, return existing
                return EmployeeResponse(
                    employee_id=existing["employee_id"],
                    full_name=existing["full_name"],
                    email=existing["email"],
                    department=existing["department"],
                    created_at=existing["created_at"]
                )
            
            # Update document
            await collection.update_one(
                {"employee_id": employee_id},
                {"$set": update_doc}
            )
            
            # Fetch and return updated document
            updated = await collection.find_one({"employee_id": employee_id})
            
            logger.info(f"Employee updated successfully: {employee_id}")
            
            return EmployeeResponse(
                employee_id=updated["employee_id"],
                full_name=updated["full_name"],
                email=updated["email"],
                department=updated["department"],
                created_at=updated["created_at"]
            )
            
        except (NotFoundException, DuplicateException):
            raise
        except Exception as e:
            logger.error(f"Error updating employee {employee_id}: {e}")
            raise DatabaseException(f"Failed to update employee: {str(e)}")
    
    @staticmethod
    async def delete_employee(employee_id: str) -> dict:
        """
        Delete an employee and their attendance records.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            Deletion result
            
        Raises:
            NotFoundException: If employee not found
        """
        employees_collection = get_employees_collection()
        attendance_collection = get_attendance_collection()
        employee_id = employee_id.upper()
        
        try:
            # Check if employee exists
            existing = await employees_collection.find_one({"employee_id": employee_id})
            if not existing:
                raise NotFoundException("Employee", employee_id)
            
            # Delete attendance records first
            attendance_result = await attendance_collection.delete_many({"employee_id": employee_id})
            
            # Delete employee
            await employees_collection.delete_one({"employee_id": employee_id})
            
            logger.info(f"Employee deleted: {employee_id}, attendance records deleted: {attendance_result.deleted_count}")
            
            return {
                "success": True,
                "message": f"Employee '{employee_id}' deleted successfully",
                "employee_id": employee_id,
                "attendance_records_deleted": attendance_result.deleted_count
            }
            
        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error deleting employee {employee_id}: {e}")
            raise DatabaseException(f"Failed to delete employee: {str(e)}")
    
    @staticmethod
    async def check_employee_exists(employee_id: str) -> bool:
        """
        Check if an employee exists.
        
        Args:
            employee_id: Employee ID
            
        Returns:
            True if exists, False otherwise
        """
        collection = get_employees_collection()
        
        try:
            employee = await collection.find_one({"employee_id": employee_id.upper()})
            return employee is not None
        except Exception as e:
            logger.error(f"Error checking employee existence: {e}")
            return False
    
    @staticmethod
    async def get_employees_by_department(department: str) -> List[EmployeeResponse]:
        """
        Get employees by department.
        
        Args:
            department: Department name
            
        Returns:
            List of employees in the department
        """
        collection = get_employees_collection()
        
        try:
            employees = []
            cursor = collection.find({"department": department.title()}).sort("full_name", 1)
            
            async for doc in cursor:
                employees.append(EmployeeResponse(
                    employee_id=doc["employee_id"],
                    full_name=doc["full_name"],
                    email=doc["email"],
                    department=doc["department"],
                    created_at=doc["created_at"]
                ))
            
            return employees
            
        except Exception as e:
            logger.error(f"Error fetching employees by department: {e}")
            raise DatabaseException(f"Failed to fetch employees: {str(e)}")