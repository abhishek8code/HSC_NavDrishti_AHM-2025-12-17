"""
Pytest unit tests for emission_analytics module.
Tests for calculate_emission_savings function.
"""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from emission_analytics import calculate_emission_savings


class TestCalculateEmissionSavings:
    """Test suite for calculate_emission_savings function."""
    
    def test_shorter_route_positive_co2_saving(self):
        """
        Verify that identifying a shorter route results in a positive CO2 saving value.
        Formula: ΔF_j = Δt where Δt = time_original - time_optimized
        """
        # Original route takes 2 hours
        time_original = 2.0
        
        # Optimized/shorter route takes 1.5 hours
        time_optimized = 1.5
        
        # Calculate savings
        savings = calculate_emission_savings(time_original, time_optimized)
        
        # Verify positive CO2 saving (0.5 hours saved)
        assert savings > 0, "Shorter route should result in positive CO2 saving"
        assert savings == 0.5, f"Expected 0.5 hours saved, got {savings}"
        
        # Verify formula: ΔF_j = Δt
        delta_t = time_original - time_optimized
        assert savings == delta_t, "Savings should equal time difference (ΔF_j = Δt)"
    
    def test_significant_time_savings(self):
        """Test with significant time difference (larger savings)."""
        time_original = 3.5  # hours
        time_optimized = 2.0  # hours
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 1.5, "Expected 1.5 hours saved"
        assert savings > 0, "Should be positive"
    
    def test_small_time_savings(self):
        """Test with small time difference."""
        time_original = 1.0  # hours
        time_optimized = 0.95  # hours (5 minutes saved)
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 0.05, "Expected 0.05 hours (3 minutes) saved"
        assert savings > 0, "Should be positive even for small savings"
    
    def test_no_savings_when_optimized_not_shorter(self):
        """Test that no savings are returned when optimized route is not shorter."""
        time_original = 1.0  # hours
        time_optimized = 1.5  # hours (longer route)
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 0.0, "No savings when optimized route is longer"
    
    def test_no_savings_when_routes_equal(self):
        """Test that no savings when both routes take same time."""
        time_original = 2.0  # hours
        time_optimized = 2.0  # hours
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 0.0, "No savings when routes are equal"
    
    def test_formula_verification_delta_f_equals_delta_t(self):
        """
        Verify the formula ΔF_j = Δt holds for multiple test cases.
        """
        test_cases = [
            (2.0, 1.0, 1.0),   # 1 hour saved
            (1.5, 1.0, 0.5),   # 0.5 hours saved
            (3.0, 2.5, 0.5),   # 0.5 hours saved
            (5.0, 4.0, 1.0),   # 1 hour saved
        ]
        
        for time_orig, time_opt, expected_savings in test_cases:
            savings = calculate_emission_savings(time_orig, time_opt)
            delta_t = time_orig - time_opt
            
            assert savings == delta_t, \
                f"Formula violation: ΔF_j ({savings}) != Δt ({delta_t})"
            assert savings == expected_savings, \
                f"Expected {expected_savings}, got {savings}"
    
    def test_fractional_time_savings(self):
        """Test with fractional time values."""
        time_original = 1.75  # hours
        time_optimized = 1.25  # hours
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 0.5, "Expected 0.5 hours saved"
        assert isinstance(savings, float), "Should return float"
    
    def test_zero_original_time(self):
        """Test edge case with zero original time."""
        time_original = 0.0
        time_optimized = 0.0
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 0.0, "No savings when both times are zero"
    
    def test_negative_time_handling(self):
        """Test that function handles negative time values appropriately."""
        # If optimized is negative (invalid), should return 0
        time_original = 1.0
        time_optimized = -0.5  # Invalid, but function should handle gracefully
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        # Optimized is "shorter" (negative), but this is invalid
        # Function should return 0 as optimized is not actually shorter
        assert savings == 0.0, "Should return 0 for invalid negative optimized time"
    
    def test_very_large_time_difference(self):
        """Test with very large time difference."""
        time_original = 10.0  # hours
        time_optimized = 1.0   # hours
        
        savings = calculate_emission_savings(time_original, time_optimized)
        
        assert savings == 9.0, "Expected 9 hours saved"
        assert savings > 0, "Should be positive"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

