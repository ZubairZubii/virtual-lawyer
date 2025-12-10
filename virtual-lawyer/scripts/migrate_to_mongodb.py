"""
Data Migration Script
Migrates hardcoded data from api_complete.py to MongoDB

Usage:
    python scripts/migrate_to_mongodb.py

This script will:
1. Read hardcoded data from api_complete.py
2. Hash passwords using bcrypt
3. Migrate all data to MongoDB collections
4. Create indexes
5. Handle duplicates
"""
import sys
import asyncio
import bcrypt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.connection import get_database, init_database, close_connection, check_connection
from database.models import (
    UserModel, LawyerModel, CaseModel,
    LawyerClientModel, AdminSettingsModel,
    initialize_indexes
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Hardcoded data from api_complete.py
USERS_STORAGE: List[Dict] = [
    {
        "id": "1",
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@email.com",
        "role": "Citizen",
        "joinDate": "2024-09-15",
        "status": "Active",
        "casesInvolved": 2,
        "password": "demo123"
    },
    {
        "id": "2",
        "name": "Priya Patel",
        "email": "priya.patel@email.com",
        "role": "Citizen",
        "joinDate": "2024-11-10",
        "status": "Pending",
        "casesInvolved": 0,
        "password": "demo123"
    },
]

LAWYERS_STORAGE: List[Dict] = [
    {
        "id": "1",
        "name": "Adv. Sharma",
        "email": "sharma.law@email.com",
        "specialization": "Criminal Law",
        "verificationStatus": "Verified",
        "casesSolved": 45,
        "winRate": 87,
        "joinDate": "2024-08-20",
        "location": "Delhi",
        "rating": 4.8,
        "reviews": 32,
        "specializations": ["Bail", "Appeals", "Evidence"],
        "yearsExp": 12,
        "cases": 45,
        "password": "demo123",
        "phone": "+91-9876543201"
    },
    {
        "id": "2",
        "name": "Adv. Kumar",
        "email": "kumar.law@email.com",
        "specialization": "Bail & Remand",
        "verificationStatus": "Verified",
        "casesSolved": 32,
        "winRate": 82,
        "joinDate": "2024-09-15",
        "location": "Mumbai",
        "rating": 4.9,
        "reviews": 28,
        "specializations": ["Constitutional", "Appeals", "FIR Defense"],
        "yearsExp": 15,
        "cases": 38,
        "password": "demo123",
        "phone": "+91-9876543202"
    },
    {
        "id": "3",
        "name": "Adv. Singh",
        "email": "singh.law@email.com",
        "specialization": "Appeals",
        "verificationStatus": "Pending",
        "casesSolved": 0,
        "winRate": 0,
        "joinDate": "2024-11-01",
        "location": "Bangalore",
        "rating": 0,
        "reviews": 0,
        "specializations": ["Appeals"],
        "yearsExp": 5,
        "cases": 0,
        "password": "demo123",
        "phone": "+91-9876543203"
    },
]

LAWYER_CLIENTS_STORAGE: List[Dict] = [
    {
        "lawyerId": "1",
        "clientId": "1",
        "clientName": "Rajesh Kumar",
        "clientEmail": "rajesh.kumar@email.com",
        "clientPhone": "+91-9876543210",
        "caseType": "Bail Application",
        "status": "Active",
        "activeCases": 1,
        "totalCases": 2
    },
    {
        "lawyerId": "1",
        "clientId": "2",
        "clientName": "Priya Sharma",
        "clientEmail": "priya.sharma@email.com",
        "clientPhone": "+91-9876543211",
        "caseType": "Appeal",
        "status": "Active",
        "activeCases": 1,
        "totalCases": 1
    },
]

ADMIN_SETTINGS: Dict = {
    "platform_name": "Lawmate",
    "support_email": "support@justiceai.com",
    "max_file_upload_size_mb": 50,
    "email_notifications": True,
    "ai_monitoring": True,
    "auto_backup": True,
    "maintenance_mode": False,
}


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def migrate_users() -> Dict[str, int]:
    """Migrate users to MongoDB"""
    logger.info("=" * 70)
    logger.info("Migrating Users...")
    logger.info("=" * 70)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for user_data in USERS_STORAGE:
        try:
            # Check if user already exists
            existing = await UserModel.find_by_id(user_data["id"])
            if existing:
                logger.warning(f"  ⚠️  User {user_data['id']} ({user_data['email']}) already exists, skipping...")
                skipped += 1
                continue
            
            # Check by email as well
            existing_email = await UserModel.find_by_email(user_data["email"])
            if existing_email:
                logger.warning(f"  ⚠️  User with email {user_data['email']} already exists, skipping...")
                skipped += 1
                continue
            
            # Hash password
            user_data["password"] = hash_password(user_data["password"])
            
            # Ensure required fields
            if "phone" not in user_data:
                user_data["phone"] = None
            
            # Create user
            await UserModel.create(user_data)
            logger.info(f"  ✅ Migrated user: {user_data['name']} ({user_data['email']})")
            migrated += 1
            
        except Exception as e:
            logger.error(f"  ❌ Error migrating user {user_data.get('id', 'unknown')}: {e}")
            errors += 1
    
    logger.info(f"\nUsers Migration Summary: {migrated} migrated, {skipped} skipped, {errors} errors")
    return {"migrated": migrated, "skipped": skipped, "errors": errors}


async def migrate_lawyers() -> Dict[str, int]:
    """Migrate lawyers to MongoDB"""
    logger.info("\n" + "=" * 70)
    logger.info("Migrating Lawyers...")
    logger.info("=" * 70)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for lawyer_data in LAWYERS_STORAGE:
        try:
            # Check if lawyer already exists
            existing = await LawyerModel.find_by_id(lawyer_data["id"])
            if existing:
                logger.warning(f"  ⚠️  Lawyer {lawyer_data['id']} ({lawyer_data['email']}) already exists, skipping...")
                skipped += 1
                continue
            
            # Check by email as well
            existing_email = await LawyerModel.find_by_email(lawyer_data["email"])
            if existing_email:
                logger.warning(f"  ⚠️  Lawyer with email {lawyer_data['email']} already exists, skipping...")
                skipped += 1
                continue
            
            # Hash password
            lawyer_data["password"] = hash_password(lawyer_data["password"])
            
            # Ensure required fields
            if "phone" not in lawyer_data:
                lawyer_data["phone"] = None
            if "specializations" not in lawyer_data:
                lawyer_data["specializations"] = []
            
            # Create lawyer
            await LawyerModel.create(lawyer_data)
            logger.info(f"  ✅ Migrated lawyer: {lawyer_data['name']} ({lawyer_data['email']})")
            migrated += 1
            
        except Exception as e:
            logger.error(f"  ❌ Error migrating lawyer {lawyer_data.get('id', 'unknown')}: {e}")
            errors += 1
    
    logger.info(f"\nLawyers Migration Summary: {migrated} migrated, {skipped} skipped, {errors} errors")
    return {"migrated": migrated, "skipped": skipped, "errors": errors}


async def migrate_lawyer_clients() -> Dict[str, int]:
    """Migrate lawyer-client relationships to MongoDB"""
    logger.info("\n" + "=" * 70)
    logger.info("Migrating Lawyer-Client Relationships...")
    logger.info("=" * 70)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for relationship_data in LAWYER_CLIENTS_STORAGE:
        try:
            # Check if relationship already exists
            existing = await LawyerClientModel.find_relationship(
                relationship_data["lawyerId"],
                relationship_data["clientId"]
            )
            if existing:
                logger.warning(
                    f"  ⚠️  Relationship lawyer {relationship_data['lawyerId']} - "
                    f"client {relationship_data['clientId']} already exists, skipping..."
                )
                skipped += 1
                continue
            
            # Create relationship
            await LawyerClientModel.create(relationship_data)
            logger.info(
                f"  ✅ Migrated relationship: Lawyer {relationship_data['lawyerId']} - "
                f"Client {relationship_data['clientName']}"
            )
            migrated += 1
            
        except Exception as e:
            logger.error(
                f"  ❌ Error migrating relationship lawyer {relationship_data.get('lawyerId', 'unknown')} - "
                f"client {relationship_data.get('clientId', 'unknown')}: {e}"
            )
            errors += 1
    
    logger.info(
        f"\nLawyer-Client Migration Summary: {migrated} migrated, {skipped} skipped, {errors} errors"
    )
    return {"migrated": migrated, "skipped": skipped, "errors": errors}


async def migrate_admin_settings() -> Dict[str, int]:
    """Migrate admin settings to MongoDB"""
    logger.info("\n" + "=" * 70)
    logger.info("Migrating Admin Settings...")
    logger.info("=" * 70)
    
    try:
        # Check if settings already exist
        existing = await AdminSettingsModel.get_settings()
        if existing:
            logger.warning("  ⚠️  Admin settings already exist, updating...")
            await AdminSettingsModel.update_settings(ADMIN_SETTINGS)
            logger.info("  ✅ Admin settings updated")
            return {"migrated": 0, "updated": 1, "errors": 0}
        else:
            # Initialize default settings (will use our data)
            await AdminSettingsModel.update_settings(ADMIN_SETTINGS)
            logger.info("  ✅ Admin settings migrated")
            return {"migrated": 1, "updated": 0, "errors": 0}
            
    except Exception as e:
        logger.error(f"  ❌ Error migrating admin settings: {e}")
        return {"migrated": 0, "updated": 0, "errors": 1}


async def verify_migration() -> Dict[str, int]:
    """Verify migration by counting documents"""
    logger.info("\n" + "=" * 70)
    logger.info("Verifying Migration...")
    logger.info("=" * 70)
    
    counts = {}
    
    try:
        users_count = await UserModel.count()
        counts["users"] = users_count
        logger.info(f"  ✅ Users in database: {users_count}")
        
        lawyers_count = await LawyerModel.count()
        counts["lawyers"] = lawyers_count
        logger.info(f"  ✅ Lawyers in database: {lawyers_count}")
        
        cases_count = await CaseModel.count()
        counts["cases"] = cases_count
        logger.info(f"  ✅ Cases in database: {cases_count}")
        
        lawyer_clients_count = await LawyerClientModel.count()
        counts["lawyer_clients"] = lawyer_clients_count
        logger.info(f"  ✅ Lawyer-Client relationships in database: {lawyer_clients_count}")
        
        settings = await AdminSettingsModel.get_settings()
        counts["admin_settings"] = 1 if settings else 0
        logger.info(f"  ✅ Admin settings: {'Present' if settings else 'Missing'}")
        
    except Exception as e:
        logger.error(f"  ❌ Error verifying migration: {e}")
    
    return counts


async def main():
    """Main migration function"""
    print("\n" + "=" * 70)
    print("MongoDB Data Migration Script")
    print("=" * 70)
    print("\nThis script will migrate hardcoded data to MongoDB")
    print("Database: FYP_VirtualLawyer")
    print("\nStarting migration...\n")
    
    try:
        # Initialize database connection
        logger.info("Connecting to MongoDB...")
        if not await check_connection():
            logger.error("❌ Failed to connect to MongoDB. Please check your connection string.")
            return
        
        logger.info("✅ Connected to MongoDB")
        
        # Create indexes
        logger.info("\nCreating database indexes...")
        await initialize_indexes()
        logger.info("✅ Indexes created")
        
        # Migrate data
        users_result = await migrate_users()
        lawyers_result = await migrate_lawyers()
        lawyer_clients_result = await migrate_lawyer_clients()
        admin_settings_result = await migrate_admin_settings()
        
        # Verify migration
        counts = await verify_migration()
        
        # Summary
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print(f"\nUsers: {users_result['migrated']} migrated, {users_result['skipped']} skipped, {users_result['errors']} errors")
        print(f"Lawyers: {lawyers_result['migrated']} migrated, {lawyers_result['skipped']} skipped, {lawyers_result['errors']} errors")
        print(f"Lawyer-Clients: {lawyer_clients_result['migrated']} migrated, {lawyer_clients_result['skipped']} skipped, {lawyer_clients_result['errors']} errors")
        print(f"Admin Settings: {admin_settings_result.get('migrated', 0)} migrated, {admin_settings_result.get('updated', 0)} updated, {admin_settings_result.get('errors', 0)} errors")
        
        print("\n" + "=" * 70)
        print("VERIFICATION")
        print("=" * 70)
        print(f"Users in database: {counts.get('users', 0)}")
        print(f"Lawyers in database: {counts.get('lawyers', 0)}")
        print(f"Cases in database: {counts.get('cases', 0)}")
        print(f"Lawyer-Client relationships: {counts.get('lawyer_clients', 0)}")
        print(f"Admin settings: {'Present' if counts.get('admin_settings', 0) > 0 else 'Missing'}")
        
        print("\n" + "=" * 70)
        print("✅ Migration completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Close connection
        await close_connection()
        logger.info("✅ Database connection closed")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

