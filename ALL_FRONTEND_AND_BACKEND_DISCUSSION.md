# 📚 Complete Frontend and Backend API Documentation

## 🎯 Overview

This document provides a comprehensive overview of all APIs, data storage, and database integration for the Virtual Lawyer AI platform.

---

## 🌐 **FRONTEND API ENDPOINTS**

### **Base Configuration**
- **API Base URL**: `http://localhost:8000` (Development)
- **Environment Variable**: `NEXT_PUBLIC_API_URL`
- **Location**: `Lawmate/Lawmate/lib/api.ts`

---

## 📱 **FRONTEND SERVICE MODULES**

### **1. Authentication (`lib/services/auth.ts`)**

#### **Login**
- **Endpoint**: `POST /api/auth/login`
- **Request Body**:
  ```typescript
  {
    email: string;
    password: string;
    userType: "citizen" | "lawyer" | "admin";
  }
  ```
- **Response**:
  ```typescript
  {
    success: boolean;
    user: {
      id: string;
      name: string;
      email: string;
      role: string;
      userType: string;
      status?: string;
      verificationStatus?: string;
    };
    message: string;
  }
  ```
- **Used In**: `/login` page

#### **Signup**
- **Endpoint**: `POST /api/auth/signup`
- **Request Body**:
  ```typescript
  {
    name: string;
    email: string;
    password: string;
    userType: "citizen" | "lawyer";
  }
  ```
- **Response**: Same as login
- **Used In**: `/signup` page

---

### **2. Chat Service (`lib/services/chat.ts`)**

#### **Chat with AI**
- **Endpoint**: `POST /api/chat`
- **Request Body**:
  ```typescript
  {
    question: string;
    context?: string;
  }
  ```
- **Response**:
  ```typescript
  {
    answer: string;
    references: Array<{
      source: string;
      section?: string;
      relevance: number;
    }>;
    response_time: number;
  }
  ```
- **Used In**: 
  - `/citizen/chatbot` page
  - `/lawyer/chatbot` page

---

### **3. Case Analysis (`lib/services/analysis.ts`)**

#### **Risk Analysis**
- **Endpoint**: `POST /api/risk-analysis`
- **Request Body**: `AnalysisRequest` (case details)
- **Response**: Risk assessment with factors and recommendations
- **Used In**: `/citizen/cases/analyze`, `/lawyer/cases/analyze`

#### **Case Prediction**
- **Endpoint**: `POST /api/case-prediction`
- **Request Body**: `AnalysisRequest`
- **Response**: Conviction probability, bail probability, sentence prediction
- **Used In**: Analysis pages

#### **Advanced Analysis**
- **Endpoint**: `POST /api/advanced-analysis`
- **Request Body**: `AnalysisRequest`
- **Response**: Comprehensive analysis with legal strategy
- **Used In**: Analysis pages

#### **Comprehensive Analysis**
- **Endpoint**: `POST /api/comprehensive`
- **Request Body**: `AnalysisRequest`
- **Response**: All-in-one analysis (chat + risk + prediction + advanced)
- **Used In**: Analysis pages (default option)

#### **Text-Based Analysis**
- **Endpoint**: `POST /api/case-analysis-text`
- **Request Body**: `{ case_text: string }`
- **Response**: Analysis from text description
- **Used In**: Analysis pages

#### **Bail Prediction**
- **Endpoint**: `POST /api/bail-prediction`
- **Request Body**: `BailFactorsRequest`
- **Response**: Bail likelihood with factors
- **Used In**: Analysis pages

---

### **4. Document Service (`lib/services/documents.ts`)**

#### **List Templates**
- **Endpoint**: `GET /api/document/templates`
- **Response**: Array of template objects with `id`, `name`, `category`
- **Used In**: `/citizen/documents`, `/lawyer/documents`

#### **Get Template Details**
- **Endpoint**: `GET /api/document/templates/{template_id}`
- **Response**: Template details with placeholders and descriptions
- **Used In**: Document generation pages

#### **Upload Document**
- **Endpoint**: `POST /api/document/upload`
- **Request**: `FormData` with file
- **Response**: Document ID and metadata
- **Used In**: Document analysis pages

#### **Ask Question About Document**
- **Endpoint**: `POST /api/document/question`
- **Request Body**: `{ doc_id: string, question: string }`
- **Response**: Answer about the document
- **Used In**: Document analysis pages

