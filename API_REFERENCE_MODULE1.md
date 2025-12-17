# Module 1: Citizen Request Submission - API Reference

**Base URL:** `http://localhost:8002/api`

---

## 📝 Submit Permission Request

### `POST /permission-requests/`

Create a new route permission request for a public event.

**Status Code:** `201 Created`

#### Request Body
```json
{
  "citizen_name": "Rajesh Patel",
  "citizen_phone": "+91-9876543210",
  "citizen_email": "rajesh@example.com",
  "organization_name": "Traffic Society",
  "event_type": "rally",
  "event_name": "Clean Ahmedabad Marathon",
  "event_description": "Community cleanup drive",
  "expected_participants": 5000,
  "vehicle_category": "mixed",
  "event_date": "2025-12-25T00:00:00",
  "event_start_time": "2025-12-25T10:00:00",
  "event_end_time": "2025-12-25T16:00:00",
  "route_geometry": {
    "type": "LineString",
    "coordinates": [
      [72.5714, 23.0225],
      [72.5800, 23.0300],
      [72.5900, 23.0400]
    ]
  }
}
```

#### Field Specifications
| Field | Type | Required | Constraints | Example |
|-------|------|----------|-------------|---------|
| `citizen_name` | string | ✓ | 3-255 chars | "Rajesh Patel" |
| `citizen_phone` | string | ✓ | Phone format | "+91-9876543210" |
| `citizen_email` | string | | Email format | "rajesh@example.com" |
| `organization_name` | string | | Max 255 chars | "Traffic Society" |
| `event_type` | enum | ✓ | See options | "rally" |
| `event_name` | string | ✓ | 5-255 chars | "Marathon 2025" |
| `event_description` | string | | Max 2000 chars | "Community event..." |
| `expected_participants` | integer | | 1-1000000 | 5000 |
| `vehicle_category` | enum | ✓ | See options | "mixed" |
| `event_date` | datetime | ✓ | >= 5 days from now | "2025-12-25T00:00:00" |
| `event_start_time` | datetime | ✓ | Must be before end_time | "2025-12-25T10:00:00" |
| `event_end_time` | datetime | ✓ | Must be after start_time | "2025-12-25T16:00:00" |
| `route_geometry` | GeoJSON | ✓ | LineString/Polygon/MultiLineString | See GeoJSON spec |

#### Event Type Options
```
"rally"
"procession"
"marathon"
"protest"
"religious_gathering"
"cultural_event"
"sports_event"
"other"
```

#### Vehicle Category Options
```
"heavy"
"light"
"mixed"
```

#### Response - Success (201)
```json
{
  "id": 1,
  "request_number": "RPR-2025-235403",
  "status": "pending",
  "citizen_name": "Rajesh Patel",
  "citizen_phone": "+91-9876543210",
  "citizen_email": "rajesh@example.com",
  "organization_name": "Traffic Society",
  "event_type": "rally",
  "event_name": "Clean Ahmedabad Marathon",
  "event_description": "Community cleanup drive",
  "expected_participants": 5000,
  "vehicle_category": "mixed",
  "event_date": "2025-12-25T00:00:00",
  "event_start_time": "2025-12-25T10:00:00",
  "event_end_time": "2025-12-25T16:00:00",
  "route_geometry": { "type": "LineString", "coordinates": [...] },
  "route_length_km": 12.5,
  "affected_area_km2": null,
  "submitted_date": "2025-12-18T18:30:55.189068",
  "reviewed_date": null,
  "approved_date": null,
  "reviewed_by_user_id": null,
  "reviewer_comments": null,
  "rejection_reason": null,
  "observation_started_date": null,
  "observation_completed_date": null,
  "alternative_routes_calculated": 0,
  "max_congestion_score": null,
  "critical_alerts_count": 0,
  "created_date": "2025-12-18T18:30:55.189068",
  "updated_date": null
}
```

