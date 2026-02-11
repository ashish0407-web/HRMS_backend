# HRMS Lite - Backend API 

live link - [LIVE DEMO](https://hrms-lite-api-556b.onrender.com)

A simple HR Management System API built with FastAPI and MongoDB.

## Features

- Employee Management (Add, View, Update, Delete)
- Attendance Tracking
- REST API with automatic documentation

## Tech Stack

- **FastAPI** - Web framework
- **MongoDB Atlas** - Database
- **Python 3.9+**

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install packages
pip install -r requirements.txt
```

### 2. Setup Environment

Create `.env` file:

```env
MONGODB_URL=your_mongodb_connection_string
DATABASE_NAME=hrms_lite
```

### 3. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs

## API Endpoints

### Employees

- `POST /employees` - Create employee
- `GET /employees` - Get all employees
- `GET /employees/{id}` - Get employee by ID
- `PUT /employees/{id}` - Update employee
- `DELETE /employees/{id}` - Delete employee

### Attendance

- `POST /attendance` - Mark attendance
- `GET /attendance` - Get all attendance
- `GET /attendance/employee/{id}` - Get employee attendance

## Example Request

```json
POST /employees

{
  "employee_id": "EMP001",
  "full_name": "John Doe",
  "email": "john@company.com",
  "department": "Engineering"
}
```

## Project Structure

```
app/
├── main.py          # Entry point
├── config.py        # Settings
├── database.py      # DB connection
├── schemas/         # Data validation
├── services/        # Business logic
├── routes/          # API endpoints
└── exceptions/      # Error handling
```

## Deployment
live link - [LIVE DEMO](https://hrms-lite-api-556b.onrender.com)

## License

MIT