#### **Extract Facts**
- **Endpoint**: `GET /api/document/{doc_id}/extract`
- **Response**: Extracted facts from document
- **Used In**: Document analysis pages

#### **Get Summary**
- **Endpoint**: `GET /api/document/{doc_id}/summary`
- **Response**: Document summary
- **Used In**: Document analysis pages

#### **Generate Document**
- **Endpoint**: `POST /api/document/generate`
- **Request Body**:
  ```typescript
  {
    template_id: string;
    data: Record<string, any>;
    generate_ai_sections?: boolean;
  }
  ```
- **Response**: Generated document path and filename
- **Used In**: Document generation pages

#### **Download Document**
- **Endpoint**: `GET /api/document/download/{filename}?format=docx`
- **Response**: File blob
- **Used In**: Document pages (download button)

#### **Suggest Document Type**
- **Endpoint**: `POST /api/document/suggest`
- **Request Body**: `{ case_details: object }`
- **Response**: Suggested document types
- **Used In**: Document pages

---

### **5. Dashboard Service (`lib/services/dashboard.ts`)**

#### **Citizen Dashboard**
- **Endpoint**: `GET /api/dashboard/citizen`
- **Response**: Stats, recent cases, recommendations, next hearing
- **Used In**: `/citizen` page

#### **Lawyer Dashboard**
- **Endpoint**: `GET /api/dashboard/lawyer`
- **Response**: Metrics, urgent cases, performance, trends
- **Used In**: `/lawyer` page

---

### **6. Cases Service (`lib/services/cases.ts`)**

#### **Get Citizen Cases**
- **Endpoint**: `GET /api/cases/citizen?status=all`
- **Response**: Array of case objects
- **Used In**: `/citizen/cases` page

#### **Get Lawyer Cases**
- **Endpoint**: `GET /api/cases/lawyer?status=all`
- **Response**: Array of case objects
- **Used In**: `/lawyer/cases` page

#### **Get Case Details**
- **Endpoint**: `GET /api/cases/{case_id}`
- **Response**: Detailed case information
- **Used In**: Case detail pages

#### **Create Case**
- **Endpoint**: `POST /api/cases?user_type=citizen`
- **Request Body**: `CreateCaseRequest`
- **Response**: Created case object
- **Used In**: Case creation forms

---

### **7. Admin Service (`lib/services/admin.ts`)**

#### **Admin Dashboard**
- **Endpoint**: `GET /api/admin/dashboard`
- **Response**: System metrics, recent activity, system status
- **Used In**: `/admin` page

#### **Get Admin Settings**
- **Endpoint**: `GET /api/admin/settings`
- **Response**: Platform settings
- **Used In**: `/admin/settings` page

#### **Update Admin Settings**
- **Endpoint**: `POST /api/admin/settings`
- **Request Body**: Settings object
- **Response**: Updated settings
- **Used In**: `/admin/settings` page

---

### **8. Admin Users Service (`lib/services/admin-users.ts`)**

#### **Get Users**
- **Endpoint**: `GET /api/admin/users?search=query`
- **Response**: Array of users
- **Used In**: `/admin/users` page

#### **Create User**
- **Endpoint**: `POST /api/admin/users`
- **Request Body**: `CreateUserRequest`
- **Response**: Created user
- **Used In**: Admin users page (Add User modal)

#### **Update User**
- **Endpoint**: `PUT /api/admin/users/{user_id}`
- **Request Body**: Partial user object
- **Response**: Updated user
- **Used In**: Admin users page

#### **Delete User**
- **Endpoint**: `DELETE /api/admin/users/{user_id}`
- **Response**: Success message
- **Used In**: Admin users page

---

### **9. Admin Lawyers Service (`lib/services/admin-lawyers.ts`)**

#### **Get Lawyers**
- **Endpoint**: `GET /api/admin/lawyers`
- **Response**: Array of lawyers
- **Used In**: `/admin/lawyers` page

#### **Create Lawyer**
- **Endpoint**: `POST /api/admin/lawyers`
- **Request Body**: `CreateLawyerRequest`
- **Response**: Created lawyer
- **Used In**: Admin lawyers page (Add Lawyer modal)

#### **Verify Lawyer**
- **Endpoint**: `PUT /api/admin/lawyers/{lawyer_id}/verify?status=Verified`
- **Response**: Updated lawyer
- **Used In**: Admin lawyers page (Approve/Reject buttons)