#### Response - Validation Error (422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "event_date"],
      "msg": "Value error, Event date must be at least 5 days from now. Your event is only 2 days away. Earliest allowed date: 2025-12-22",
      "input": "2025-12-20T18:30:55",
      "ctx": {"error": {}},
      "url": "https://errors.pydantic.dev/2.5/v/value_error"
    }
  ]
}
```

#### Validation Rules
1. **5-Day Constraint:** `event_date` must be ≥ now + 5 days
   - Error: Detailed message with days away and earliest allowed date
   
2. **Time Order:** `event_end_time` must be > `event_start_time`
   - Error: "Event end time must be after start time"
   
3. **Geometry:** Must be valid GeoJSON with type ∈ [LineString, Polygon, MultiLineString]
   - Error: "Geometry type must be one of: [...]"

---

## 📋 List Permission Requests

### `GET /permission-requests/`

Retrieve paginated list of all permission requests.

**Status Code:** `200 OK`

#### Query Parameters
| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number (1-indexed) |
| `page_size` | integer | 20 | 100 | Items per page |
| `status_filter` | enum | - | - | Filter by status (optional) |
| `event_type_filter` | string | - | - | Filter by event type (optional) |

#### Example Requests
```bash
# Get first 20 requests
GET /permission-requests/?page=1&page_size=20

# Get requests with pending status
GET /permission-requests/?status_filter=pending

# Get rally events with approved status
GET /permission-requests/?event_type_filter=rally&status_filter=approved

# Get page 2 with custom page size
GET /permission-requests/?page=2&page_size=50
```

#### Response - Success (200)
```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "requests": [
    {
      "id": 1,
      "request_number": "RPR-2025-235403",
      "status": "pending",
      "citizen_name": "Rajesh Patel",
      "event_type": "rally",
      "event_name": "Clean Ahmedabad Marathon",
      "event_date": "2025-12-25T00:00:00",
      "submitted_date": "2025-12-18T18:30:55.189068",
      "expected_participants": 5000
    },
    {
      "id": 2,
      "request_number": "RPR-2025-456789",
      "status": "approved",
      "citizen_name": "Priya Singh",
      "event_type": "procession",
      "event_name": "Cultural Festival Parade",
      "event_date": "2025-12-26T00:00:00",
      "submitted_date": "2025-12-17T10:15:22.123456",
      "expected_participants": 8000
    }
  ]
}
```

#### Status Filter Options
```
"pending"
"under_review"
"approved"
"rejected"
"observing"
"active"
"completed"
"cancelled"
```

---

## 🔍 Get Permission Request by ID

### `GET /permission-requests/{request_id}`

Retrieve detailed information for a specific request.

**Status Code:** `200 OK` (if found) | `404 Not Found` (if not found)

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `request_id` | integer | Unique request ID from creation |

#### Example Request
```bash
GET /permission-requests/1
```

#### Response - Success (200)
```json
{
  "id": 1,
  "request_number": "RPR-2025-235403",
  "status": "pending",
  "citizen_name": "Rajesh Patel",
  "citizen_phone": "+91-9876543210",
  "citizen_email": "rajesh@example.com",
  "organization_name": "Traffic Society",
  "event_type": "rally",
  "event_name": "Clean Ahmedabad Marathon",
  "event_description": "Community cleanup drive",
  "expected_participants": 5000,
  "vehicle_category": "mixed",
  "event_date": "2025-12-25T00:00:00",
  "event_start_time": "2025-12-25T10:00:00",
  "event_end_time": "2025-12-25T16:00:00",
  "route_geometry": {
    "type": "LineString",
    "coordinates": [[72.5714, 23.0225], [72.5800, 23.0300], [72.5900, 23.0400]]
  },
  "route_length_km": 12.5,
  "affected_area_km2": null,
  "submitted_date": "2025-12-18T18:30:55.189068",
  "reviewed_date": null,
  "approved_date": null,
  "reviewed_by_user_id": null,
  "reviewer_comments": null,
  "rejection_reason": null,
  "observation_started_date": null,
  "observation_completed_date": null,
  "alternative_routes_calculated": 0,
  "max_congestion_score": null,
  "critical_alerts_count": 0,
  "created_date": "2025-12-18T18:30:55.189068",
  "updated_date": null
}
```

#### Response - Not Found (404)
```json
{
  "detail": "Permission request with ID 999 not found"
}
```

---

## 📊 Get Audit Logs for Request

### `GET /permission-requests/{request_id}/audit-logs`

Retrieve complete audit trail for a permission request (governance transparency).

**Status Code:** `200 OK` (if found) | `404 Not Found` (if request not found)

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `request_id` | integer | Unique request ID |

#### Example Request
```bash
GET /permission-requests/1/audit-logs
```

#### Response - Success (200)
```json
[
  {
    "id": 1,
    "action": "request_submitted",
    "action_description": "Citizen 'Rajesh Patel' submitted request for rally event",
    "user_id": null,
    "user_role": null,
    "timestamp": "2025-12-18T18:30:55.189068",
    "permission_request_id": 1,
    "audit_metadata": {
      "event_name": "Clean Ahmedabad Marathon",
      "event_date": "2025-12-25T00:00:00",
      "expected_participants": 5000
    }
  },
  {
    "id": 2,
    "action": "request_reviewed",
    "action_description": "Police admin reviewed request",
    "user_id": 5,
    "user_role": "police_admin",
    "timestamp": "2025-12-18T19:00:00.000000",
    "permission_request_id": 1,
    "audit_metadata": {
      "reviewer_name": "Officer Singh",
      "comments": "Route approved for traffic management"
    }
  }
]
```

#### Audit Action Types
```
"request_submitted"
"request_reviewed"
"request_approved"
"request_rejected"
"observation_started"
"observation_completed"
"alternative_routes_calculated"
"live_monitoring_started"
```

---

## ❌ Cancel Permission Request

### `DELETE /permission-requests/{request_id}`

Cancel a pending permission request (citizen cancellation only).

**Status Code:** `200 OK` (if cancelled) | `404 Not Found` (if not found) | `400 Bad Request` (if not pending)

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `request_id` | integer | Unique request ID |

#### Example Request
```bash
DELETE /permission-requests/1
```

#### Response - Success (200)
```json
{
  "message": "Permission request cancelled successfully",
  "request_number": "RPR-2025-235403",
  "status": "cancelled"
}
```

#### Response - Not Found (404)
```json
{
  "detail": "Permission request with ID 999 not found"
}
```

#### Response - Cannot Cancel (400)
```json
{
  "detail": "Cannot cancel request in 'approved' status. Only PENDING requests can be cancelled."
}
```

#### Business Rules
- Only requests with status `pending` can be cancelled
- Cancellation creates audit log entry (REQUEST_CANCELLED)
- Status changed to `cancelled`
- Updated date is set to current timestamp

---

## 🚨 Error Responses

### Validation Error (422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "field_name"],
      "msg": "Error message here",
      "input": "provided_value",
      "ctx": {"error": {}},
      "url": "https://errors.pydantic.dev/2.5/v/value_error"
    }
  ]
}
```

