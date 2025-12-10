# MongoDB Database Schema Documentation

## Database: `FYP_VirtualLawyer`

---

## Collection: `users`

**Description:** Stores citizen user accounts

### Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `id` | String | Yes | User ID (unique, indexed) |
| `name` | String | Yes | Full name |
| `email` | String | Yes | Email address (unique, indexed) |
| `password` | String | Yes | Hashed password (bcrypt) |
| `role` | String | Yes | User role (default: "Citizen") |
| `phone` | String | No | Phone number |
| `status` | String | Yes | Account status: "Active", "Pending", "Suspended" |
| `joinDate` | String | Yes | Registration date (ISO format) |
| `casesInvolved` | Integer | Yes | Number of cases (default: 0) |
| `createdAt` | DateTime | Yes | Document creation timestamp |
| `updatedAt` | DateTime | Yes | Last update timestamp |

### Indexes:
- `email` (unique)
- `id` (unique)
- `status`

---

## Collection: `lawyers`

**Description:** Stores lawyer profiles and accounts

### Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `id` | String | Yes | Lawyer ID (unique, indexed) |
| `name` | String | Yes | Full name |
| `email` | String | Yes | Email address (unique, indexed) |
| `password` | String | Yes | Hashed password (bcrypt) |
| `phone` | String | No | Phone number |
| `specialization` | String | Yes | Primary specialization |
| `specializations` | Array[String] | Yes | List of specializations |
| `verificationStatus` | String | Yes | "Verified", "Pending", "Rejected" |
| `location` | String | No | Location/City |
| `yearsExp` | Integer | Yes | Years of experience (default: 0) |
| `casesSolved` | Integer | Yes | Total cases solved (default: 0) |
| `cases` | Integer | Yes | Total cases handled (default: 0) |
| `winRate` | Integer | Yes | Win rate percentage (0-100, default: 0) |
| `rating` | Float | Yes | Average rating (0-5, default: 0) |
| `reviews` | Integer | Yes | Number of reviews (default: 0) |
| `joinDate` | String | Yes | Registration date (ISO format) |
| `createdAt` | DateTime | Yes | Document creation timestamp |
| `updatedAt` | DateTime | Yes | Last update timestamp |

### Indexes:
- `email` (unique)
- `id` (unique)
- `verificationStatus`
- `specialization`

---

## Collection: `cases`

**Description:** Stores all cases (both citizen and lawyer cases)

### Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `id` | String | Yes | Case ID (unique, indexed) |
| `case_type` | String | Yes | Type of case (e.g., "Bail Application", "Appeal") |
| `status` | String | Yes | Case status: "Active", "Hearing Scheduled", "Closed", "Urgent" |
| `priority` | String | No | Priority level: "High", "Medium", "Low" (for lawyer cases) |
| `userId` | String | No | Citizen user ID (if citizen case) |
| `lawyerId` | String | No | Lawyer ID (if lawyer case) |
| `client_name` | String | No | Client name (for lawyer cases) |
| `court` | String | Yes | Court name |
| `judge` | String | No | Judge name |
| `sections` | Array[String] | No | Legal sections involved |
| `police_station` | String | No | Police station name |
| `fir_number` | String | No | FIR number |
| `description` | String | No | Case description |
| `filing_date` | String | No | Filing date (ISO format) |
| `next_hearing` | String | No | Next hearing date (ISO format) |
| `deadline` | String | No | Deadline (for lawyer cases) |
| `documents_count` | Integer | Yes | Number of documents (default: 0) |
| `assigned_lawyer` | String | No | Assigned lawyer name |
| `assigned_lawyer_id` | String | No | Assigned lawyer ID |
| `progress` | Integer | Yes | Progress percentage (0-100, default: 0) |
| `hours_billed` | Integer | No | Hours billed (for lawyer cases) |
| `createdAt` | DateTime | Yes | Document creation timestamp |
| `updatedAt` | DateTime | Yes | Last update timestamp |

### Indexes:
- `id` (unique)
- `userId`
- `lawyerId`
- `status`
- `case_type`
- `assigned_lawyer_id`

---

## Collection: `lawyer_clients`

**Description:** Stores lawyer-client relationships

### Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `lawyerId` | String | Yes | Lawyer ID (indexed) |
| `clientId` | String | Yes | Client/Citizen user ID (indexed) |
| `clientName` | String | Yes | Client name |
| `clientEmail` | String | Yes | Client email |
| `clientPhone` | String | No | Client phone |
| `caseType` | String | No | Type of case |
| `status` | String | Yes | Relationship status: "Active", "Inactive", "Closed" |
| `activeCases` | Integer | Yes | Number of active cases (default: 0) |
| `totalCases` | Integer | Yes | Total cases together (default: 0) |
| `createdAt` | DateTime | Yes | Document creation timestamp |
| `updatedAt` | DateTime | Yes | Last update timestamp |

### Indexes:
- `lawyerId`
- `clientId`
- Compound index: `(lawyerId, clientId)` (unique)
- `status`

---

## Collection: `admin_settings`

**Description:** Platform-wide settings (single document)

### Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `platform_name` | String | Yes | Platform name |
| `support_email` | String | Yes | Support email address |
| `max_file_upload_size_mb` | Integer | Yes | Maximum file upload size in MB |
| `email_notifications` | Boolean | Yes | Enable email notifications |
| `ai_monitoring` | Boolean | Yes | Enable AI monitoring |
| `auto_backup` | Boolean | Yes | Enable automatic backups |
| `maintenance_mode` | Boolean | Yes | Maintenance mode flag |
| `updatedAt` | DateTime | Yes | Last update timestamp |

### Notes:
- Only one document should exist in this collection
- Use `findOneAndUpdate` with `upsert: true` to ensure single document

---

## Collection: `sessions` (Optional - Future)

**Description:** User authentication sessions and tokens

### Fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `_id` | ObjectId | Yes | MongoDB auto-generated ID |
| `userId` | String | Yes | User ID |
| `userType` | String | Yes | "Citizen" or "Lawyer" |
| `token` | String | Yes | JWT token |
| `refreshToken` | String | No | Refresh token |
| `expiresAt` | DateTime | Yes | Token expiration |
| `createdAt` | DateTime | Yes | Session creation timestamp |

### Indexes:
- `userId`
- `token` (unique)
- `expiresAt` (TTL index for auto-deletion)

---

## Data Relationships

```
users (Citizens)
  └── cases (userId)
      └── assigned_lawyer_id → lawyers

lawyers
  └── cases (lawyerId)
  └── lawyer_clients (lawyerId)
      └── clientId → users

cases
  ├── userId → users
  └── lawyerId → lawyers
```

---

## Indexes Summary

### Performance Indexes:
1. **users**: `email` (unique), `id` (unique), `status`
2. **lawyers**: `email` (unique), `id` (unique), `verificationStatus`, `specialization`
3. **cases**: `id` (unique), `userId`, `lawyerId`, `status`, `case_type`, `assigned_lawyer_id`
4. **lawyer_clients**: `lawyerId`, `clientId`, compound `(lawyerId, clientId)` (unique), `status`
5. **admin_settings**: No indexes needed (single document)
6. **sessions**: `userId`, `token` (unique), `expiresAt` (TTL)

---

## Migration Notes

- All `id` fields will be preserved from hardcoded data
- `_id` is MongoDB's auto-generated ObjectId
- Timestamps (`createdAt`, `updatedAt`) will be added during migration
- Passwords should be hashed using bcrypt before storage
- Email addresses should be validated and normalized (lowercase)

