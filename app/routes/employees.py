from fastapi import APIRouter, status, Query
from typing import Optional
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeListResponse
)
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post(
    "",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new employee",
    description="Add a new employee to the system with unique employee ID and email."
)
async def create_employee(employee: EmployeeCreate):
    """
    Create a new employee with the following fields:
    
    - **employee_id**: Unique identifier (e.g., EMP001)
    - **full_name**: Full name of the employee
    - **email**: Valid, unique email address
    - **department**: Department name
    """
    return await EmployeeService.create_employee(employee)


@router.get(
    "",
    response_model=EmployeeListResponse,
    summary="Get all employees",
    description="Retrieve a list of all employees in the system."
)
async def get_all_employees(
    department: Optional[str] = Query(None, description="Filter by department")
):
    """
    Retrieve all employees. Optionally filter by department.
    """
    if department:
        employees = await EmployeeService.get_employees_by_department(department)
    else:
        employees = await EmployeeService.get_all_employees()
    
    return EmployeeListResponse(
        success=True,
        message=f"Retrieved {len(employees)} employees",
        data=employees,
        total=len(employees)
    )


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get employee by ID",
    description="Retrieve a specific employee by their employee ID."
)
async def get_employee(employee_id: str):
    """
    Get a specific employee by their ID.
    
    - **employee_id**: The unique employee identifier
    """
    return await EmployeeService.get_employee_by_id(employee_id)


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update an employee",
    description="Update employee information. All fields are optional."
)
async def update_employee(employee_id: str, update_data: EmployeeUpdate):
    """
    Update an employee's information.
    
    - **employee_id**: The employee to update
    - **update_data**: Fields to update (all optional)
    """
    return await EmployeeService.update_employee(employee_id, update_data)


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete an employee",
    description="Delete an employee and all their attendance records."
)
async def delete_employee(employee_id: str):
    """
    Delete an employee and their associated attendance records.
    
    - **employee_id**: The employee to delete
    """
    return await EmployeeService.delete_employee(employee_id)