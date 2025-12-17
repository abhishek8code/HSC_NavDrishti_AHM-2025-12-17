"""
Pydantic schemas for Route Permission Request module.
Handles request validation, response serialization, and business rules.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from Traffic_Backend.models import RequestStatus, EventType, VehicleCategory


# =====================================================
# REQUEST SCHEMAS (Input Validation)
# =====================================================

class RoutePermissionRequestCreate(BaseModel):
    """Citizen submission schema with 5+ day constraint validation"""
    
    # Citizen information
    citizen_name: str = Field(..., min_length=3, max_length=255, description="Full name of applicant")
    citizen_phone: str = Field(..., pattern=r'^\+?[\d\s\-()]{10,20}$', description="Valid phone number")
    citizen_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    organization_name: Optional[str] = Field(None, max_length=255)
    
    # Event details
    event_type: EventType = Field(..., description="Type of public event")
    event_name: str = Field(..., min_length=5, max_length=255, description="Name/title of event")
    event_description: Optional[str] = Field(None, max_length=2000)
    expected_participants: Optional[int] = Field(None, ge=1, le=1000000, description="Estimated crowd size")
    vehicle_category: VehicleCategory = Field(default=VehicleCategory.MIXED)
    
    # Temporal data (UTC timestamps)
    event_date: datetime = Field(..., description="Event date (must be > 5 days from submission)")
    event_start_time: datetime = Field(..., description="Event start time")
    event_end_time: datetime = Field(..., description="Event end time")
    
    # Spatial data (GeoJSON geometry)
    route_geometry: Dict[str, Any] = Field(..., description="GeoJSON LineString or Polygon")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('event_date')
    @classmethod
    def validate_event_date_constraint(cls, v: datetime) -> datetime:
        """
        GOVERNANCE RULE: Event must be > 5 days from now.
        This ensures adequate time for review and observation phase.
        """
        now = datetime.utcnow()
        min_required_date = now + timedelta(days=5)
        
        if v < min_required_date:
            days_from_now = (v - now).days
            raise ValueError(
                f"Event date must be at least 5 days from now. "
                f"Your event is only {days_from_now} days away. "
                f"Earliest allowed date: {min_required_date.date()}"
            )
        return v
    
    @field_validator('event_end_time')
    @classmethod
    def validate_event_time_order(cls, v: datetime, info) -> datetime:
        """Event end time must be after start time"""
        if 'event_start_time' in info.data and v <= info.data['event_start_time']:
            raise ValueError("Event end time must be after start time")
        return v
    
    @field_validator('route_geometry')
    @classmethod
    def validate_geometry(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GeoJSON geometry structure"""
        if not isinstance(v, dict):
            raise ValueError("route_geometry must be a GeoJSON object")
        
        if 'type' not in v or 'coordinates' not in v:
            raise ValueError("GeoJSON must have 'type' and 'coordinates' fields")
        
        allowed_types = ['LineString', 'Polygon', 'MultiLineString']
        if v['type'] not in allowed_types:
            raise ValueError(f"Geometry type must be one of: {allowed_types}")
        
        if not v['coordinates'] or len(v['coordinates']) == 0:
            raise ValueError("Geometry coordinates cannot be empty")
        
        return v


class RoutePermissionRequestUpdate(BaseModel):
    """Schema for updating request fields (limited to citizen-editable fields)"""
    event_name: Optional[str] = Field(None, min_length=5, max_length=255)
    event_description: Optional[str] = Field(None, max_length=2000)
    expected_participants: Optional[int] = Field(None, ge=1)
    citizen_phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-()]{10,20}$')
    citizen_email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# RESPONSE SCHEMAS (Output Serialization)
# =====================================================

