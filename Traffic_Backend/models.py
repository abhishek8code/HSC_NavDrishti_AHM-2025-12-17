from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

# =====================================================
# ENUMS FOR GOVERNANCE MODULE
# =====================================================

class RequestStatus(str, enum.Enum):
    """Status of route permission request - governance workflow"""
    PENDING = "pending"           # Citizen submitted, awaiting admin review
    UNDER_REVIEW = "under_review"  # Admin is reviewing
    APPROVED = "approved"         # Admin approved, observation phase starts
    REJECTED = "rejected"         # Admin rejected
    OBSERVING = "observing"       # 48-hour baseline monitoring in progress
    ACTIVE = "active"             # Event day - live monitoring
    COMPLETED = "completed"       # Event finished
    CANCELLED = "cancelled"       # Citizen cancelled

class EventType(str, enum.Enum):
    """Type of public event requiring route permission"""
    RALLY = "rally"               # Political rally
    PROCESSION = "procession"     # Religious/cultural procession
    MARATHON = "marathon"         # Sports event
    PROTEST = "protest"           # Peaceful demonstration
    PARADE = "parade"             # Festival/celebration parade
    FUNERAL = "funeral"           # Large funeral procession
    WEDDING = "wedding"           # Wedding procession
    OTHER = "other"               # Other public gathering

class VehicleCategory(str, enum.Enum):
    """Vehicle type for route calculation - intelligence layer"""
    HEAVY = "heavy"               # Heavy vehicles (trucks, buses) - need wide roads
    LIGHT = "light"               # Light vehicles (cars, bikes) - prioritize speed
    MIXED = "mixed"               # Mixed traffic

class AuditAction(str, enum.Enum):
    """Audit log action types for accountability"""
    REQUEST_SUBMITTED = "request_submitted"
    REQUEST_REVIEWED = "request_reviewed"
    REQUEST_APPROVED = "request_approved"
    REQUEST_REJECTED = "request_rejected"
    OBSERVATION_STARTED = "observation_started"
    OBSERVATION_COMPLETED = "observation_completed"
    ALERT_TRIGGERED = "alert_triggered"
    REQUEST_CANCELLED = "request_cancelled"

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    start_lat = Column(Float)
    start_lon = Column(Float)
    end_lat = Column(Float)
    end_lon = Column(Float)
    resource_allocation = Column(Text)
    emission_reduction_estimate = Column(Float)
    road_segment_id = Column(Integer, ForeignKey('road_network.id'))
    road_segment = relationship('RoadNetwork')

class RoadNetwork(Base):
    __tablename__ = 'road_network'
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    geometry = Column(Text)  # WKT or GeoJSON
    base_capacity = Column(Integer)
    roughness_index = Column(Float)

class TrafficDynamics(Base):
    __tablename__ = 'traffic_dynamics'
    id = Column(Integer, primary_key=True)
    road_segment_id = Column(Integer, ForeignKey('road_network.id'))
    timestamp = Column(DateTime)
    flow_entropy = Column(Float)
    congestion_state = Column(String(32))
    vehicle_count = Column(Integer)
    average_speed = Column(Float)
    road_segment = relationship('RoadNetwork')

class DamageCluster(Base):
    __tablename__ = 'damage_clusters'
    id = Column(Integer, primary_key=True)
    centroid_lat = Column(Float)
    centroid_lon = Column(Float)
    avg_severity = Column(Float)
    count = Column(Integer)
    road_segment_id = Column(Integer, ForeignKey('road_network.id'))
    road_segment = relationship('RoadNetwork')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    roles = Column(String(255), default='')  # comma-separated roles


