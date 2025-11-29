from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Route:
    """
    Represents a calculated route segment.
    Attributes:
        length_km (float): Total distance of the route in Kilometers.
        lane_count (int): Minimum lane count found on the primary segments of this route.
        route_id (str): Unique identifier for the route.
    """
    route_id: str
    length_km: float
    lane_count: int

def assess_diversion(primary_route: Route, alternative_routes: List[Route]) -> Dict[str, Any]:
    """
    Evaluates whether a specific diversion analysis is required based on infrastructure 
    constraints (FR-3.6.1).

    Logic:
    1. Single Lane Constraint: If the primary route has only 1 lane, it is a bottleneck candidate.
    2. Detour Efficiency Constraint: If any alternative route adds > 3.0 km to the journey, 
       it is considered an inefficient detour, requiring analysis.

    Args:
        primary_route (Route): The optimal path found by the algorithm.
        alternative_routes (List[Route]): List of other viable paths found (e.g., via Yen's K-Shortest).

    Returns:
        Dict[str, Any]: {
            "diversion_required": bool, 
            "reason": str (or None),
            "meta": dict (debug info)
        }
    """
    
    # default response
    response = {
        "diversion_required": False,
        "reason": None,
        "meta": {}
    }

    # 1. Check Primary Route Infrastructure (Single Lane Constraint)
    # Single lane roads cannot handle high volume or broken down vehicles easily.
    if primary_route.lane_count == 1:
        response["diversion_required"] = True
        response["reason"] = "Infrastructure Constraint: Primary route is Single Lane."
        return response

    # 2. Check Efficiency of Alternatives (Distance Threshold)
    # If the alternatives are significantly longer, simple automatic diversion might 
    # cause excessive fuel consumption or delays.
    threshold_km = 3.0
    inefficient_alternatives = []

    for alt in alternative_routes:
        detour_added = alt.length_km - primary_route.length_km
        
        if detour_added > threshold_km:
            inefficient_alternatives.append(f"{alt.route_id} (+{detour_added:.2f}km)")

    if inefficient_alternatives:
        response["diversion_required"] = True
        response["reason"] = (
            f"Efficiency Constraint: Alternative routes exceed deviation threshold (+{threshold_km}km). "
            f"Routes flagged: {', '.join(inefficient_alternatives)}"
        )
        return response

    return response

# --- Integration Example ---
if __name__ == "__main__":
    # Simulate a scenario from the Routing Engine
    primary = Route(route_id="RT_A", length_km=10.5, lane_count=2)
    
    alts = [
        Route(route_id="RT_B", length_km=11.2, lane_count=2), # +0.7km (OK)
        Route(route_id="RT_C", length_km=14.0, lane_count=2)  # +3.5km (Too long)
    ]

    result = assess_diversion(primary, alts)
    print(f"Diversion Check Result: {result}")