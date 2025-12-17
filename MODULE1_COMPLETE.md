# Module 1: Citizen Request Submission - Implementation Complete ✅

**Date:** 2025-12-18  
**Status:** READY FOR PRODUCTION TESTING  
**Architecture Phase:** Phase 1 of 5 (Governance-First Traffic Permission Module)

---

## 📊 Executive Summary

Module 1 implements the **Citizen Request Submission Layer** of the governance-first traffic permission system. This layer allows citizens to submit route permission requests for public events with 5-day advance constraint enforcement and full audit trail logging.

**Key Achievement:** Complete end-to-end API implementation with production-grade validation, error handling, and accountability tracking.

---

## ✅ Deliverables

### 1. **Database Models** ✓
**File:** `Traffic_Backend/models.py`

#### RoutePermissionRequest Model
- **Purpose:** Store all citizen requests with complete event details
- **Fields (35+):**
  - Citizen info: name, phone, email, organization
  - Event details: type, name, description, participants, vehicle category
  - Temporal data: event date, start time, end time
  - Spatial data: route geometry (GeoJSON), calculated length & area
  - Workflow: status (8 states), submitted/reviewed/approved dates
  - Governance: reviewer ID, comments, rejection reason
  - Observation phase: start/completion dates, baseline traffic summary
  - Intelligence: alternative routes count & data
  - Live ops: monitoring start date, max congestion, critical alerts
  - Metadata: created/updated timestamps
- **Constraints:**
  - `event_end_time > event_start_time` (CHECK constraint)
  - `expected_participants >= 0` (CHECK constraint)
  - `request_number` UNIQUE (globally unique submission ID)
  - Foreign key to `users.id` (reviewer relationship)

#### AuditLog Model
- **Purpose:** Track every action on every request for accountability
- **Fields (8):**
  - action: enum of 8 governance actions
  - action_description: human-readable description
  - user_id: who performed action (nullable for system actions)
  - user_role: role at time of action
  - timestamp: when action occurred
  - permission_request_id: which request it affects
  - audit_metadata: JSON context (IP, endpoint, etc.)
  - relationships: back_populates to RoutePermissionRequest

#### Enums
- `RequestStatus`: pending, under_review, approved, rejected, observing, active, completed, cancelled
- `EventType`: rally, procession, marathon, protest, religious_gathering, cultural_event, sports_event, other
- `VehicleCategory`: heavy, light, mixed
- `AuditAction`: request_submitted, request_reviewed, request_approved, request_rejected, observation_started, observation_completed, alternative_routes_calculated, live_monitoring_started

### 2. **API Endpoints** ✓
**File:** `Traffic_Backend/routers/permission_requests.py`

#### POST `/api/permission-requests/` - Create Request
- **Input:** RoutePermissionRequestCreate schema
- **Validations:**
  - Event date must be ≥ 5 days from now (governance constraint)
  - Event end time > start time
  - Geometry must be valid GeoJSON (LineString, Polygon, MultiLineString)
  - Required fields enforced
- **Processing:**
  - Generate unique request number (RPR-YYYY-NNNNNN format)
  - Calculate route metrics (length in km, area in km²)
  - Create database record with PENDING status
  - Log audit entry for accountability
- **Response:** Full RoutePermissionRequestResponse (201 Created)
- **Error Handling:** 422 validation errors, 500 server errors with details

#### GET `/api/permission-requests/` - List Requests
- **Query Parameters:**
  - `page`: page number (default 1)
  - `page_size`: items per page (default 20, max 100)
  - `status_filter`: filter by RequestStatus enum
  - `event_type_filter`: filter by event type
- **Response:** PermissionRequestListResponse with pagination metadata
- **Features:** Ordered by submission date (newest first)

#### GET `/api/permission-requests/{request_id}` - Get by ID
- **Path Parameter:** request_id (unique request ID)
- **Response:** Full RoutePermissionRequestResponse with all fields
- **Error Handling:** 404 if request not found

#### GET `/api/permission-requests/{request_id}/audit-logs` - Audit Trail
- **Path Parameter:** request_id
- **Response:** List[AuditLogResponse] in chronological order
- **Features:** Complete governance transparency/accountability

