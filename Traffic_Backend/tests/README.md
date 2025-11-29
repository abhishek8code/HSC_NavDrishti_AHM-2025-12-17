# Test Suite Documentation

This directory contains pytest unit tests for the Traffic Backend analytics modules.

## Test Files

### `test_road_analytics.py`
Tests for `calculate_roughness_penalty` function:
- **Empty list test**: Verifies function handles empty damaged segments list
- **Zero variance test**: Tests with identical severities (zero variance)
- **Extreme variance outliers test**: Verifies Critical Damage flag is triggered when extreme outliers are present
- **Moderate variance test**: Ensures Critical Damage is not triggered for moderate variance without outliers
- **Penalty application tests**: Verifies exponential penalty is applied when density thresholds are exceeded

### `test_emission_analytics.py`
Tests for `calculate_emission_savings` function:
- **Shorter route test**: Verifies positive CO2 saving for shorter routes (ΔF_j = Δt)
- **Formula verification**: Multiple test cases verifying ΔF_j = Δt formula
- **Edge cases**: Tests for equal routes, longer optimized routes, fractional values, etc.

## Running Tests

### Run all tests
```bash
cd Traffic_Backend
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_road_analytics.py -v
pytest tests/test_emission_analytics.py -v
```

### Run specific test class
```bash
pytest tests/test_road_analytics.py::TestCalculateRoughnessPenalty -v
pytest tests/test_emission_analytics.py::TestCalculateEmissionSavings -v
```

### Run with coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

## Test Requirements

All dependencies are listed in `requirements.txt`. Key testing dependencies:
- `pytest==7.4.3`
- `numpy==1.26.2`
- `networkx==3.2.1`

## Test Coverage

### `calculate_roughness_penalty`
- ✅ Empty damaged segments list
- ✅ Zero variance (identical severities)
- ✅ Extreme variance outliers triggering Critical Damage flag
- ✅ Moderate variance without outliers
- ✅ Single severity value
- ✅ Penalty application when density exceeded
- ✅ No penalty when density below threshold

### `calculate_emission_savings`
- ✅ Positive CO2 saving for shorter routes
- ✅ Formula verification (ΔF_j = Δt)
- ✅ No savings for longer/equal routes
- ✅ Edge cases (zero time, fractional values, large differences)

## Expected Test Results

All tests should pass with the following structure:

```
tests/test_road_analytics.py::TestCalculateRoughnessPenalty::test_empty_damaged_segments_list PASSED
tests/test_road_analytics.py::TestCalculateRoughnessPenalty::test_zero_variance PASSED
tests/test_road_analytics.py::TestCalculateRoughnessPenalty::test_extreme_variance_outliers_triggers_critical_damage PASSED
...

tests/test_emission_analytics.py::TestCalculateEmissionSavings::test_shorter_route_positive_co2_saving PASSED
tests/test_emission_analytics.py::TestCalculateEmissionSavings::test_formula_verification_delta_f_equals_delta_t PASSED
...
```

