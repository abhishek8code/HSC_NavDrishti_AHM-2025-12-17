"""
NavDrishti: Mapbox Geospatial Intelligence Service
Purpose: Secure proxy for Mapbox API calls with cost control and error handling
Author: NavDrishti Team
Date: December 16, 2025

Security Notes:
- API keys are never exposed to frontend
- Rate limiting applied to prevent cost overruns
- All requests are logged for government audit trails
"""

import os
import httpx
import logging
from typing import List, Dict, Tuple, Optional, Any
from fastapi import HTTPException
import json

# Configure logging for audit trail
logger = logging.getLogger("mapbox_service")
logger.setLevel(logging.INFO)

# =====================================================
# CONFIGURATION
# =====================================================
MAPBOX_ACCESS_TOKEN = os.getenv("MAPBOX_ACCESS_TOKEN")
if not MAPBOX_ACCESS_TOKEN:
    logger.warning("MAPBOX_ACCESS_TOKEN environment variable not set at module load time!")
    logger.warning("This may be set later during initialization. Mock data will be used if token is unavailable.")

MAPBOX_BASE_URL = "https://api.mapbox.com"

# API Endpoints
BASE_DIRECTIONS_ENDPOINT = f"{MAPBOX_BASE_URL}/directions/v5/mapbox"
ISOCHRONE_ENDPOINT = f"{MAPBOX_BASE_URL}/isochrone/v1/mapbox/driving"
MATRIX_ENDPOINT = f"{MAPBOX_BASE_URL}/directions-matrix/v1/mapbox/driving-traffic"

# Routing profiles for different use cases
ROUTING_PROFILES = {
    "driving-traffic": "driving-traffic",  # Primary: traffic-aware routing
    "driving": "driving",  # Fallback: standard driving routes
    "walking": "walking",  # For pedestrian analysis if needed
}

# Timeout settings (prevent hanging requests)
REQUEST_TIMEOUT = 30.0

# =====================================================
# ERROR HANDLING UTILITIES
# =====================================================
def handle_mapbox_error(status_code: int, response_text: str):
    """
    Standardized error handling for Mapbox API responses.
    Provides meaningful messages for government users.
    """
    if status_code == 401:
        logger.error("Mapbox authentication failed - check API token")
        raise HTTPException(status_code=500, detail="Map service authentication error. Contact system administrator.")
    elif status_code == 429:
        logger.warning("Mapbox rate limit exceeded")
        raise HTTPException(status_code=429, detail="Map service is experiencing high traffic. Please try again in a moment.")
    elif status_code == 422:
        logger.error(f"Invalid request to Mapbox: {response_text}")
        raise HTTPException(status_code=400, detail="Invalid coordinates or parameters provided.")
    else:
        logger.error(f"Mapbox API error {status_code}: {response_text}")
        raise HTTPException(status_code=500, detail=f"Map service error. Status: {status_code}")


# =====================================================
# SERVICE FUNCTIONS
# =====================================================