#### DELETE `/api/permission-requests/{request_id}` - Cancel Request
- **Business Rule:** Only PENDING requests can be cancelled by citizen
- **Processing:**
  - Verify request exists
  - Check status is PENDING
  - Update status to CANCELLED
  - Log audit entry
- **Response:** Confirmation with request_number and new status
- **Error Handling:** 404 if not found, 400 if not PENDING

### 3. **Validation Schemas** ✓
**File:** `Traffic_Backend/schemas/permission_schemas.py`

#### RoutePermissionRequestCreate
- **Custom Validators (3):**
  - `validate_event_date_constraint`: Enforces 5+ day rule with detailed error messages including days away and earliest allowed date
  - `validate_event_time_order`: Ensures end > start
  - `validate_geometry`: Validates GeoJSON structure and allowed types
- **Field Patterns:**
  - Phone: `^\+?[\d\s\-()]{10,20}$`
  - Email: `^[\w\.-]+@[\w\.-]+\.\w+$`
  - Min/max length constraints on strings

#### Response Schemas
- `RoutePermissionRequestResponse`: Full response (35+ fields)
- `RoutePermissionRequestSummary`: Lightweight list view (9 fields)
- `PermissionRequestListResponse`: Paginated wrapper
- `AuditLogResponse`: Audit entry serialization
- `ErrorResponse`: Standardized error format

### 4. **Database Tables** ✓
**File:** `Traffic_Backend/navdrishti.db`

```sql
CREATE TABLE route_permission_requests (
    id INTEGER PRIMARY KEY,
    request_number VARCHAR(64) UNIQUE NOT NULL,
    citizen_name VARCHAR(255) NOT NULL,
    citizen_phone VARCHAR(20) NOT NULL,
    citizen_email VARCHAR(255),
    organization_name VARCHAR(255),
    event_type VARCHAR(10) NOT NULL,  -- Enum
    event_name VARCHAR(255) NOT NULL,
    event_description TEXT,
    expected_participants INTEGER CHECK (>= 0),
    vehicle_category VARCHAR(5),  -- Enum
    event_date DATETIME NOT NULL,
    event_start_time DATETIME NOT NULL,
    event_end_time DATETIME NOT NULL,
    route_geometry JSON NOT NULL,  -- GeoJSON
    route_length_km FLOAT,
    affected_area_km2 FLOAT,
    status VARCHAR(12) NOT NULL,  -- Enum: pending, under_review, ...
    submitted_date DATETIME NOT NULL,
    reviewed_date DATETIME,
    approved_date DATETIME,
    reviewed_by_user_id INTEGER FOREIGN KEY,
    reviewer_comments TEXT,
    rejection_reason TEXT,
    observation_started_date DATETIME,
    observation_completed_date DATETIME,
    baseline_traffic_summary JSON,
    alternative_routes_calculated INTEGER,
    alternative_routes_data JSON,
    live_monitoring_started DATETIME,
    max_congestion_score FLOAT,
    critical_alerts_count INTEGER,
    created_date DATETIME NOT NULL,
    updated_date DATETIME,
    CHECK (event_end_time > event_start_time),
    CHECK (expected_participants >= 0)
);

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    action VARCHAR(21) NOT NULL,  -- Enum
    action_description TEXT,
    user_id INTEGER FOREIGN KEY,
    user_role VARCHAR(64),
    timestamp DATETIME NOT NULL,
    permission_request_id INTEGER FOREIGN KEY,
    audit_metadata JSON
);
```

### 5. **Test Suite** ✓
**File:** `test_permission_requests.py`

**7 Comprehensive Tests:**
1. ✅ Submit valid request (> 5 days) → 201 Created
2. ✅ Reject invalid date (< 5 days) → 422 Validation Error
3. ✅ Reject invalid geometry (Point type) → 422 Validation Error
4. ✅ List all requests with pagination → 200 with summary list
5. ✅ Get single request by ID → 200 with full details
6. ✅ Get audit logs for request → 200 with chronological actions
7. ✅ Cancel pending request → 200 with confirmation

**Test Results:** ALL TESTS PASS ✓

---

## 🏗️ Architecture Integration

