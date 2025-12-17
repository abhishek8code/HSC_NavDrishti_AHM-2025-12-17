"""
Route Permission Request Router - Module 1: Citizen Submission Layer
Implements governance-first submission with accountability logging.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import logging
import json

from Traffic_Backend.db_config import get_db
from Traffic_Backend.models import (
    RoutePermissionRequest, 
    AuditLog, 
    RequestStatus, 
    AuditAction
)
from Traffic_Backend.schemas.permission_schemas import (
    RoutePermissionRequestCreate,
    RoutePermissionRequestResponse,
    RoutePermissionRequestSummary,
    PermissionRequestListResponse,
    AuditLogResponse,
    ErrorResponse
)

# Configure logging
logger = logging.getLogger("permission_requests")
logger.setLevel(logging.INFO)

router = APIRouter(
    prefix="/permission-requests",
    tags=["Route Permission Requests"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
        400: {"model": ErrorResponse, "description": "Validation error"}
    }
)


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def generate_request_number() -> str:
    """Generate unique request number: RPR-YYYY-NNNNNN"""
    from datetime import datetime
    import random
    year = datetime.utcnow().year
    random_num = random.randint(100000, 999999)
    return f"RPR-{year}-{random_num:06d}"


def calculate_route_metrics(geometry: dict) -> tuple[Optional[float], Optional[float]]:
    """Calculate route length (km) and area (km²) from GeoJSON geometry"""
    try:
        import geojson
        from shapely.geometry import shape
        from shapely.ops import unary_union
        
        geom = shape(geometry)
        
        # Calculate length for LineString/MultiLineString
        length_km = None
        if geom.geom_type in ['LineString', 'MultiLineString']:
            # Approximate: 1 degree ≈ 111 km at equator
            length_km = geom.length * 111.0
        
        # Calculate area for Polygon/MultiPolygon
        area_km2 = None
        if geom.geom_type in ['Polygon', 'MultiPolygon']:
            # Convert to km² (approximate)
            area_km2 = geom.area * (111.0 ** 2)
        
        return length_km, area_km2
    
    except Exception as e:
        logger.warning(f"Error calculating route metrics: {e}")
        return None, None


def create_audit_log(
    db: Session,
    action: AuditAction,
    permission_request_id: int,
    user_id: Optional[int] = None,
    description: Optional[str] = None,
    audit_metadata: Optional[dict] = None
) -> AuditLog:
    """Create audit log entry for accountability"""
    audit_entry = AuditLog(
        action=action,
        action_description=description,
        user_id=user_id,
        permission_request_id=permission_request_id,
        audit_metadata=audit_metadata,
        timestamp=datetime.utcnow()
    )
    db.add(audit_entry)
    db.commit()
    logger.info(f"Audit log created: {action.value} for request {permission_request_id}")
    return audit_entry


# =====================================================
# API ENDPOINTS
# =====================================================

@router.post(
    "/",
    response_model=RoutePermissionRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit new route permission request",
    description=(
        "Citizen submits a route permission request for a public event. "
        "CONSTRAINT: Event date must be at least 5 days from now."
    )
)
async def create_permission_request(
    request_data: RoutePermissionRequestCreate,
    db: Session = Depends(get_db)
) -> RoutePermissionRequest:
    """
    Create new route permission request with validation and audit logging.
    
    **Governance Rules:**
    - Event must be > 5 days from now (validated in schema)
    - Geometry must be valid GeoJSON (LineString or Polygon)
    - Unique request number generated automatically
    - Initial status: PENDING
    - Audit log entry created automatically
    
    **Returns:** Full permission request object with assigned ID and request number.
    """
    try:
        # Generate unique request number
        request_number = generate_request_number()
        while db.query(RoutePermissionRequest).filter_by(request_number=request_number).first():
            request_number = generate_request_number()  # Retry if collision
        
        # Calculate route metrics
        length_km, area_km2 = calculate_route_metrics(request_data.route_geometry)
        
        # Create database record
        db_request = RoutePermissionRequest(
            request_number=request_number,
            citizen_name=request_data.citizen_name,
            citizen_phone=request_data.citizen_phone,
            citizen_email=request_data.citizen_email,
            organization_name=request_data.organization_name,
            event_type=request_data.event_type,
            event_name=request_data.event_name,
            event_description=request_data.event_description,
            expected_participants=request_data.expected_participants,
            vehicle_category=request_data.vehicle_category,
            event_date=request_data.event_date,
            event_start_time=request_data.event_start_time,
            event_end_time=request_data.event_end_time,
            route_geometry=request_data.route_geometry,
            route_length_km=length_km,
            affected_area_km2=area_km2,
            status=RequestStatus.PENDING,
            submitted_date=datetime.utcnow()
        )
        
        db.add(db_request)
        db.commit()
        db.refresh(db_request)
        
        # Create audit log entry (accountability)
        create_audit_log(
            db=db,
            action=AuditAction.REQUEST_SUBMITTED,
            permission_request_id=db_request.id,
            description=f"Citizen '{request_data.citizen_name}' submitted request for {request_data.event_type.value} event",
            audit_metadata={
                "event_name": request_data.event_name,
                "event_date": request_data.event_date.isoformat(),
                "expected_participants": request_data.expected_participants
            }
        )
        
        logger.info(
            f"✓ Permission request created: {db_request.request_number} "
            f"for {request_data.event_name} on {request_data.event_date.date()}"
        )
        
        return db_request
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating permission request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create request: {str(e)}"
        )


@router.get(
    "/",
    response_model=PermissionRequestListResponse,
    summary="List all permission requests",
    description="Retrieve paginated list of route permission requests with optional filters."
)
async def list_permission_requests(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[RequestStatus] = None,
    event_type_filter: Optional[str] = None,
    db: Session = Depends(get_db)
) -> dict:
    """
    List route permission requests with pagination and filtering.
    
    **Query Parameters:**
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - status_filter: Filter by request status
    - event_type_filter: Filter by event type
    
    **Returns:** Paginated list with total count and summary objects.
    """
    try:
        # Validate pagination
        if page < 1:
            raise HTTPException(status_code=400, detail="Page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise HTTPException(status_code=400, detail="Page size must be between 1 and 100")
        
        # Build query with filters
        query = db.query(RoutePermissionRequest)
        
        if status_filter:
            query = query.filter(RoutePermissionRequest.status == status_filter)
        
        if event_type_filter:
            query = query.filter(RoutePermissionRequest.event_type == event_type_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        requests = query.order_by(RoutePermissionRequest.submitted_date.desc()).offset(offset).limit(page_size).all()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "requests": requests
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing permission requests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve requests: {str(e)}"
        )


@router.get(
    "/{request_id}",
    response_model=RoutePermissionRequestResponse,
    summary="Get permission request by ID",
    description="Retrieve detailed information for a specific route permission request."
)
async def get_permission_request(
    request_id: int,
    db: Session = Depends(get_db)
) -> RoutePermissionRequest:
    """
    Get single permission request by ID.
    
    **Path Parameters:**
    - request_id: Unique request ID
    
    **Returns:** Full permission request details including geometry and audit trail.
    """
    try:
        db_request = db.query(RoutePermissionRequest).filter(RoutePermissionRequest.id == request_id).first()
        
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission request with ID {request_id} not found"
            )
        
        return db_request
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving permission request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve request: {str(e)}"
        )


@router.get(
    "/{request_id}/audit-logs",
    response_model=List[AuditLogResponse],
    summary="Get audit trail for request",
    description="Retrieve complete audit log history for accountability and transparency."
)
async def get_request_audit_logs(
    request_id: int,
    db: Session = Depends(get_db)
) -> List[AuditLog]:
    """
    Get audit log entries for a specific permission request.
    
    **Path Parameters:**
    - request_id: Unique request ID
    
    **Returns:** Chronological list of all actions taken on this request (governance accountability).
    """
    try:
        # Verify request exists
        db_request = db.query(RoutePermissionRequest).filter(RoutePermissionRequest.id == request_id).first()
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission request with ID {request_id} not found"
            )
        
        # Get audit logs
        logs = db.query(AuditLog).filter(
            AuditLog.permission_request_id == request_id
        ).order_by(AuditLog.timestamp.asc()).all()
        
        return logs
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving audit logs for request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audit logs: {str(e)}"
        )


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancel permission request",
    description="Citizen cancels their own request (only allowed if status is PENDING)."
)
async def cancel_permission_request(
    request_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """
    Cancel a pending permission request.
    
    **Business Rules:**
    - Only PENDING requests can be cancelled by citizen
    - Audit log entry created for accountability
    - Status changed to CANCELLED
    
    **Returns:** Confirmation message.
    """
    try:
        db_request = db.query(RoutePermissionRequest).filter(RoutePermissionRequest.id == request_id).first()
        
        if not db_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Permission request with ID {request_id} not found"
            )
        
        if db_request.status != RequestStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel request in '{db_request.status.value}' status. Only PENDING requests can be cancelled."
            )
        
        # Update status
        db_request.status = RequestStatus.CANCELLED
        db_request.updated_date = datetime.utcnow()
        db.commit()
        
        # Create audit log
        create_audit_log(
            db=db,
            action=AuditAction.REQUEST_CANCELLED,
            permission_request_id=request_id,
            description=f"Request {db_request.request_number} cancelled by citizen",
            audit_metadata={"cancelled_at": datetime.utcnow().isoformat()}
        )
        
        logger.info(f"✓ Request {db_request.request_number} cancelled")
        
        return {
            "message": "Permission request cancelled successfully",
            "request_number": db_request.request_number,
            "status": RequestStatus.CANCELLED.value
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error cancelling request {request_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel request: {str(e)}"
        )