#### **Delete Lawyer**
- **Endpoint**: `DELETE /api/admin/lawyers/{lawyer_id}`
- **Response**: Success message
- **Used In**: Admin lawyers page

---

### **10. Lawyer Analytics Service (`lib/services/lawyer-analytics.ts`)**

#### **Get Lawyer Analytics**
- **Endpoint**: `GET /api/analytics/lawyer`
- **Response**: Case outcomes, performance metrics, trends
- **Used In**: `/lawyer/analytics` page

---

### **11. Lawyer Clients Service (`lib/services/lawyer-clients.ts`)**

#### **Get Clients**
- **Endpoint**: `GET /api/lawyer/clients?lawyer_id=id`
- **Response**: Array of client objects
- **Used In**: `/lawyer/clients` page

---

### **12. Citizen Lawyers Service (`lib/services/citizen-lawyers.ts`)**

#### **Get Lawyers (for Citizens)**
- **Endpoint**: `GET /api/lawyers?search=query&specialization=type`
- **Response**: Array of verified lawyers
- **Used In**: `/citizen/lawyers` page

#### **Get Lawyer Profile**
- **Endpoint**: `GET /api/lawyers/{lawyer_id}`
- **Response**: Detailed lawyer profile
- **Used In**: Lawyer profile pages

---

### **13. Analytics Service (`lib/services/analytics.ts`)**

#### **Get Analytics**
- **Endpoint**: `GET /api/analytics?days=30`
- **Response**: Platform analytics (queries, trends, performance)
- **Used In**: `/admin/analytics` page

---

## 🔧 **BACKEND API ENDPOINTS**

### **Base Configuration**
- **Server**: FastAPI (Uvicorn)
- **Port**: `8000`
- **Host**: `0.0.0.0`
- **Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## 📋 **COMPLETE BACKEND API LIST**

### **1. System Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/` | Root endpoint | - | System info |
| GET | `/health` | Health check | - | Component status |

---

### **2. Authentication Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/auth/login` | User login | `LoginRequest` | User info + token |
| POST | `/api/auth/signup` | User registration | `SignupRequest` | User info |

---

### **3. Chat & AI Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/chat` | Chat with legal AI | `{ question, context? }` | Answer + references |

---

### **4. Case Analysis Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/risk-analysis` | Risk assessment | `AnalysisRequest` | Risk score + factors |
| POST | `/api/case-prediction` | Outcome prediction | `AnalysisRequest` | Probabilities + predictions |
| POST | `/api/advanced-analysis` | Advanced analysis | `AnalysisRequest` | Comprehensive analysis |
| POST | `/api/comprehensive` | All-in-one analysis | `AnalysisRequest` | Combined results |
| POST | `/api/case-analysis-text` | Text-based analysis | `{ case_text }` | Analysis from text |
| POST | `/api/bail-prediction` | Bail prediction | `BailFactorsRequest` | Bail likelihood |

---

### **5. Document Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/document/upload` | Upload document | `FormData` (file) | Document ID |
| POST | `/api/document/question` | Ask about document | `{ doc_id, question }` | Answer |
| GET | `/api/document/{doc_id}/extract` | Extract facts | - | Extracted facts |
| GET | `/api/document/{doc_id}/summary` | Get summary | - | Document summary |
| GET | `/api/document/templates` | List templates | - | Template list |
| GET | `/api/document/templates/{template_id}` | Template details | - | Template info |
| POST | `/api/document/generate` | Generate document | `{ template_id, data }` | Generated file |
| GET | `/api/document/download/{filename}` | Download document | - | File blob |
| POST | `/api/document/suggest` | Suggest document type | `{ case_details }` | Suggestions |
| POST | `/api/document/analyze-and-generate` | Complete workflow | `{ doc_id, template_id }` | Generated document |

---

### **6. Dashboard Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/dashboard/citizen` | Citizen dashboard | - | Dashboard data |
| GET | `/api/dashboard/lawyer` | Lawyer dashboard | - | Dashboard data |

---

### **7. Cases Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/cases/citizen?status=all` | Get citizen cases | - | Case list |
| GET | `/api/cases/lawyer?status=all` | Get lawyer cases | - | Case list |
| GET | `/api/cases/{case_id}` | Get case details | - | Case details |
| POST | `/api/cases?user_type=citizen` | Create case | `CreateCaseRequest` | Created case |

---