class RoutePermissionRequestResponse(BaseModel):
    """Full response schema for permission request"""
    
    # Core identification
    id: int
    request_number: str
    status: RequestStatus
    
    # Citizen info
    citizen_name: str
    citizen_phone: str
    citizen_email: Optional[str]
    organization_name: Optional[str]
    
    # Event details
    event_type: EventType
    event_name: str
    event_description: Optional[str]
    expected_participants: Optional[int]
    vehicle_category: VehicleCategory
    
    # Temporal data
    event_date: datetime
    event_start_time: datetime
    event_end_time: datetime
    submitted_date: datetime
    reviewed_date: Optional[datetime]
    approved_date: Optional[datetime]
    
    # Spatial data
    route_geometry: Dict[str, Any]
    route_length_km: Optional[float]
    affected_area_km2: Optional[float]
    
    # Governance
    reviewed_by_user_id: Optional[int]
    reviewer_comments: Optional[str]
    rejection_reason: Optional[str]
    
    # Observation phase
    observation_started_date: Optional[datetime]
    observation_completed_date: Optional[datetime]
    
    # Intelligence & live ops
    alternative_routes_calculated: int
    max_congestion_score: Optional[float]
    critical_alerts_count: int
    
    # Metadata
    created_date: datetime
    updated_date: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RoutePermissionRequestSummary(BaseModel):
    """Lightweight summary for list views"""
    id: int
    request_number: str
    status: RequestStatus
    citizen_name: str
    event_type: EventType
    event_name: str
    event_date: datetime
    submitted_date: datetime
    expected_participants: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)


class PermissionRequestListResponse(BaseModel):
    """Paginated list response"""
    total: int
    page: int
    page_size: int
    requests: List[RoutePermissionRequestSummary]


# =====================================================
# AUDIT LOG SCHEMAS
# =====================================================

class AuditLogResponse(BaseModel):
    """Audit log entry for transparency"""
    id: int
    action: str
    action_description: Optional[str]
    user_id: Optional[int]
    user_role: Optional[str]
    timestamp: datetime
    permission_request_id: Optional[int]
    audit_metadata: Optional[Dict[str, Any]]
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# APPROVAL/REJECTION SCHEMAS (Module 2)
# =====================================================

class RequestApprovalSchema(BaseModel):
    """Schema for admin approval of requests"""
    approval_comments: Optional[str] = Field(None, max_length=1000, description="Optional approval comments")
    
    model_config = ConfigDict(from_attributes=True)


class RequestRejectionSchema(BaseModel):
    """Schema for admin rejection of requests"""
    rejection_reason: str = Field(..., min_length=10, max_length=500, description="Reason for rejection (required)")
    
    @field_validator('rejection_reason')
    @classmethod
    def validate_rejection_reason(cls, v: str) -> str:
        """Ensure rejection reason is meaningful"""
        if not v.strip() or len(v.strip()) < 10:
            raise ValueError("Rejection reason must be at least 10 characters and meaningful")
        return v
    
    model_config = ConfigDict(from_attributes=True)


class AdminDashboardSummary(BaseModel):
    """Summary statistics for admin dashboard"""
    total_pending: int
    total_under_review: int
    total_approved: int
    total_rejected: int
    pending_requests_summary: List[RoutePermissionRequestSummary]
    
    model_config = ConfigDict(from_attributes=True)


class ApprovalResponse(BaseModel):
    """Response after successful approval"""
    id: int
    request_number: str
    status: str
    message: str
    approved_date: datetime
    reviewer_comments: Optional[str]
    next_phase: str = "observation"
    
    model_config = ConfigDict(from_attributes=True)


class RejectionResponse(BaseModel):
    """Response after successful rejection"""
    id: int
    request_number: str
    status: str
    message: str
    reviewed_date: datetime
    rejection_reason: str
    
    model_config = ConfigDict(from_attributes=True)


# =====================================================
# ERROR RESPONSES
# =====================================================

class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: str
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationErrorDetail(BaseModel):
    """Detailed validation error"""
    field: str
    message: str
    invalid_value: Optional[Any] = None
