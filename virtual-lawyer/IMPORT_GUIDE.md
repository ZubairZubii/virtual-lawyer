# Import Guide for MongoDB Models

## Import Paths

Since the models are located in `src/Schemas/`, and `api_complete.py` already has:
```python
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

You can import models in two ways:

### Method 1: Direct import (Recommended)
```python
# In api_complete.py or any file that has src in path
from Schemas import UserCreate, UserResponse, LawyerCreate, CaseCreate
from Schemas.admin_settings_model import AdminSettingsUpdate
```

### Method 2: Full path import
```python
# If src is not in path, use full path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
from Schemas import UserCreate, UserResponse
```

## Using Database Models

The database models are in `src/database/models.py` and work with dictionaries:

```python
# Import database models
from database.models import UserModel, LawyerModel, CaseModel

# Use them (all methods are async)
user = await UserModel.find_by_email("user@example.com")
lawyer = await LawyerModel.find_by_id("lawyer_123")
cases = await CaseModel.find_by_user_id("user_123")
```

## Using Pydantic Models with Database Models

```python
from Schemas import UserCreate, UserResponse
from database.models import UserModel

# Create user with Pydantic validation
user_data = UserCreate(
    name="John Doe",
    email="john@example.com",
    password="secure123"
)

# Convert to dict for database
user_dict = user_data.model_dump()
user_dict["id"] = "user_123"
user_dict["password"] = hash_password(user_dict["password"])  # Hash password

# Save to database
await UserModel.create(user_dict)

# Retrieve and convert to response
user_doc = await UserModel.find_by_id("user_123")
user_response = UserResponse(**user_doc)
```

## Collection of All Available Imports

### From Schemas (Pydantic Models):
```python
from Schemas import (
    # User models
    UserCreate, UserUpdate, UserResponse, UserInDB,
    # Lawyer models
    LawyerCreate, LawyerUpdate, LawyerResponse, LawyerInDB,
    # Case models
    CaseCreate, CaseUpdate, CaseResponse,
    # Lawyer-Client models
    LawyerClientCreate, LawyerClientUpdate, LawyerClientResponse,
    # Admin Settings models
    AdminSettingsUpdate, AdminSettingsResponse
)
```

### From Database Models:
```python
from database.models import (
    UserModel,
    LawyerModel,
    CaseModel,
    LawyerClientModel,
    AdminSettingsModel,
    initialize_indexes  # Function to create all indexes
)
```

### From Database Connection:
```python
from database.connection import (
    get_database,
    get_client,
    check_connection,
    close_connection,
    init_database
)
```

