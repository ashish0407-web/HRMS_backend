from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import IndexModel, ASCENDING
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None


db = Database()


async def connect_to_database():
    """
    Create database connection and set up indexes.
    Called on application startup.
    """
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]
        
        # Verify connection
        await db.client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def create_indexes():
    """Create database indexes for better performance."""
    try:
        # Employee indexes
        employees_collection = get_employees_collection()
        await employees_collection.create_indexes([
            IndexModel([("employee_id", ASCENDING)], unique=True),
            IndexModel([("email", ASCENDING)], unique=True),
            IndexModel([("department", ASCENDING)])
        ])
        logger.info("Employee indexes created successfully")
        
        # Attendance indexes
        attendance_collection = get_attendance_collection()
        await attendance_collection.create_indexes([
            IndexModel([("employee_id", ASCENDING), ("date", ASCENDING)], unique=True),
            IndexModel([("date", ASCENDING)]),
            IndexModel([("employee_id", ASCENDING)])
        ])
        logger.info("Attendance indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {e}")
        raise


async def close_database_connection():
    """
    Close database connection.
    Called on application shutdown.
    """
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    if db.database is None:
        raise RuntimeError("Database not initialized. Call connect_to_database() first.")
    return db.database


def get_employees_collection():
    """Get employees collection."""
    return get_database()["employees"]


def get_attendance_collection():
    """Get attendance collection."""
    return get_database()["attendance"]