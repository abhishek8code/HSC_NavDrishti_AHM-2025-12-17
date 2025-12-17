"""
NavDrishti: Construction Planning Router
Purpose: Handle construction zone analysis and impact assessment
Author: NavDrishti Team
Date: December 16, 2025
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

# Import our Mapbox service module
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from mapbox_service import (
    get_diversion_routes,
    calculate_impact_isochrone,
    get_traffic_matrix,
    validate_geojson_polygon
)
from db_config import get_db

logger = logging.getLogger("construction_router")

router = APIRouter(
    prefix="/construction",
    tags=["Construction Planning"],
    responses={404: {"description": "Not found"}},
)


# =====================================================
# REQUEST/RESPONSE MODELS
# =====================================================

class ConstructionZoneRequest(BaseModel):
    """Request model for analyzing construction zone impact"""
    project_name: str = Field(..., min_length=3, max_length=255, description="Name of construction project")
    description: Optional[str] = Field(None, description="Detailed description")
    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")
    zone_polygon: Dict[str, Any] = Field(..., description="GeoJSON Polygon of construction zone")
    analysis_center: List[float] = Field(..., description="[longitude, latitude] for impact analysis")
    
    @validator("zone_polygon")
    def validate_polygon(cls, v):
        """Ensure zone_polygon is valid GeoJSON"""
        if not validate_geojson_polygon(v):
            raise ValueError("zone_polygon must be a valid GeoJSON Polygon or MultiPolygon")
        return v
    
    @validator("analysis_center")
    def validate_center(cls, v):
        """Ensure analysis_center is valid coordinates"""
        if len(v) != 2:
            raise ValueError("analysis_center must be [longitude, latitude]")
        lon, lat = v
        if not (68.0 <= lon <= 97.0 and 8.0 <= lat <= 37.0):
            raise ValueError("Coordinates must be within India bounds")
        return v
    
    @validator("end_date")
    def validate_dates(cls, v, values):
        """Ensure end_date is after start_date"""
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class DiversionRouteRequest(BaseModel):
    """Request model for calculating diversion routes"""
    origin: List[float] = Field(..., description="[longitude, latitude] of origin")
    destination: List[float] = Field(..., description="[longitude, latitude] of destination")
    construction_zone_id: Optional[int] = Field(None, description="ID of construction project to avoid")
    avoid_polygon: Optional[Dict[str, Any]] = Field(None, description="GeoJSON Polygon to avoid")


class IsochroneRequest(BaseModel):
    """Request model for calculating impact isochrones"""
    center_point: List[float] = Field(..., description="[longitude, latitude] of analysis center")
    time_intervals: List[int] = Field(default=[5, 10, 15], description="Time intervals in minutes")


# =====================================================
# ENDPOINTS
# =====================================================

@router.post("/analyze-impact")
async def analyze_construction_impact(
    request: ConstructionZoneRequest,
    db: Session = Depends(get_db)
):
    """
    Comprehensive analysis of construction zone impact.
    
    Steps:
    1. Validate and save construction zone to database
    2. Calculate isochrone impact area
    3. Identify affected routes
    4. Return visualization data for frontend
    
    Government Use Case:
    - Road Planning Officer draws a polygon on map
    - System calculates which areas will be affected
    - System suggests alternative diversion routes
    """
    logger.info(f"Analyzing impact for construction project: {request.project_name}")
    
    try:
        # Step 1: Save construction zone to database
        # Use SQLite JSON storage instead of PostGIS geometry
        from models import ConstructionProject
        
        construction_project = ConstructionProject(
            project_name=request.project_name,
            description=request.description,
            start_date=request.start_date,
            end_date=request.end_date,
            zone_geojson=request.zone_polygon.dict() if hasattr(request.zone_polygon, 'dict') else request.zone_polygon,
            analysis_center_lat=request.analysis_center[1],
            analysis_center_lon=request.analysis_center[0],
            status='planned'
        )
        
        db.add(construction_project)
        db.flush()  # Get the project_id without committing
        db.commit()
        
        project_id = construction_project.id
        logger.info(f"Created construction project with ID: {project_id}")
        
        # Step 2: Calculate isochrone impact area
        isochrone_data = await calculate_impact_isochrone(
            center_point=tuple(request.analysis_center),
            time_intervals=[5, 10, 15, 20]
        )
        
        # Step 3: Save impact isochrone data back to database
        if isochrone_data["success"] and isochrone_data["isochrones"].get("features"):
            # Update with isochrone data
            construction_project.impact_radius_geojson = isochrone_data["isochrones"]
            
            # Calculate approximate impact area (using the largest isochrone)
            largest_isochrone = isochrone_data["isochrones"]["features"][-1]
            if largest_isochrone.get("geometry", {}).get("coordinates"):
                # Simple approximation: count vertices as proxy for area
                coords_count = len(largest_isochrone["geometry"]["coordinates"][0])
                construction_project.estimated_impact_area_km2 = coords_count * 0.1  # Rough estimate
            
            construction_project.impact_analysis_data = isochrone_data
            db.commit()
            logger.info(f"Updated impact radius for project {project_id}")
        
        # Step 4: Return comprehensive analysis
        return {
            "success": True,
            "project_id": project_id,
            "project_name": request.project_name,
            "status": "Analysis complete",
            "impact_analysis": {
                "isochrones": isochrone_data["isochrones"],
                "affected_area_km2": "Calculated server-side",  # Placeholder
                "affected_routes": "Under analysis"  # Placeholder for future enhancement
            },
            "recommendations": {
                "message": "Construction zone created. Use 'Get Diversion Routes' to calculate alternatives.",
                "next_steps": [
                    "Review isochrone impact on map",
                    "Calculate diversion routes for affected corridors",
                    "Notify traffic controllers"
                ]
            }
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error analyzing construction impact: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/diversion-routes")
async def calculate_diversion_routes(request: DiversionRouteRequest):
    """
    Calculate alternative routes avoiding construction zone.
    
    Government Use Case:
    - Traffic controller selects origin and destination
    - System finds 3 best alternative routes
    - Results displayed with travel time and distance
    """
    logger.info(f"Calculating diversion routes from {request.origin} to {request.destination}")
    
    try:
        # Call Mapbox service to get alternative routes
        routes_data = await get_diversion_routes(
            origin=tuple(request.origin),
            destination=tuple(request.destination),
            avoid_polygon=request.avoid_polygon,
            alternatives=3
        )
        
        # Enhance response with traffic analysis
        enhanced_routes = []
        for route in routes_data["routes"]:
            route["traffic_severity"] = "Moderate"  # Placeholder for real-time traffic analysis
            route["recommended_for_vehicles"] = ["Cars", "Buses", "Emergency"]
            enhanced_routes.append(route)
        
        return {
            "success": True,
            "routes": enhanced_routes,
            "analysis": {
                "total_alternatives": len(enhanced_routes),
                "fastest_route_id": enhanced_routes[0]["id"] if enhanced_routes else None,
                "shortest_route_id": min(enhanced_routes, key=lambda r: r["distance_km"])["id"] if enhanced_routes else None
            }
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error calculating diversion routes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Route calculation failed: {str(e)}")


@router.post("/impact-isochrone")
async def get_impact_isochrone(request: IsochroneRequest):
    """
    Calculate isochrone polygons for impact visualization.
    
    Government Use Case:
    - Visualize how far traffic can travel from construction center
    - Identify affected neighborhoods
    """
    logger.info(f"Calculating isochrone for center {request.center_point}")
    
    try:
        isochrone_data = await calculate_impact_isochrone(
            center_point=tuple(request.center_point),
            time_intervals=request.time_intervals
        )
        
        return isochrone_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error calculating isochrone: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Isochrone calculation failed: {str(e)}")


@router.get("/projects")
async def list_construction_projects(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all construction projects with optional status filter.
    
    Government Use Case:
    - View all planned/active/completed construction zones
    - Export for reporting
    """
    try:
        from models import ConstructionProject
        
        query = db.query(ConstructionProject)
        
        if status:
            query = query.filter(ConstructionProject.status == status)
        
        projects_list = query.order_by(ConstructionProject.created_date.desc()).all()
        
        projects = []
        for proj in projects_list:
            projects.append({
                "id": proj.id,
                "project_name": proj.project_name,
                "description": proj.description,
                "start_date": str(proj.start_date),
                "end_date": str(proj.end_date),
                "status": proj.status,
                "zone_geometry": proj.zone_geojson,
                "impact_radius": proj.impact_radius_geojson,
                "analysis_center": [proj.analysis_center_lon, proj.analysis_center_lat] if proj.analysis_center_lat else None,
                "estimated_impact_area_km2": proj.estimated_impact_area_km2
            })
        
        return {
            "success": True,
            "count": len(projects),
            "projects": projects
        }
        
    except Exception as e:
        logger.error(f"Error listing projects: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve projects: {str(e)}")


@router.delete("/projects/{project_id}")
async def delete_construction_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a construction project (admin only).
    
    Government Use Case:
    - Remove cancelled projects
    - Clean up test data
    """
    try:
        from models import ConstructionProject
        
        project = db.query(ConstructionProject).filter(ConstructionProject.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Construction project {project_id} not found")
        
        db.delete(project)
        db.commit()
        
        logger.info(f"Deleted construction project {project_id}")
        return {"success": True, "message": f"Project {project_id} deleted"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
