"""
MongoDB Connection Module
Handles database connection, connection pooling, and health checks
"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for database connection
_client: Optional[AsyncIOMotorClient] = None
_database: Optional[AsyncIOMotorDatabase] = None

# MongoDB Configuration from environment
MONGODB_CONNECTION_STRING = os.getenv(
    "MONGODB_CONNECTION_STRING",
    "mongodb+srv://bilalsonofkhirsheed:2249263bilal@cluster0.dp5gbye.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "FYP_VirtualLawyer")


async def get_client() -> AsyncIOMotorClient:
    """
    Get or create MongoDB client connection
    Uses connection pooling for better performance
    """
    global _client
    
    if _client is None:
        try:
            logger.info("Connecting to MongoDB...")
            _client = AsyncIOMotorClient(
                MONGODB_CONNECTION_STRING,
                # Connection pool settings
                maxPoolSize=50,
                minPoolSize=10,
                # Server selection timeout (milliseconds)
                serverSelectionTimeoutMS=5000,
                # Connection timeout (milliseconds)
                connectTimeoutMS=10000,
                # Socket timeout (milliseconds)
                socketTimeoutMS=30000,
            )
            
            # Test the connection
            await _client.admin.command('ping')
            logger.info("✅ Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    return _client


async def get_database() -> AsyncIOMotorDatabase:
    """
    Get database instance
    Creates connection if not already established
    """
    global _database
    
    if _database is None:
        client = await get_client()
        _database = client[MONGODB_DATABASE_NAME]
        logger.info(f"✅ Database '{MONGODB_DATABASE_NAME}' ready")
    
    return _database


async def check_connection() -> bool:
    """
    Check if MongoDB connection is healthy
    Returns True if connection is active, False otherwise
    """
    try:
        client = await get_client()
        # Ping the database to check connection
        await client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"❌ MongoDB connection check failed: {e}")
        return False


async def close_connection():
    """
    Close MongoDB connection
    Should be called on application shutdown
    """
    global _client, _database
    
    if _client:
        _client.close()
        _client = None
        _database = None
        logger.info("✅ MongoDB connection closed")


# Initialize connection on module import (optional - can be lazy loaded)
async def init_database():
    """
    Initialize database connection
    Call this function at application startup
    """
    try:
        await get_database()
        logger.info("✅ Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

