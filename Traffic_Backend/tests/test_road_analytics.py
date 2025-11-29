"""
Pytest unit tests for road_analytics module.
Tests for calculate_roughness_penalty function.
"""

import pytest
import networkx as nx
import numpy as np
from math import sqrt, exp
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from road_analytics import calculate_roughness_penalty, DamagedSegment


class TestCalculateRoughnessPenalty:
    """Test suite for calculate_roughness_penalty function."""
    
    def create_test_graph(self):
        """Helper method to create a test graph with nodes and edges."""
        graph = nx.Graph()
        
        # Add nodes with position attributes
        graph.add_node('A', pos=(23.0225, 72.5714))
        graph.add_node('B', pos=(23.0300, 72.5800))
        graph.add_node('C', pos=(23.0400, 72.5900))
        
        # Add edges with initial weights and lengths
        graph.add_edge('A', 'B', weight=1.0, length=100.0)  # 100 meters
        graph.add_edge('B', 'C', weight=1.0, length=150.0)  # 150 meters
        
        return graph
    
    def test_empty_damaged_segments_list(self):
        """Test calculate_roughness_penalty with an empty list of damaged segments."""
        graph = self.create_test_graph()
        
        # Call function with empty list
        result_graph = calculate_roughness_penalty(graph, [])
        
        # Verify graph structure is preserved
        assert result_graph.number_of_nodes() == 3
        assert result_graph.number_of_edges() == 2
        
        # Verify all edges have initialized damage tracking
        for u, v, data in result_graph.edges(data=True):
            assert data['damage_count'] == 0
            assert data['total_severity'] == 0.0
            assert data['severity_variance'] == 0.0
            assert data['critical_damage'] == False
            assert 'severity_list' in data
        
        # Verify no penalties were applied
        for u, v, data in result_graph.edges(data=True):
            assert data.get('roughness_penalty_applied', False) == False
    
    def test_zero_variance(self):
        """Test calculate_roughness_penalty with zero variance (all severities identical)."""
        graph = self.create_test_graph()
        
        # Create damaged segments with identical severity (zero variance)
        damaged_segments = [
            DamagedSegment(cluster_id=1, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=3.0, count=5),
            DamagedSegment(cluster_id=2, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=3.0, count=3),
        ]
        
        result_graph = calculate_roughness_penalty(graph, damaged_segments)
        
        # Find the edge that received the damage (should be A-B based on centroid)
        edge_data = result_graph['A']['B']
        
        # Verify damage was assigned
        assert edge_data['damage_count'] > 0
        
        # Verify variance is zero (all severities are 3.0)
        assert edge_data['severity_variance'] == 0.0
        assert edge_data['severity_mean'] == 3.0
        assert edge_data['severity_std'] == 0.0
        
        # Verify Critical Damage flag is False (no outliers when variance is zero)
        assert edge_data['critical_damage'] == False
    
    def test_extreme_variance_outliers_triggers_critical_damage(self):
        """Test that extreme variance outliers trigger the 'Critical Damage' flag."""
        graph = self.create_test_graph()
        
        # Create damaged segments with extreme variance (mix of low and very high severities)
        # This simulates a road with mostly normal damage but some critical spots
        damaged_segments = [
            DamagedSegment(cluster_id=1, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=2.0, count=10),  # Normal damage
            DamagedSegment(cluster_id=2, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=15.0, count=2),  # Extreme outlier
            DamagedSegment(cluster_id=3, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=1.5, count=5),  # Normal damage
        ]
        
        result_graph = calculate_roughness_penalty(graph, damaged_segments)
        
        # Find the edge that received the damage
        edge_data = result_graph['A']['B']
        
        # Verify damage was assigned
        assert edge_data['damage_count'] > 0
        
        # Verify variance is high (not zero)
        variance = edge_data['severity_variance']
        assert variance > 0.0, "Variance should be positive with mixed severities"
        
        # Calculate expected values
        severity_list = edge_data['severity_list']
        expected_mean = np.mean(severity_list)
        expected_std = np.std(severity_list)
        
        # Verify variance calculation
        assert abs(edge_data['severity_mean'] - expected_mean) < 0.01
        assert abs(edge_data['severity_std'] - expected_std) < 0.01
        
        # Verify Critical Damage flag is True (extreme outliers detected)
        assert edge_data['critical_damage'] == True, \
            "Critical Damage flag should be True when extreme outliers are present"
        
        # Verify the outlier threshold logic
        # Outliers are values > mean + 2*std
        outlier_threshold = expected_mean + (2 * expected_std)
        has_outliers = any(sev > outlier_threshold for sev in severity_list)
        assert has_outliers, "Test data should contain outliers"
    
    def test_moderate_variance_no_critical_damage(self):
        """Test that moderate variance without extreme outliers does not trigger Critical Damage."""
        graph = self.create_test_graph()
        
        # Create damaged segments with moderate variance (no extreme outliers)
        damaged_segments = [
            DamagedSegment(cluster_id=1, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=2.0, count=5),
            DamagedSegment(cluster_id=2, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=3.5, count=5),
            DamagedSegment(cluster_id=3, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=2.5, count=5),
        ]
        
        result_graph = calculate_roughness_penalty(graph, damaged_segments)
        
        edge_data = result_graph['A']['B']
        
        # Verify variance exists but is moderate
        assert edge_data['severity_variance'] > 0.0
        assert edge_data['severity_variance'] < 5.0  # Moderate variance
        
        # Verify Critical Damage flag is False (no extreme outliers)
        assert edge_data['critical_damage'] == False, \
            "Critical Damage should be False when variance is moderate without extreme outliers"
    
    def test_single_severity_value_zero_variance(self):
        """Test with single damaged segment (single severity value = zero variance)."""
        graph = self.create_test_graph()
        
        damaged_segments = [
            DamagedSegment(cluster_id=1, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=4.0, count=1),
        ]
        
        result_graph = calculate_roughness_penalty(graph, damaged_segments)
        
        edge_data = result_graph['A']['B']
        
        # Verify variance is zero (single value)
        assert edge_data['severity_variance'] == 0.0
        assert edge_data['severity_mean'] == 4.0
        assert edge_data['critical_damage'] == False
    
    def test_penalty_applied_when_density_exceeded(self):
        """Test that exponential penalty is applied when damage density exceeds threshold."""
        graph = self.create_test_graph()
        
        # Create enough damage to exceed density threshold (5 per 100m = 0.05 per meter)
        # For a 100m edge, we need > 5 damage points
        damaged_segments = [
            DamagedSegment(cluster_id=1, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=3.0, count=10),  # 10 points on 100m edge = 0.1 per meter
        ]
        
        original_weight = graph['A']['B']['weight']
        result_graph = calculate_roughness_penalty(graph, damaged_segments)
        
        edge_data = result_graph['A']['B']
        
        # Verify penalty was applied
        assert edge_data.get('roughness_penalty_applied', False) == True
        assert edge_data['weight'] > original_weight  # Weight should increase
    
    def test_no_penalty_when_density_below_threshold(self):
        """Test that no penalty is applied when damage density is below threshold."""
        graph = self.create_test_graph()
        
        # Create minimal damage (below threshold: < 5 per 100m)
        damaged_segments = [
            DamagedSegment(cluster_id=1, centroid_lat=23.0225, centroid_lon=72.5714, 
                          avg_severity=3.0, count=2),  # 2 points on 100m edge = 0.02 per meter
        ]
        
        original_weight = graph['A']['B']['weight']
        result_graph = calculate_roughness_penalty(graph, damaged_segments)
        
        edge_data = result_graph['A']['B']
        
        # Verify no penalty was applied
        assert edge_data.get('roughness_penalty_applied', False) == False
        assert edge_data['weight'] == original_weight  # Weight unchanged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