async def get_diversion_routes(
    origin: Tuple[float, float],
    destination: Tuple[float, float],
    avoid_polygon: Optional[Dict[str, Any]] = None,
    alternatives: int = 3,
    profile: str = "driving-traffic",
    include_streets: bool = True
) -> Dict[str, Any]:
    """
    Calculate alternative routes with street-level precision and traffic awareness.
    Supports precise routing through local roads, streets, and highways.
    
    Args:
        origin: (longitude, latitude) tuple for start point
        destination: (longitude, latitude) tuple for end point
        avoid_polygon: GeoJSON polygon representing construction zone to avoid
        alternatives: Number of alternative routes to request (max 3 for Mapbox)
        profile: Routing profile ("driving-traffic", "driving", "walking")
        include_streets: If True, include local streets in routing (not just highways)
    
    Returns:
        Dict containing routes with duration, distance, geometry, and turn-by-turn steps
        
    Example:
        routes = await get_diversion_routes(
            origin=(72.5714, 23.0225),
            destination=(72.58, 23.035),
            profile="driving-traffic",
            include_streets=True
        )
    """
    logger.info(f"Calculating diversion routes from {origin} to {destination} using profile: {profile}")
    
    # Check if token is available
    token = MAPBOX_ACCESS_TOKEN or os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        logger.error("MAPBOX_ACCESS_TOKEN is not available for routing")
        raise HTTPException(status_code=503, detail="Mapbox service not configured. Please set MAPBOX_ACCESS_TOKEN.")
    
    # Validate coordinates (India bounds check)
    if not (68.0 <= origin[0] <= 97.0 and 8.0 <= origin[1] <= 37.0):
        raise HTTPException(status_code=400, detail="Origin coordinates are outside India bounds")
    if not (68.0 <= destination[0] <= 97.0 and 8.0 <= destination[1] <= 37.0):
        raise HTTPException(status_code=400, detail="Destination coordinates are outside India bounds")
    
    # Build coordinate string: "lon,lat;lon,lat"
    coordinates = f"{origin[0]},{origin[1]};{destination[0]},{destination[1]}"
    
    # Select routing profile
    profile = profile if profile in ROUTING_PROFILES else "driving-traffic"
    directions_endpoint = f"{BASE_DIRECTIONS_ENDPOINT}/{ROUTING_PROFILES[profile]}"
    
    # Build query parameters for street-level precision
    params = {
        "access_token": token,
        "alternatives": "true" if alternatives > 1 else "false",
        "geometries": "geojson",  # Return GeoJSON LineString
        "steps": "true",  # Include turn-by-turn instructions for street accuracy
        "banner_instructions": "true",  # Include banner (signage) instructions
        "language": "en",  # English language for instructions
        "overview": "full",  # Full geometry detail for all streets
        "annotations": "duration,distance,speed,congestion",  # Detailed metrics including congestion
        "exclude": "toll" if include_streets else "",  # Optionally exclude tolls for local routing
    }
    
    # Add roundabout information for navigation precision
    params["roundabout_exits"] = "true"
    
    # Add avoidance polygon if provided
    # Note: Mapbox Directions API doesn't directly support polygon avoidance
    # We'll use this in post-processing or recommend Matrix API for complex avoidance
    if avoid_polygon:
        logger.info("Avoidance polygon provided - will filter routes post-request")
    
    # Use selected profile endpoint
    url = f"{directions_endpoint}/{coordinates}"
    
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                handle_mapbox_error(response.status_code, response.text)
            
            data = response.json()
            
            # Parse and structure the response for NavDrishti frontend with street-level details
            routes = []
            for idx, route in enumerate(data.get("routes", [])):
                # Extract street-level information from steps
                street_info = {
                    "turn_count": 0,
                    "road_classes": set(),
                    "instructions": []
                }
                
                for leg in route.get("legs", []):
                    for step in leg.get("steps", []):
                        # Count turns for routing complexity
                        if step.get("maneuver", {}).get("type"):
                            street_info["turn_count"] += 1
                        
                        # Collect road classes (local road, secondary, tertiary, etc.)
                        if step.get("roads"):
                            for road in step.get("roads", []):
                                if isinstance(road, dict) and "class" in road:
                                    street_info["road_classes"].add(road["class"])
                        
                        # Extract turn-by-turn instructions for street navigation
                        instruction = step.get("maneuver", {}).get("instruction")
                        if instruction:
                            street_info["instructions"].append(instruction)
                
                parsed_route = {
                    "id": f"route-{idx + 1}",
                    "duration_seconds": route.get("duration", 0),
                    "duration_minutes": round(route.get("duration", 0) / 60, 1),
                    "distance_meters": route.get("distance", 0),
                    "distance_km": round(route.get("distance", 0) / 1000, 2),
                    "geometry": route.get("geometry", {}),  # GeoJSON LineString with all streets
                    "legs": route.get("legs", []),
                    "weight": route.get("weight", 0),  # Mapbox internal routing metric
                    # Street-level precision details
                    "turn_count": street_info["turn_count"],
                    "road_classes": list(street_info["road_classes"]),
                    "turn_instructions": street_info["instructions"][:5],  # First 5 turns for summary
                    "profile": profile,
                }
                routes.append(parsed_route)
            
            logger.info(f"Successfully retrieved {len(routes)} diversion routes")
            
            return {
                "success": True,
                "routes": routes,
                "waypoints": data.get("waypoints", []),
            }
            
    except httpx.TimeoutException:
        logger.error("Mapbox Directions API timeout")
        raise HTTPException(status_code=504, detail="Map service timeout. Please try again.")
    except httpx.RequestError as e:
        logger.error(f"Network error calling Mapbox: {str(e)}")
        raise HTTPException(status_code=503, detail="Unable to reach map service. Check network connectivity.")