### **8. Admin Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/admin/dashboard` | Admin dashboard | - | System metrics |
| GET | `/api/admin/settings` | Get settings | - | Settings object |
| POST | `/api/admin/settings` | Update settings | Settings object | Updated settings |
| GET | `/api/admin/users?search=query` | Get users | - | User list |
| POST | `/api/admin/users` | Create user | `CreateUserRequest` | Created user |
| PUT | `/api/admin/users/{user_id}` | Update user | Partial user | Updated user |
| DELETE | `/api/admin/users/{user_id}` | Delete user | - | Success message |
| GET | `/api/admin/lawyers` | Get lawyers | - | Lawyer list |
| POST | `/api/admin/lawyers` | Create lawyer | `CreateLawyerRequest` | Created lawyer |
| PUT | `/api/admin/lawyers/{lawyer_id}/verify` | Verify lawyer | `?status=Verified` | Updated lawyer |
| DELETE | `/api/admin/lawyers/{lawyer_id}` | Delete lawyer | - | Success message |

---

### **9. Analytics Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/analytics?days=30` | Platform analytics | - | Analytics data |
| GET | `/api/analytics/lawyer` | Lawyer analytics | - | Case performance |

---

### **10. Lawyer Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/lawyer/clients?lawyer_id=id` | Get clients | - | Client list |

---

### **11. Citizen Lawyer Directory Endpoints**

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/lawyers?search=query&specialization=type` | Get lawyers | - | Lawyer list |
| GET | `/api/lawyers/{lawyer_id}` | Get lawyer profile | - | Lawyer details |

---

## 💾 **CURRENT DATA STORAGE**

### **In-Memory Storage (Current Implementation)**

The backend currently uses **in-memory Python lists and dictionaries** for data storage. This means data is lost when the server restarts.

#### **Storage Variables (in `api_complete.py`)**

1. **`USERS_STORAGE`** - Citizen users
   ```python
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
       # ... more users
   ]
   ```

2. **`LAWYERS_STORAGE`** - Lawyer profiles
   ```python
   LAWYERS_STORAGE: List[Dict] = [
       {
           "id": "1",
           "name": "Adv. Sharma",
           "email": "sharma.law@email.com",
           "specialization": "Criminal Law",
           "verificationStatus": "Verified",
           "casesSolved": 45,
           "winRate": 87,
           # ... more fields
       },
       # ... more lawyers
   ]
   ```

3. **`CITIZEN_CASES_STORAGE`** - Citizen cases
   ```python
   CITIZEN_CASES_STORAGE: List[Dict] = []
   ```

4. **`LAWYER_CASES_STORAGE`** - Lawyer cases
   ```python
   LAWYER_CASES_STORAGE: List[Dict] = []
   ```

5. **`LAWYER_CLIENTS_STORAGE`** - Lawyer-client relationships
   ```python
   LAWYER_CLIENTS_STORAGE: List[Dict] = [
       {
           "lawyerId": "1",
           "clientId": "1",
           "clientName": "Rajesh Kumar",
           # ... more fields
       }
   ]
   ```

6. **`ADMIN_SETTINGS`** - Platform settings
   ```python
   ADMIN_SETTINGS: Dict = {
       "platform_name": "Lawmate",
       "support_email": "support@justiceai.com",
       "max_file_upload_size_mb": 50,
       "email_notifications": True,
       "ai_monitoring": True,
       "auto_backup": True,
       "maintenance_mode": False,
   }
   ```

#### **Limitations of In-Memory Storage**

- ❌ **Data Loss**: All data is lost when server restarts
- ❌ **No Persistence**: Cannot recover data after crashes
- ❌ **Single Server**: Cannot scale to multiple servers
- ❌ **No Relationships**: Difficult to maintain data integrity
- ❌ **No Queries**: Limited search and filtering capabilities

---

## 🗄️ **DATABASE INTEGRATION GUIDE**

### **Recommended Database: PostgreSQL**

PostgreSQL is recommended because:
- ✅ Robust and reliable
- ✅ Excellent for complex queries
- ✅ Supports JSON fields
- ✅ Good performance
- ✅ Free and open-source

### **Alternative Options**

1. **SQLite** - Simple, file-based (good for development)
2. **MySQL** - Popular, widely used
3. **MongoDB** - NoSQL, document-based (if you prefer JSON)

---

## 📦 **STEP 1: Install Database Dependencies**

### **For PostgreSQL**

```bash
pip install sqlalchemy psycopg2-binary alembic
```

### **For SQLite (Simpler, for Development)**

```bash
pip install sqlalchemy alembic
```

---

## 🏗️ **STEP 2: Database Schema Design**

### **Tables Structure**

```sql
-- Users Table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'Citizen', 'Lawyer', 'Admin'
    status VARCHAR(50) DEFAULT 'Active',
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lawyers Table (extends users)
CREATE TABLE lawyers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    specialization VARCHAR(255),
    verification_status VARCHAR(50) DEFAULT 'Pending',
    cases_solved INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2) DEFAULT 0,
    location VARCHAR(255),
    phone VARCHAR(50),
    years_exp INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0,
    reviews INTEGER DEFAULT 0,
    specializations TEXT[], -- Array of specializations
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cases Table
CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE SET NULL,
    case_type VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Active',
    court VARCHAR(255),
    judge VARCHAR(255),
    sections TEXT[], -- Array of sections
    police_station VARCHAR(255),
    fir_number VARCHAR(100),
    client_name VARCHAR(255),
    description TEXT,
    filing_date DATE,
    next_hearing DATE,
    priority VARCHAR(50), -- For lawyer cases
    documents_count INTEGER DEFAULT 0,
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lawyer-Client Relationships
CREATE TABLE lawyer_clients (
    id SERIAL PRIMARY KEY,
    lawyer_id INTEGER REFERENCES lawyers(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    case_type VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Active',
    active_cases INTEGER DEFAULT 0,
    total_cases INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lawyer_id, client_id)
);

