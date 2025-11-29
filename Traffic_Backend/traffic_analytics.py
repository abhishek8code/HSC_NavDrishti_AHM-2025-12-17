import pandas as pd
import numpy as np
from scipy.stats import entropy

def calculate_flow_stability(
    df: pd.DataFrame, 
    speed_col: str = 'speed', 
    entropy_threshold: float = 1.5, 
    low_speed_threshold: float = 20.0
) -> str:
    """
    Calculates the stability of traffic flow using Shannon's Entropy on speed distribution.
    
    Implements the logic from 'Visual Cause Analytics for Traffic Congestion' by Pi et al.
    High entropy indicates mixed speeds (Unstable/Transitioning).
    Low entropy indicates uniform speeds (either uniformly fast or uniformly stuck).

    Args:
        df (pd.DataFrame): DataFrame containing vehicle data for the last 15 minutes.
        speed_col (str): Name of the column containing vehicle speeds (km/h).
        entropy_threshold (float): Cutoff for defining 'High' entropy (tunable).
        low_speed_threshold (float): Cutoff (km/h) for defining 'Congestion'.

    Returns:
        str: 'Unstable', 'Congested', or 'Free Flow'.
    """
    
    # 1. Handle Empty Data (No traffic = Free Flow or No Data)
    if df.empty or speed_col not in df.columns:
        return "Free Flow" # Default assumption if road is empty

    speeds = df[speed_col].dropna()
    
    if len(speeds) == 0:
        return "Free Flow"

    # 2. Construct Histogram (Speed Bins) to get P(x_i)
    # We use fixed bins of 5 km/h to standardise the distribution analysis
    # Range is 0 to max_speed + buffer
    max_speed = speeds.max()
    bins = np.arange(0, max_speed + 10, 5) 
    
    # Get counts per bin
    counts, _ = np.histogram(speeds, bins=bins)
    
    # Calculate Probabilities P(x_i)
    # P(x_i) = count_in_bin / total_count
    probabilities = counts / counts.sum()
    
    # 3. Calculate Shannon's Entropy: H(X) = - sum(P(x) * log(P(x)))
    # Scipy's entropy function uses natural log by default (nat units) or base 2 (bits)
    # We use base 2 for standard information theory alignment
    flow_entropy = entropy(probabilities, base=2)
    
    # Calculate Average Speed for the second condition
    avg_speed = speeds.mean()

    # 4. Classification Logic (per Pi et al.)
    
    # Condition A: High Entropy -> High variance in speeds -> Unstable/Transitioning
    # This detects the onset or dissipation of congestion before it becomes a gridlock.
    if flow_entropy > entropy_threshold:
        return "Unstable"
    
    # Condition B: Low Entropy -> Stable State
    else:
        # Stable + Low Speed = All cars are moving slowly uniformly (Gridlock)
        if avg_speed < low_speed_threshold:
            return "Congested"
        
        # Stable + High Speed = All cars are moving fast uniformly
        else:
            return "Free Flow"

# --- Example Usage (Integration Context) ---
# Assuming 'traffic_data' is your filtered 15-minute window DataFrame
# 
# status = calculate_flow_stability(traffic_data)
# print(f"Current Road Status: {status}")