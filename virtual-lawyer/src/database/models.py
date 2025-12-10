"""
MongoDB Document Models
Helper classes and methods for working with MongoDB documents
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from .connection import get_database
import logging

logger = logging.getLogger(__name__)


class BaseModel:
    """Base model with common helper methods"""
    
    @staticmethod
    def to_dict(document: Dict) -> Dict:
        """Convert MongoDB document to dict, handling ObjectId"""
        if document is None:
            return None
        
        result = {}
        for key, value in document.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @staticmethod
    def prepare_for_insert(data: Dict) -> Dict:
        """Prepare data for MongoDB insert"""
        # Remove None values
        cleaned = {k: v for k, v in data.items() if v is not None}
        
        # Add timestamps if not present
        now = datetime.utcnow()
        if 'createdAt' not in cleaned:
            cleaned['createdAt'] = now
        if 'updatedAt' not in cleaned:
            cleaned['updatedAt'] = now
        
        return cleaned
    
    @staticmethod
    def prepare_for_update(data: Dict) -> Dict:
        """Prepare data for MongoDB update"""
        # Remove None values and timestamps
        cleaned = {k: v for k, v in data.items() 
                  if v is not None and k not in ['_id', 'id', 'createdAt']}
        
        # Update timestamp
        cleaned['updatedAt'] = datetime.utcnow()
        
        return cleaned


class UserModel(BaseModel):
    """User document model"""
    
    @staticmethod
    async def get_collection() -> AsyncIOMotorCollection:
        """Get users collection"""
        db = await get_database()
        return db.users
    
    @staticmethod
    async def create_indexes():
        """Create indexes for users collection"""
        collection = await UserModel.get_collection()
        await collection.create_index("email", unique=True)
        await collection.create_index("id", unique=True)
        await collection.create_index("status")
        logger.info("✅ User indexes created")
    
    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict]:
        """Find user by email"""
        collection = await UserModel.get_collection()
        return await collection.find_one({"email": email.lower()})
    
    @staticmethod
    async def find_by_id(user_id: str) -> Optional[Dict]:
        """Find user by ID"""
        collection = await UserModel.get_collection()
        return await collection.find_one({"id": user_id})
    
    @staticmethod
    async def find_all(filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Find all users matching filter"""
        collection = await UserModel.get_collection()
        filter_dict = filter_dict or {}
        cursor = collection.find(filter_dict)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def create(user_data: Dict) -> Dict:
        """Create new user"""
        collection = await UserModel.get_collection()
        user_data = UserModel.prepare_for_insert(user_data)
        # Normalize email
        if 'email' in user_data:
            user_data['email'] = user_data['email'].lower()
        result = await collection.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return user_data
    
    @staticmethod
    async def update(user_id: str, update_data: Dict) -> Optional[Dict]:
        """Update user"""
        collection = await UserModel.get_collection()
        update_data = UserModel.prepare_for_update(update_data)
        # Normalize email if present
        if 'email' in update_data:
            update_data['email'] = update_data['email'].lower()
        result = await collection.find_one_and_update(
            {"id": user_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    @staticmethod
    async def delete(user_id: str) -> bool:
        """Delete user"""
        collection = await UserModel.get_collection()
        result = await collection.delete_one({"id": user_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def count(filter_dict: Optional[Dict] = None) -> int:
        """Count users matching filter"""
        collection = await UserModel.get_collection()
        filter_dict = filter_dict or {}
        return await collection.count_documents(filter_dict)


class LawyerModel(BaseModel):
    """Lawyer document model"""
    
    @staticmethod
    async def get_collection() -> AsyncIOMotorCollection:
        """Get lawyers collection"""
        db = await get_database()
        return db.lawyers
    
    @staticmethod
    async def create_indexes():
        """Create indexes for lawyers collection"""
        collection = await LawyerModel.get_collection()
        await collection.create_index("email", unique=True)
        await collection.create_index("id", unique=True)
        await collection.create_index("verificationStatus")
        await collection.create_index("specialization")
        logger.info("✅ Lawyer indexes created")
    
    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict]:
        """Find lawyer by email"""
        collection = await LawyerModel.get_collection()
        return await collection.find_one({"email": email.lower()})
    
    @staticmethod
    async def find_by_id(lawyer_id: str) -> Optional[Dict]:
        """Find lawyer by ID"""
        collection = await LawyerModel.get_collection()
        return await collection.find_one({"id": lawyer_id})
    
    @staticmethod
    async def find_all(filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Find all lawyers matching filter"""
        collection = await LawyerModel.get_collection()
        filter_dict = filter_dict or {}
        cursor = collection.find(filter_dict)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def create(lawyer_data: Dict) -> Dict:
        """Create new lawyer"""
        collection = await LawyerModel.get_collection()
        lawyer_data = LawyerModel.prepare_for_insert(lawyer_data)
        # Normalize email
        if 'email' in lawyer_data:
            lawyer_data['email'] = lawyer_data['email'].lower()
        result = await collection.insert_one(lawyer_data)
        lawyer_data['_id'] = result.inserted_id
        return lawyer_data
    
    @staticmethod
    async def update(lawyer_id: str, update_data: Dict) -> Optional[Dict]:
        """Update lawyer"""
        collection = await LawyerModel.get_collection()
        update_data = LawyerModel.prepare_for_update(update_data)
        # Normalize email if present
        if 'email' in update_data:
            update_data['email'] = update_data['email'].lower()
        result = await collection.find_one_and_update(
            {"id": lawyer_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    @staticmethod
    async def delete(lawyer_id: str) -> bool:
        """Delete lawyer"""
        collection = await LawyerModel.get_collection()
        result = await collection.delete_one({"id": lawyer_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def count(filter_dict: Optional[Dict] = None) -> int:
        """Count lawyers matching filter"""
        collection = await LawyerModel.get_collection()
        filter_dict = filter_dict or {}
        return await collection.count_documents(filter_dict)


class CaseModel(BaseModel):
    """Case document model"""
    
    @staticmethod
    async def get_collection() -> AsyncIOMotorCollection:
        """Get cases collection"""
        db = await get_database()
        return db.cases
    
    @staticmethod
    async def create_indexes():
        """Create indexes for cases collection"""
        collection = await CaseModel.get_collection()
        await collection.create_index("id", unique=True)
        await collection.create_index("userId")
        await collection.create_index("lawyerId")
        await collection.create_index("status")
        await collection.create_index("case_type")
        await collection.create_index("assigned_lawyer_id")
        logger.info("✅ Case indexes created")
    
    @staticmethod
    async def find_by_id(case_id: str) -> Optional[Dict]:
        """Find case by ID"""
        collection = await CaseModel.get_collection()
        return await collection.find_one({"id": case_id})
    
    @staticmethod
    async def find_by_user_id(user_id: str, status: Optional[str] = None) -> List[Dict]:
        """Find all cases for a user"""
        collection = await CaseModel.get_collection()
        filter_dict = {"userId": user_id}
        if status and status.lower() != "all":
            filter_dict["status"] = status
        cursor = collection.find(filter_dict).sort("createdAt", -1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def find_by_lawyer_id(lawyer_id: str, status: Optional[str] = None) -> List[Dict]:
        """Find all cases for a lawyer"""
        collection = await CaseModel.get_collection()
        filter_dict = {"lawyerId": lawyer_id}
        if status and status.lower() != "all":
            filter_dict["status"] = status
        cursor = collection.find(filter_dict).sort("createdAt", -1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def find_all(filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Find all cases matching filter"""
        collection = await CaseModel.get_collection()
        filter_dict = filter_dict or {}
        cursor = collection.find(filter_dict).sort("createdAt", -1)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def create(case_data: Dict) -> Dict:
        """Create new case"""
        collection = await CaseModel.get_collection()
        case_data = CaseModel.prepare_for_insert(case_data)
        result = await collection.insert_one(case_data)
        case_data['_id'] = result.inserted_id
        return case_data
    
    @staticmethod
    async def update(case_id: str, update_data: Dict) -> Optional[Dict]:
        """Update case"""
        collection = await CaseModel.get_collection()
        update_data = CaseModel.prepare_for_update(update_data)
        result = await collection.find_one_and_update(
            {"id": case_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    @staticmethod
    async def delete(case_id: str) -> bool:
        """Delete case"""
        collection = await CaseModel.get_collection()
        result = await collection.delete_one({"id": case_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def count(filter_dict: Optional[Dict] = None) -> int:
        """Count cases matching filter"""
        collection = await CaseModel.get_collection()
        filter_dict = filter_dict or {}
        return await collection.count_documents(filter_dict)


class LawyerClientModel(BaseModel):
    """Lawyer-Client relationship document model"""
    
    @staticmethod
    async def get_collection() -> AsyncIOMotorCollection:
        """Get lawyer_clients collection"""
        db = await get_database()
        return db.lawyer_clients
    
    @staticmethod
    async def create_indexes():
        """Create indexes for lawyer_clients collection"""
        collection = await LawyerClientModel.get_collection()
        await collection.create_index("lawyerId")
        await collection.create_index("clientId")
        await collection.create_index([("lawyerId", 1), ("clientId", 1)], unique=True)
        await collection.create_index("status")
        logger.info("✅ Lawyer-Client indexes created")
    
    @staticmethod
    async def find_by_lawyer_id(lawyer_id: str) -> List[Dict]:
        """Find all clients for a lawyer"""
        collection = await LawyerClientModel.get_collection()
        cursor = collection.find({"lawyerId": lawyer_id})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def find_by_client_id(client_id: str) -> List[Dict]:
        """Find all lawyers for a client"""
        collection = await LawyerClientModel.get_collection()
        cursor = collection.find({"clientId": client_id})
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def find_relationship(lawyer_id: str, client_id: str) -> Optional[Dict]:
        """Find specific lawyer-client relationship"""
        collection = await LawyerClientModel.get_collection()
        return await collection.find_one({
            "lawyerId": lawyer_id,
            "clientId": client_id
        })
    
    @staticmethod
    async def find_all(filter_dict: Optional[Dict] = None) -> List[Dict]:
        """Find all relationships matching filter"""
        collection = await LawyerClientModel.get_collection()
        filter_dict = filter_dict or {}
        cursor = collection.find(filter_dict)
        return await cursor.to_list(length=None)
    
    @staticmethod
    async def create(relationship_data: Dict) -> Dict:
        """Create new lawyer-client relationship"""
        collection = await LawyerClientModel.get_collection()
        relationship_data = LawyerClientModel.prepare_for_insert(relationship_data)
        result = await collection.insert_one(relationship_data)
        relationship_data['_id'] = result.inserted_id
        return relationship_data
    
    @staticmethod
    async def update(lawyer_id: str, client_id: str, update_data: Dict) -> Optional[Dict]:
        """Update lawyer-client relationship"""
        collection = await LawyerClientModel.get_collection()
        update_data = LawyerClientModel.prepare_for_update(update_data)
        result = await collection.find_one_and_update(
            {"lawyerId": lawyer_id, "clientId": client_id},
            {"$set": update_data},
            return_document=True
        )
        return result
    
    @staticmethod
    async def delete(lawyer_id: str, client_id: str) -> bool:
        """Delete lawyer-client relationship"""
        collection = await LawyerClientModel.get_collection()
        result = await collection.delete_one({
            "lawyerId": lawyer_id,
            "clientId": client_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    async def count(filter_dict: Optional[Dict] = None) -> int:
        """Count relationships matching filter"""
        collection = await LawyerClientModel.get_collection()
        filter_dict = filter_dict or {}
        return await collection.count_documents(filter_dict)


class AdminSettingsModel(BaseModel):
    """Admin settings document model (single document)"""
    
    @staticmethod
    async def get_collection() -> AsyncIOMotorCollection:
        """Get admin_settings collection"""
        db = await get_database()
        return db.admin_settings
    
    @staticmethod
    async def get_settings() -> Optional[Dict]:
        """Get admin settings (single document)"""
        collection = await AdminSettingsModel.get_collection()
        return await collection.find_one({})
    
    @staticmethod
    async def update_settings(settings_data: Dict) -> Dict:
        """Update admin settings (upsert to ensure single document)"""
        collection = await AdminSettingsModel.get_collection()
        settings_data = AdminSettingsModel.prepare_for_update(settings_data)
        result = await collection.find_one_and_update(
            {},
            {"$set": settings_data},
            upsert=True,
            return_document=True
        )
        return result
    
    @staticmethod
    async def initialize_default_settings() -> Dict:
        """Initialize default admin settings if not exists"""
        collection = await AdminSettingsModel.get_collection()
        existing = await collection.find_one({})
        if existing:
            return existing
        
        default_settings = {
            "platform_name": "Lawmate",
            "support_email": "support@justiceai.com",
            "max_file_upload_size_mb": 50,
            "email_notifications": True,
            "ai_monitoring": True,
            "auto_backup": True,
            "maintenance_mode": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        result = await collection.insert_one(default_settings)
        default_settings['_id'] = result.inserted_id
        logger.info("✅ Default admin settings initialized")
        return default_settings


# Initialize all indexes
async def initialize_indexes():
    """Initialize all collection indexes"""
    try:
        await UserModel.create_indexes()
        await LawyerModel.create_indexes()
        await CaseModel.create_indexes()
        await LawyerClientModel.create_indexes()
        logger.info("✅ All database indexes initialized")
    except Exception as e:
        logger.error(f"❌ Error initializing indexes: {e}")
        raise