### Router Registration
**File:** `Traffic_Backend/main.py`

```python
from .routers.permission_requests import router as permission_requests_router
app.include_router(permission_requests_router, prefix="/api", tags=["Permission Requests"])
```

**Endpoints Available At:**
- `http://localhost:8002/api/permission-requests/`
- `http://localhost:8002/api/permission-requests/{id}`
- `http://localhost:8002/api/permission-requests/{id}/audit-logs`

### API Documentation
- **Swagger UI:** `http://localhost:8002/docs`
- **ReDoc:** `http://localhost:8002/redoc`
- All endpoints auto-documented with descriptions and examples

---

## 🔐 Governance Features Implemented

### 1. **5-Day Advance Constraint**
```python
@field_validator('event_date')
def validate_event_date_constraint(cls, v: datetime) -> datetime:
    now = datetime.utcnow()
    min_required_date = now + timedelta(days=5)
    if v < min_required_date:
        raise ValueError(f"Event must be at least 5 days from now...")
```

**Why:** Allows adequate time for:
- Governance review (Module 2)
- 48-hour observation baseline (Module 3)
- Intelligence analysis (Module 4)
- Live operations setup (Module 5)

### 2. **Audit Trail for Accountability**
Every action logged automatically:
- REQUEST_SUBMITTED: When citizen submits
- REQUEST_REVIEWED: When admin reviews (Module 2)
- REQUEST_APPROVED: When admin approves
- REQUEST_REJECTED: When admin rejects
- OBSERVATION_STARTED: When monitoring begins (Module 3)
- OBSERVATION_COMPLETED: When baseline collected
- ALTERNATIVE_ROUTES_CALCULATED: When routes computed (Module 4)
- LIVE_MONITORING_STARTED: When live ops begin (Module 5)

### 3. **Unique Request Numbers**
Format: `RPR-2025-XXXXXX` (Route Permission Request)
- Ensures every submission globally traceable
- Citizen-friendly reference
- No duplicates (UNIQUE constraint)

### 4. **Geometry Validation**
- Validates GeoJSON structure
- Restricts to LineString, Polygon, MultiLineString
- Rejects invalid geometry types (e.g., Point)
- Ensures spatial data consistency

### 5. **Comprehensive Request Metadata**
All submission data preserved for complete context:
- Who (citizen info)
- What (event details)
- When (temporal constraints)
- Where (route geometry)
- Why (event description)
- How many (expected participants)

---

## 📊 Data Flow

```
Citizen Submission
       ↓
   [Validation]
   - Date constraint (5+ days)
   - Time order (end > start)
   - Geometry validation
   - Required fields
       ↓
   [Processing]
   - Generate request_number
   - Calculate route metrics
   - Create RoutePermissionRequest
   - Create AuditLog entry (REQUEST_SUBMITTED)
       ↓
   [Database]
   - INSERT into route_permission_requests
   - INSERT into audit_logs
       ↓
   [Response]
   - 201 Created
   - Full request details
   - Request number for tracking
       ↓
   [Governance Queue]
   - Status: PENDING
   - Awaiting police admin review (Module 2)
```

---

## 🛠️ Utility Functions

### `generate_request_number()`
- Creates unique RPR-YYYY-NNNNNN format
- Checks for collisions in database
- Retries if collision detected

### `calculate_route_metrics(geometry)`
- Calculates route length (km) for LineString types
- Calculates affected area (km²) for Polygon types
- Returns None if calculation fails (graceful degradation)
- Uses Shapely geometry library

### `create_audit_log(db, action, permission_request_id, ...)`
- Helper function for audit entry creation
- Timestamps automatically
- Logs to both database and application log
- Supports metadata JSON for context

---

## 📁 File Structure

```
Traffic_Backend/
├── models.py                          [MODIFIED] +250 lines (enums, RoutePermissionRequest, AuditLog)
├── db_config.py                       [EXISTING] Database connection management
├── main.py                            [MODIFIED] +1 import, +1 router registration
├── init_permission_tables.py          [NEW] Table creation script
├── routers/
│   ├── __init__.py                    [NEW] Package marker
│   ├── permission_requests.py         [NEW] 414 lines (5 endpoints + utilities)
│   └── ...                            [EXISTING] Other routers
├── schemas/
│   ├── __init__.py                    [NEW] Package marker
│   └── permission_schemas.py          [NEW] 217 lines (Pydantic schemas + validators)
└── ...                                [EXISTING] Other files

test_permission_requests.py            [NEW] Comprehensive test suite
navdrishti.db                          [NEW] SQLite database with 2 tables
```

