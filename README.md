HRMS Lite – Backend API

HRMS Lite is a simple HR Management System backend API built using FastAPI and MongoDB.

Features

Employee management (Create, Read, Update, Delete)

Attendance tracking

RESTful API with automatic documentation (Swagger)

Tech Stack

FastAPI – Backend web framework

MongoDB (Atlas / Local) – Database

Python 3.9+

Quick Start
1. Install Dependencies
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate        # Windows
source venv/bin/activate    # Mac/Linux

# Install required packages
pip install -r requirements.txt

2. Environment Setup

Create a .env file in the project root:

MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=hrms_lite

3. Run the Server
uvicorn app.main:app --reload --port 8000


API documentation will be available at:

http://localhost:8000/docs

API Endpoints
Employees

POST /employees – Create a new employee

GET /employees – Get all employees

GET /employees/{id} – Get employee by ID

PUT /employees/{id} – Update employee details

DELETE /employees/{id} – Delete an employee

Attendance

POST /attendance – Mark attendance

GET /attendance – Get all attendance records

GET /attendance/employee/{id} – Get attendance for a specific employee

Example Request

POST /employees

{
  "employee_id": "EMP001",
  "full_name": "John Doe",
  "email": "john@company.com",
  "department": "Engineering"
}

Project Structure
app/
├── main.py          # Application entry point
├── config.py        # Configuration settings
├── database.py      # Database connection
├── schemas/         # Request & response validation
├── services/        # Business logic
├── routes/          # API routes
└── exceptions/      # Custom error handling

License

MIT