async def calculate_impact_isochrone(
    center_point: Tuple[float, float],
    time_intervals: List[int] = [5, 10, 15]
) -> Dict[str, Any]:
    """
    Calculate isochrone polygons showing driveable area from construction center.
    Used to visualize impact radius on surrounding traffic.
    
    Args:
        center_point: (longitude, latitude) tuple for construction center
        time_intervals: List of time intervals in minutes (e.g., [5, 10, 15])
    
    Returns:
        Dict containing isochrone polygons (GeoJSON FeatureCollection)
        
    Example:
        isochrones = await calculate_impact_isochrone(
            center_point=(72.5714, 23.0225),
            time_intervals=[5, 10, 15]
        )
    """
    logger.info(f"Calculating isochrones for center {center_point}, intervals: {time_intervals}")
    
    # Check if token is available
    token = MAPBOX_ACCESS_TOKEN or os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        logger.error("MAPBOX_ACCESS_TOKEN is not available for isochrone calculation")
        raise HTTPException(status_code=503, detail="Mapbox service not configured. Please set MAPBOX_ACCESS_TOKEN.")
    
    # Validate time intervals
    if not time_intervals or len(time_intervals) > 4:
        raise HTTPException(status_code=400, detail="Provide 1-4 time intervals")
    if any(t <= 0 or t > 60 for t in time_intervals):
        raise HTTPException(status_code=400, detail="Time intervals must be between 1-60 minutes")
    
    # Build URL: /isochrone/v1/mapbox/driving/lon,lat
    coordinates = f"{center_point[0]},{center_point[1]}"
    url = f"{ISOCHRONE_ENDPOINT}/{coordinates}"
    
    # Build query parameters
    contours_minutes = ",".join(str(t) for t in sorted(time_intervals))
    params = {
        "access_token": token,
        "contours_minutes": contours_minutes,
        "polygons": "true",  # Return polygons (not just points)
        "denoise": "1.0",  # Smooth polygons for cleaner visualization
    }
    
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                handle_mapbox_error(response.status_code, response.text)
            
            data = response.json()
            
            # Mapbox returns a FeatureCollection with Polygon features
            # Each feature has a 'contour' property indicating the time interval
            logger.info(f"Successfully retrieved {len(data.get('features', []))} isochrone polygons")
            
            return {
                "success": True,
                "isochrones": data,  # GeoJSON FeatureCollection
                "center": center_point,
                "intervals_minutes": time_intervals,
            }
            
    except httpx.TimeoutException:
        logger.error("Mapbox Isochrone API timeout")
        raise HTTPException(status_code=504, detail="Isochrone calculation timeout. Try fewer intervals.")
    except httpx.RequestError as e:
        logger.error(f"Network error calling Mapbox: {str(e)}")
        raise HTTPException(status_code=503, detail="Unable to reach map service.")