-- Admin Settings
CREATE TABLE admin_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents Table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated Documents
CREATE TABLE generated_documents (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    template_id VARCHAR(255) NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔌 **STEP 3: Create Database Connection Module**

Create a new file: `src/database.py`

```python
"""
Database connection and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://username:password@localhost:5432/virtual_lawyer_db"
)

# For SQLite (development):
# DATABASE_URL = "sqlite:///./virtual_lawyer.db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 📝 **STEP 4: Create Database Models**

Create a new file: `src/models.py`

```python
"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, DECIMAL, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # Citizen, Lawyer, Admin
    status = Column(String(50), default="Active")
    join_date = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    cases = relationship("Case", back_populates="user")
    lawyer_profile = relationship("Lawyer", back_populates="user", uselist=False)

class Lawyer(Base):
    __tablename__ = "lawyers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    specialization = Column(String(255))
    verification_status = Column(String(50), default="Pending")
    cases_solved = Column(Integer, default=0)
    win_rate = Column(DECIMAL(5, 2), default=0)
    location = Column(String(255))
    phone = Column(String(50))
    years_exp = Column(Integer, default=0)
    rating = Column(DECIMAL(3, 2), default=0)
    reviews = Column(Integer, default=0)
    specializations = Column(ARRAY(String))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="lawyer_profile")
    cases = relationship("Case", back_populates="lawyer")
    clients = relationship("LawyerClient", back_populates="lawyer")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    lawyer_id = Column(Integer, ForeignKey("lawyers.id", ondelete="SET NULL"), nullable=True)
    case_type = Column(String(255), nullable=False)
    status = Column(String(50), default="Active")
    court = Column(String(255))
    judge = Column(String(255))
    sections = Column(ARRAY(String))
    police_station = Column(String(255))
    fir_number = Column(String(100))
    client_name = Column(String(255))
    description = Column(Text)
    filing_date = Column(Date)
    next_hearing = Column(Date)
    priority = Column(String(50))
    documents_count = Column(Integer, default=0)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="cases")
    lawyer = relationship("Lawyer", back_populates="cases")

class LawyerClient(Base):
    __tablename__ = "lawyer_clients"
    
    id = Column(Integer, primary_key=True, index=True)
    lawyer_id = Column(Integer, ForeignKey("lawyers.id", ondelete="CASCADE"))
    client_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    case_type = Column(String(255))
    status = Column(String(50), default="Active")
    active_cases = Column(Integer, default=0)
    total_cases = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lawyer = relationship("Lawyer", back_populates="clients")
    client = relationship("User")

class AdminSetting(Base):
    __tablename__ = "admin_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

---

## 🔄 **STEP 5: Update API Endpoints to Use Database**

### **Example: Update User Management Endpoint**

