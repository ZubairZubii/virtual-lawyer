"""
Test script to verify MongoDB connection
Run this to check if your MongoDB setup is working correctly
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import (
    get_database,
    get_client,
    check_connection,
    close_connection,
    init_database,
    MONGODB_DATABASE_NAME
)


async def test_connection():
    """Test MongoDB connection and basic operations"""
    print("=" * 70)
    print("MongoDB Connection Test")
    print("=" * 70)
    print(f"\nDatabase Name: {MONGODB_DATABASE_NAME}\n")
    
    try:
        # Test 1: Check connection
        print("1. Testing connection...")
        is_connected = await check_connection()
        if is_connected:
            print("   ✅ Connection successful!")
        else:
            print("   ❌ Connection failed!")
            return
        
        # Test 2: Get database instance
        print("\n2. Getting database instance...")
        db = await get_database()
        print(f"   ✅ Database '{db.name}' ready")
        
        # Test 3: List collections
        print("\n3. Listing collections...")
        collections = await db.list_collection_names()
        if collections:
            print(f"   ✅ Found {len(collections)} collection(s):")
            for col in collections:
                count = await db[col].count_documents({})
                print(f"      - {col}: {count} document(s)")
        else:
            print("   ℹ️  No collections found (database is empty)")
        
        # Test 4: Test write operation (create a test collection)
        print("\n4. Testing write operation...")
        test_collection = db["connection_test"]
        test_doc = {
            "test": True,
            "message": "MongoDB connection test successful",
            "timestamp": "2024-01-01"
        }
        result = await test_collection.insert_one(test_doc)
        print(f"   ✅ Test document inserted with ID: {result.inserted_id}")
        
        # Test 5: Test read operation
        print("\n5. Testing read operation...")
        retrieved_doc = await test_collection.find_one({"_id": result.inserted_id})
        if retrieved_doc:
            print(f"   ✅ Document retrieved: {retrieved_doc['message']}")
        
        # Test 6: Cleanup test document
        print("\n6. Cleaning up test data...")
        await test_collection.delete_one({"_id": result.inserted_id})
        print("   ✅ Test document deleted")
        
        print("\n" + "=" * 70)
        print("✅ All tests passed! MongoDB connection is working correctly.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close connection
        await close_connection()
        print("\n✅ Connection closed")


if __name__ == "__main__":
    asyncio.run(test_connection())

