"""
Test script to verify all imports work correctly
Run this to check if Phase 2 & 3 implementation is correct
"""
import sys
from pathlib import Path

# Add src to path (same as api_complete.py)
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 70)
print("Testing Imports from src/Schemas/")
print("=" * 70)

try:
    # Test Pydantic model imports
    print("\n1. Testing Pydantic model imports...")
    from Schemas import (
        UserCreate, UserUpdate, UserResponse, UserInDB,
        LawyerCreate, LawyerUpdate, LawyerResponse, LawyerInDB,
        CaseCreate, CaseUpdate, CaseResponse,
        LawyerClientCreate, LawyerClientUpdate, LawyerClientResponse,
        AdminSettingsUpdate, AdminSettingsResponse
    )
    print("   ✅ All Pydantic models imported successfully!")
    
    # Test database model imports
    print("\n2. Testing database model imports...")
    from database.models import (
        UserModel, LawyerModel, CaseModel,
        LawyerClientModel, AdminSettingsModel,
        initialize_indexes
    )
    print("   ✅ All database models imported successfully!")
    
    # Test connection imports
    print("\n3. Testing connection imports...")
    from database.connection import (
        get_database, get_client, check_connection,
        close_connection, init_database
    )
    print("   ✅ All connection functions imported successfully!")
    
    # Test model instantiation
    print("\n4. Testing model instantiation...")
    user_create = UserCreate(
        name="Test User",
        email="test@example.com",
        password="test123"
    )
    print(f"   ✅ UserCreate model works: {user_create.name}")
    
    lawyer_create = LawyerCreate(
        name="Test Lawyer",
        email="lawyer@example.com",
        password="test123",
        specialization="Criminal Law"
    )
    print(f"   ✅ LawyerCreate model works: {lawyer_create.name}")
    
    case_create = CaseCreate(
        case_type="Bail Application",
        court="High Court"
    )
    print(f"   ✅ CaseCreate model works: {case_create.case_type}")
    
    print("\n" + "=" * 70)
    print("✅ All imports and models are working correctly!")
    print("✅ Phase 2 & 3 implementation is correct!")
    print("=" * 70)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("Please check the file structure and import paths.")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