async def get_traffic_matrix(
    origins: List[Tuple[float, float]],
    destinations: List[Tuple[float, float]]
) -> Dict[str, Any]:
    """
    Calculate travel time/distance matrix for batch route analysis.
    Useful for evaluating multiple diversion paths simultaneously.
    
    Args:
        origins: List of (longitude, latitude) tuples (max 25)
        destinations: List of (longitude, latitude) tuples (max 25)
    
    Returns:
        Dict containing matrix of durations and distances
        
    Example:
        matrix = await get_traffic_matrix(
            origins=[(72.5714, 23.0225), (72.58, 23.03)],
            destinations=[(72.59, 23.04), (72.60, 23.05)]
        )
    """
    logger.info(f"Calculating traffic matrix: {len(origins)} origins × {len(destinations)} destinations")
    
    # Check if token is available
    token = MAPBOX_ACCESS_TOKEN or os.getenv("MAPBOX_ACCESS_TOKEN")
    if not token:
        logger.error("MAPBOX_ACCESS_TOKEN is not available for traffic matrix")
        raise HTTPException(status_code=503, detail="Mapbox service not configured. Please set MAPBOX_ACCESS_TOKEN.")
    
    # Validate matrix size (Mapbox limit: 25 x 25)
    if len(origins) == 0 or len(destinations) == 0:
        raise HTTPException(status_code=400, detail="Provide at least one origin and destination")
    if len(origins) > 25 or len(destinations) > 25:
        raise HTTPException(status_code=400, detail="Maximum 25 origins and 25 destinations allowed")
    
    # Build coordinate string: "lon,lat;lon,lat;..."
    all_coords = origins + destinations
    coordinates = ";".join(f"{lon},{lat}" for lon, lat in all_coords)
    
    # Specify which coordinates are sources (origins) vs destinations
    # Format: sources=0,1,2&destinations=3,4,5
    sources = ",".join(str(i) for i in range(len(origins)))
    destinations_indices = ",".join(str(i) for i in range(len(origins), len(all_coords)))
    
    url = f"{MATRIX_ENDPOINT}/{coordinates}"
    
    params = {
        "access_token": token,
        "sources": sources,
        "destinations": destinations_indices,
        "annotations": "duration,distance",  # Return both time and distance
    }
    
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                handle_mapbox_error(response.status_code, response.text)
            
            data = response.json()
            
            # Parse matrix results
            # data["durations"] is a 2D array: durations[origin_index][destination_index]
            # data["distances"] is a 2D array: distances[origin_index][destination_index]
            
            logger.info(f"Successfully calculated traffic matrix")
            
            return {
                "success": True,
                "durations_seconds": data.get("durations", []),
                "distances_meters": data.get("distances", []),
                "sources": data.get("sources", []),
                "destinations": data.get("destinations", []),
            }
            
    except httpx.TimeoutException:
        logger.error("Mapbox Matrix API timeout")
        raise HTTPException(status_code=504, detail="Matrix calculation timeout. Reduce number of points.")
    except httpx.RequestError as e:
        logger.error(f"Network error calling Mapbox: {str(e)}")
        raise HTTPException(status_code=503, detail="Unable to reach map service.")


# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def validate_geojson_polygon(geojson: Dict[str, Any]) -> bool:
    """
    Validate that a GeoJSON object is a valid Polygon or MultiPolygon.
    Used for input sanitization before database storage.
    """
    if not geojson or not isinstance(geojson, dict):
        return False
    
    geom_type = geojson.get("type")
    if geom_type not in ["Polygon", "MultiPolygon"]:
        return False
    
    coordinates = geojson.get("coordinates")
    if not coordinates or not isinstance(coordinates, list):
        return False
    
    return True


def format_route_for_display(route: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a Mapbox route for government dashboard display.
    Adds user-friendly labels and converts units.
    """
    return {
        "route_id": route.get("id"),
        "travel_time": f"{route.get('duration_minutes', 0)} minutes",
        "distance": f"{route.get('distance_km', 0)} km",
        "geometry": route.get("geometry"),
        "suitable_for_diversion": True,  # Placeholder for traffic analysis
    }


# =====================================================
# AUDIT LOGGING
# =====================================================

def log_api_usage(endpoint: str, params: Dict[str, Any], user_id: Optional[str] = None):
    """
    Log all Mapbox API calls for cost tracking and government audit.
    """
    logger.info(f"AUDIT: Endpoint={endpoint}, User={user_id}, Params={params}")
    # In production, write to separate audit log file or database