class Notification(Base):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    recipient_type = Column(String(32), nullable=False)  # 'admin' or 'public'
    message = Column(Text, nullable=False)
    template = Column(String(128), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    delivery_status = Column(String(32), default='sent')


class TrafficThreshold(Base):
    __tablename__ = 'traffic_thresholds'
    id = Column(Integer, primary_key=True)
    road_segment_id = Column(Integer, ForeignKey('road_network.id'), nullable=False)
    vehicle_count_limit = Column(Integer, nullable=True)
    density_limit = Column(Float, nullable=True)
    alert_type = Column(String(32), nullable=True)
    is_active = Column(Integer, default=1)


class Vehicle(Base):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(String(64), unique=True, nullable=False)
    vehicle_type = Column(String(32), nullable=False)  # 'bus', 'truck', 'emergency', 'patrol'
    driver_name = Column(String(128), nullable=True)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    status = Column(String(32), default='active')  # 'active', 'idle', 'offline'
    speed = Column(Float, nullable=True)  # km/h
    heading = Column(Float, nullable=True)  # degrees
    last_update = Column(DateTime, nullable=True)
    registration_date = Column(DateTime, nullable=False)


class ConstructionProject(Base):
    __tablename__ = 'construction_projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(32), default='planned')  # 'planned', 'active', 'completed'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Store GeoJSON as JSON instead of PostGIS geometry
    zone_geojson = Column(JSON, nullable=False)  # Polygon GeoJSON
    impact_radius_geojson = Column(JSON, nullable=True)  # Isochrone FeatureCollection
    analysis_center_lat = Column(Float, nullable=True)
    analysis_center_lon = Column(Float, nullable=True)
    estimated_impact_area_km2 = Column(Float, nullable=True)
    affected_roads_count = Column(Integer, nullable=True)
    impact_analysis_data = Column(JSON, nullable=True)  # Full isochrone data


# =====================================================
# GOVERNANCE-FIRST TRAFFIC PERMISSION MODULE
# =====================================================

class RoutePermissionRequest(Base):
    """Citizen route permission requests for public events - Module 1"""
    __tablename__ = 'route_permission_requests'
    
    # Primary identification
    id = Column(Integer, primary_key=True)
    request_number = Column(String(64), unique=True, nullable=False)  # e.g., RPR-2025-001234
    
    # Citizen information
    citizen_name = Column(String(255), nullable=False)
    citizen_phone = Column(String(20), nullable=False)
    citizen_email = Column(String(255), nullable=True)
    organization_name = Column(String(255), nullable=True)  # Optional: organizing body
    
    # Event details
    event_type = Column(SQLEnum(EventType), nullable=False)
    event_name = Column(String(255), nullable=False)
    event_description = Column(Text, nullable=True)
    expected_participants = Column(Integer, nullable=True)  # Estimated crowd size
    vehicle_category = Column(SQLEnum(VehicleCategory), default=VehicleCategory.MIXED)
    
    # Temporal constraints (5+ day validation in API layer)
    event_date = Column(DateTime, nullable=False)
    event_start_time = Column(DateTime, nullable=False)
    event_end_time = Column(DateTime, nullable=False)
    
    # Spatial data (GeoJSON format for interoperability)
    route_geometry = Column(JSON, nullable=False)  # LineString or Polygon GeoJSON
    route_length_km = Column(Float, nullable=True)  # Calculated length
    affected_area_km2 = Column(Float, nullable=True)  # For polygon events
    
    # Workflow status
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING, nullable=False)
    submitted_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_date = Column(DateTime, nullable=True)
    approved_date = Column(DateTime, nullable=True)
    
    # Governance layer
    reviewed_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewer_comments = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Observation phase tracking (Module 3)
    observation_started_date = Column(DateTime, nullable=True)
    observation_completed_date = Column(DateTime, nullable=True)
    baseline_traffic_summary = Column(JSON, nullable=True)  # Aggregated baseline data
    
    # Intelligence layer (Module 4)
    alternative_routes_calculated = Column(Integer, default=0)  # Count of alternatives
    alternative_routes_data = Column(JSON, nullable=True)  # Stored route options
    
    # Live ops tracking (Module 5)
    live_monitoring_started = Column(DateTime, nullable=True)
    max_congestion_score = Column(Float, nullable=True)  # Highest recorded score
    critical_alerts_count = Column(Integer, default=0)
    
    # Audit & metadata
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviewer = relationship('User', foreign_keys=[reviewed_by_user_id])
    audit_logs = relationship('AuditLog', back_populates='permission_request', cascade='all, delete-orphan')
    
    # Table-level constraints
    __table_args__ = (
        CheckConstraint('event_end_time > event_start_time', name='check_event_time_order'),
        CheckConstraint('expected_participants >= 0', name='check_participants_positive'),
    )


class AuditLog(Base):
    """Comprehensive audit trail for governance accountability"""
    __tablename__ = 'audit_logs'
    
    id = Column(Integer, primary_key=True)
    
    # What happened
    action = Column(SQLEnum(AuditAction), nullable=False)
    action_description = Column(Text, nullable=True)  # Human-readable details
    
    # Who did it
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # NULL for system actions
    user_role = Column(String(64), nullable=True)  # Role at time of action
    
    # When
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Context
    permission_request_id = Column(Integer, ForeignKey('route_permission_requests.id'), nullable=True)
    
    # Additional metadata (e.g., IP address, browser, API endpoint)
    # NOTE: 'metadata' is reserved in SQLAlchemy - using 'audit_metadata' instead
    audit_metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    permission_request = relationship('RoutePermissionRequest', back_populates='audit_logs')