### Not Found (404)
```json
{
  "detail": "Permission request with ID {id} not found"
}
```

### Business Logic Error (400)
```json
{
  "detail": "Cannot cancel request in '{status}' status. Only PENDING requests can be cancelled."
}
```

### Server Error (500)
```json
{
  "detail": "Failed to create request: {error_message}"
}
```

---

## 📌 Common Use Cases

### Submit a Marathon Event Request
```bash
curl -X POST http://localhost:8002/api/permission-requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "citizen_name": "Priya Sharma",
    "citizen_phone": "+91-9876543210",
    "citizen_email": "priya@example.com",
    "event_type": "marathon",
    "event_name": "Ahmedabad Marathon 2025",
    "event_description": "Annual city marathon event",
    "expected_participants": 10000,
    "vehicle_category": "mixed",
    "event_date": "2025-12-30T00:00:00",
    "event_start_time": "2025-12-30T06:00:00",
    "event_end_time": "2025-12-30T10:00:00",
    "route_geometry": {
      "type": "LineString",
      "coordinates": [
        [72.5714, 23.0225],
        [72.5750, 23.0250],
        [72.5800, 23.0300],
        [72.5850, 23.0350]
      ]
    }
  }'
```

### Check All Pending Requests
```bash
curl http://localhost:8002/api/permission-requests/?status_filter=pending&page_size=50
```

### Get Detailed Request Info
```bash
curl http://localhost:8002/api/permission-requests/5
```

### View Governance Trail
```bash
curl http://localhost:8002/api/permission-requests/5/audit-logs
```

### Cancel a Request
```bash
curl -X DELETE http://localhost:8002/api/permission-requests/5
```

---

## ℹ️ Additional Resources

- **Swagger UI:** `http://localhost:8002/docs`
- **ReDoc:** `http://localhost:8002/redoc`
- **Test Suite:** `test_permission_requests.py`
- **Full Documentation:** `MODULE1_COMPLETE.md`

---

**Last Updated:** 2025-12-18  
**Module:** 1 (Citizen Request Submission)  
**API Version:** 1.0
