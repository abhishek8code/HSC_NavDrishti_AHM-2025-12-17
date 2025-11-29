"""
Emission analytics module for calculating CO2 savings from route optimization.
"""

def calculate_emission_savings(time_original: float, time_optimized: float) -> float:
    """
    Calculates CO2 emission savings based on time difference between routes.
    
    Formula: ΔF_j = Δt
    Where:
        ΔF_j = Emission savings (CO2 reduction)
        Δt = Time difference (time_original - time_optimized)
    
    A shorter route (time_optimized < time_original) results in positive CO2 saving
    because Δt > 0, meaning time is saved and emissions are reduced.
    
    Args:
        time_original (float): Travel time for the original route (in hours)
        time_optimized (float): Travel time for the optimized/shorter route (in hours)
    
    Returns:
        float: CO2 emission savings (positive value when shorter route is identified)
               Returns 0 if optimized route is not shorter
    """
    delta_t = time_original - time_optimized
    
    # Only return positive savings if the optimized route is shorter
    if delta_t > 0:
        return delta_t  # ΔF_j = Δt
    else:
        return 0.0  # No savings if route is not shorter