**Before (In-Memory):**
```python
@app.get("/api/admin/users")
async def get_admin_users(search: Optional[str] = None):
    users = USERS_STORAGE.copy()
    # ... filter logic
    return {"users": users, "total": len(users)}
```

**After (Database):**
```python
from database import get_db
from models import User, Lawyer
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/api/admin/users")
async def get_admin_users(
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    # Query users
    query = db.query(User)
    
    # Apply search filter
    if search:
        search_lower = search.lower()
        query = query.filter(
            (User.name.ilike(f"%{search_lower}%")) |
            (User.email.ilike(f"%{search_lower}%"))
        )
    
    users = query.all()
    
    # Convert to dict format
    users_list = []
    for user in users:
        user_dict = {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "joinDate": user.join_date.strftime("%Y-%m-%d"),
            "status": user.status,
            "casesInvolved": len(user.cases)
        }
        users_list.append(user_dict)
    
    return {"users": users_list, "total": len(users_list)}
```

---

## 🚀 **STEP 6: Database Setup Commands**

### **1. Create Database (PostgreSQL)**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE virtual_lawyer_db;

# Create user (optional)
CREATE USER lawmate_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE virtual_lawyer_db TO lawmate_user;
```

### **2. Initialize Database Tables**

Create `init_db.py`:

```python
"""Initialize database tables"""
from database import engine, Base
from models import User, Lawyer, Case, LawyerClient, AdminSetting

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
```

Run:
```bash
python init_db.py
```

### **3. Environment Variables**

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://lawmate_user:your_password@localhost:5432/virtual_lawyer_db

# For SQLite (development):
# DATABASE_URL=sqlite:///./virtual_lawyer.db
```

---

## 📊 **STEP 7: Migration Strategy**

### **Option A: Manual Migration (Simple)**

1. Export current in-memory data to JSON
2. Create database tables
3. Import JSON data into database

### **Option B: Use Alembic (Recommended for Production)**

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

---

## 🔐 **STEP 8: Password Hashing**

Update authentication to hash passwords:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

---

## 📋 **STEP 9: Update All Endpoints**

### **Endpoints to Update:**

1. ✅ `/api/auth/login` - Query user from database
2. ✅ `/api/auth/signup` - Insert new user
3. ✅ `/api/admin/users` - Query users from database
4. ✅ `/api/admin/lawyers` - Query lawyers from database
5. ✅ `/api/cases/citizen` - Query cases from database
6. ✅ `/api/cases/lawyer` - Query cases from database
7. ✅ `/api/cases` (POST) - Insert case into database
8. ✅ `/api/lawyer/clients` - Query clients from database
9. ✅ `/api/lawyers` - Query lawyers from database
10. ✅ `/api/admin/settings` - Query/update settings from database

---

## 🎯 **QUICK START: Database Integration**

### **1. Install Dependencies**

```bash
pip install sqlalchemy psycopg2-binary alembic python-dotenv passlib[bcrypt]
```

### **2. Set Up Database**

```bash
# PostgreSQL
createdb virtual_lawyer_db

# Or SQLite (no setup needed)
```

### **3. Create Models and Connection**

- Copy `src/database.py` (from Step 3)
- Copy `src/models.py` (from Step 4)

### **4. Initialize Database**

```bash
python init_db.py
```

### **5. Update Endpoints**

- Replace in-memory storage with database queries
- Use `Depends(get_db)` for database sessions

### **6. Test**

```bash
python api_complete.py
```

---

## 📝 **SUMMARY**

### **Frontend APIs: 13 Service Modules**
- Authentication, Chat, Analysis, Documents, Dashboard, Cases, Admin, Analytics, etc.

### **Backend APIs: 40+ Endpoints**
- System, Auth, Chat, Analysis, Documents, Dashboard, Cases, Admin, Analytics, Lawyers

### **Current Storage: In-Memory**
- 6 storage variables (lists/dicts)
- Data lost on restart
- Not suitable for production

### **Recommended Database: PostgreSQL**
- Robust, reliable, scalable
- Full SQL support
- Good for production

### **Migration Path:**
1. Install dependencies
2. Create database models
3. Set up connection
4. Update endpoints one by one
5. Test thoroughly

---

## 🔗 **USEFUL LINKS**

- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **FastAPI Database**: https://fastapi.tiangolo.com/tutorial/sql-databases/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Alembic Docs**: https://alembic.sqlalchemy.org/

---

**Last Updated**: 2024-12-09
**Version**: 1.0.0

