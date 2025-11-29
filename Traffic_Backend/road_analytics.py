import pandas as pd
import numpy as np
import networkx as nx
from sklearn.cluster import DBSCAN
from math import radians, exp, sqrt

# Data Object Definition
class DamagedSegment:
    def __init__(self, cluster_id, centroid_lat, centroid_lon, avg_severity, count):
        self.cluster_id = cluster_id
        self.centroid = (centroid_lat, centroid_lon)
        self.avg_severity = avg_severity
        self.count = count # Number of anomalies in this cluster

    def __repr__(self):
        return f"DamagedSegment(ID={self.cluster_id}, Sev={self.avg_severity:.2f}, Count={self.count})"

def process_damage_clusters(df: pd.DataFrame, epsilon_meters=20, min_samples=3) -> list[DamagedSegment]:
    """
    Ingests road damage data (Lat/Lon/Severity) and applies DBSCAN clustering.
    Returns a list of DamagedSegment objects.
    """
    # 1. Coordinate Conversion
    # DBSCAN with haversine metric requires radians.
    # Earth Radius ~ 6371km. Epsilon must be converted to radians.
    kms_per_radian = 6371.0088
    epsilon_radians = (epsilon_meters / 1000.0) / kms_per_radian

    coords = df[['lat', 'lon']].values
    
    # 2. DBSCAN Clustering 
    # metric='haversine' expects [lat, lon] in radians
    db = DBSCAN(eps=epsilon_radians, min_samples=min_samples, algorithm='ball_tree', metric='haversine')
    df['cluster'] = db.fit_predict(np.radians(coords))

    # 3. Aggregation Logic
    # Filter noise (cluster -1) and group by valid clusters
    clustered_data = df[df['cluster'] != -1]
    
    damaged_segments = []
    
    for cluster_id, group in clustered_data.groupby('cluster'):
        # Calculate Centroid
        centroid_lat = group['lat'].mean()
        centroid_lon = group['lon'].mean()
        
        # Calculate Average Severity (e.g., from accelerometer MAXacc or variance) 
        avg_severity = group['severity'].mean()
        count = len(group)
        
        damaged_segments.append(DamagedSegment(
            cluster_id, centroid_lat, centroid_lon, avg_severity, count
        ))
        
    return damaged_segments

def calculate_roughness_penalty(graph: nx.Graph, damaged_segments: list[DamagedSegment]):
    """
    Maps damaged segments to the nearest graph edge and applies an exponential
    penalty if density thresholds are exceeded[cite: 147, 149].
    Includes variance-based outlier detection to flag Critical Damage.
    """
    # Initialize a damage counter on edges if not present
    for u, v, data in graph.edges(data=True):
        if 'damage_count' not in data:
            data['damage_count'] = 0
            data['total_severity'] = 0.0
            data['severity_list'] = []  # Store individual severities for variance calculation

    # 1. Map Matching (Simplified Nearest Edge Logic)
    # In a production environment, use Geopandas sjoin or R-Tree for efficiency [cite: 123]
    for seg in damaged_segments:
        nearest_edge = None
        min_dist = float('inf')
        
        # Iterate edges to find the geometrically nearest one
        # Assumes nodes have 'pos'=(lat, lon) attributes
        for u, v, data in graph.edges(data=True):
            p1 = graph.nodes[u]['pos']
            p2 = graph.nodes[v]['pos']
            
            # Simple Euclidean approximation for demonstration 
            # (Use Haversine or Point-to-Line distance in production)
            edge_midpoint = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
            dist = sqrt((seg.centroid[0] - edge_midpoint[0])**2 + 
                        (seg.centroid[1] - edge_midpoint[1])**2)
            
            if dist < min_dist:
                min_dist = dist
                nearest_edge = (u, v)
        
        # Assign damage to the nearest edge
        if nearest_edge:
            u, v = nearest_edge
            graph[u][v]['damage_count'] += seg.count
            graph[u][v]['total_severity'] += seg.avg_severity * seg.count
            # Store individual severities for variance calculation
            graph[u][v]['severity_list'].extend([seg.avg_severity] * seg.count)

    # 2. Calculate variance and detect outliers for Critical Damage flag
    for u, v, data in graph.edges(data=True):
        severity_list = data.get('severity_list', [])
        
        if len(severity_list) > 1:
            # Calculate variance
            variance = np.var(severity_list)
            mean_severity = np.mean(severity_list)
            std_dev = sqrt(variance) if variance > 0 else 0
            
            data['severity_variance'] = variance
            data['severity_mean'] = mean_severity
            data['severity_std'] = std_dev
            
            # Detect outliers: values beyond 2 standard deviations from mean
            # Extreme outliers trigger Critical Damage flag
            outlier_threshold = mean_severity + (2 * std_dev)
            has_extreme_outliers = any(sev > outlier_threshold for sev in severity_list)
            
            if has_extreme_outliers and variance > 0:
                data['critical_damage'] = True
            else:
                data['critical_damage'] = False
        elif len(severity_list) == 1:
            # Single value: zero variance
            data['severity_variance'] = 0.0
            data['severity_mean'] = severity_list[0]
            data['severity_std'] = 0.0
            data['critical_damage'] = False
        else:
            # Empty list: no variance
            data['severity_variance'] = 0.0
            data['severity_mean'] = 0.0
            data['severity_std'] = 0.0
            data['critical_damage'] = False

    # 3. Apply Exponential Penalty [cite: 148, 149]
    for u, v, data in graph.edges(data=True):
        length_meters = data.get('length', 100) # Default to 100m if missing
        damage_count = data.get('damage_count', 0)
        
        if length_meters > 0:
            # Calculate Density (anomalies per meter)
            density = damage_count / length_meters
            
            # "If the density of anomalies exceeds 5 per 100m" (0.05 per meter)
            if density > 0.05:
                avg_sev = data['total_severity'] / damage_count if damage_count > 0 else 0
                
                # Exponential Penalty Formula
                # This drastically increases 'weight' (cost) to simulate driver avoidance
                penalty_factor = exp(density * (avg_sev / 10.0)) 
                
                # Update the edge weight used by Dijkstra/A*
                original_weight = data.get('weight', 1.0)
                data['weight'] = original_weight * penalty_factor
                data['roughness_penalty_applied'] = True

    return graph