---

## 🚀 Quick Start

### 1. **Initialize Database Tables**
```bash
cd C:\Users\abhis\HSC_NavDrishti_AHM
python Traffic_Backend/init_permission_tables.py
```

### 2. **Start Backend (if not already running)**
```bash
# Backend already running on port 8002
http://localhost:8002
```

### 3. **Run Test Suite**
```bash
python test_permission_requests.py
```

### 4. **Submit Request (Manual)**
```bash
curl -X POST http://localhost:8002/api/permission-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "citizen_name": "John Doe",
    "citizen_phone": "+91-9876543210",
    "event_type": "rally",
    "event_name": "City Cleanup",
    "event_date": "2025-12-25T00:00:00",
    "event_start_time": "2025-12-25T10:00:00",
    "event_end_time": "2025-12-25T16:00:00",
    "vehicle_category": "mixed",
    "route_geometry": {
      "type": "LineString",
      "coordinates": [[72.5714, 23.0225], [72.5800, 23.0300]]
    }
  }'
```

### 5. **View API Documentation**
```
http://localhost:8002/docs
```

---

## ✨ Production Features

- ✅ **Type Safety:** Full Python type hints, Pydantic validation
- ✅ **Error Handling:** Comprehensive try-catch, detailed error messages
- ✅ **Logging:** Structured logging for diagnostics
- ✅ **Pagination:** Efficient list retrieval with page control
- ✅ **Validation:** 3+ custom validators + Pydantic field constraints
- ✅ **Audit Trail:** Complete action history for compliance
- ✅ **Constraints:** CHECK constraints + unique fields + relationships
- ✅ **Geospatial:** GeoJSON support for routes/areas
- ✅ **Status Tracking:** 8-state workflow for governance process
- ✅ **Extensibility:** Ready for Module 2-5 integration

---

## 📋 Next Steps (Modules 2-5)

### Module 2: Police Admin Approval Workflow
- Review submitted requests
- Approve/reject with comments
- Change status to UNDER_REVIEW → APPROVED/REJECTED

### Module 3: Observation Phase (48-hour baseline)
- Auto-collect baseline traffic for 48 hours
- Use Mapbox Traffic API for congestion data
- Store baseline_traffic_summary in database

### Module 4: Intelligence Layer (Alternative Routes)
- Calculate alternative routes using NetworkX
- Vehicle-type-aware routing
- Store alternative_routes_data with efficiency scores

### Module 5: Live Operations
- Real-time congestion monitoring
- Critical alert thresholds (if > 80% congestion)
- Dynamic rerouting recommendations
- Event wrap-up and analytics

---

## 📞 Support

**Test Results Location:** `test_permission_requests.py`  
**Database Location:** `navdrishti.db` (SQLite)  
**API Documentation:** `http://localhost:8002/docs`  
**Backend Logs:** Console output from `start_backend.ps1`

---

## ✅ Checklist

- ✅ Database models created (RoutePermissionRequest + AuditLog)
- ✅ Enums defined (RequestStatus, EventType, VehicleCategory, AuditAction)
- ✅ API endpoints implemented (POST, GET list, GET by ID, audit logs, DELETE)
- ✅ Validation schemas created with 3 custom validators
- ✅ 5-day advance constraint enforced
- ✅ Geometry validation working
- ✅ Audit logging implemented
- ✅ Unique request numbers generated
- ✅ Database tables created
- ✅ Router registered in main.py
- ✅ Error handling comprehensive
- ✅ Test suite created and passing
- ✅ Pagination implemented
- ✅ Documentation complete

---

**Implementation Date:** 2025-12-18  
**Status:** PRODUCTION READY  
**Module:** 1 of 5 (Governance-First Architecture)  
**All Tests:** PASSING ✅
