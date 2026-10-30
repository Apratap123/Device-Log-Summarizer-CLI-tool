import math
from typing import Any, List

def clean_sensor_readings(readings: Any) -> List[float]:
    if not isinstance(readings, (list, tuple)):
        return []
    
    cleaned_readings: List[float] = []
    
    for item in readings:
        if item is None or isinstance(item, bool):
            continue
        try:
            converted_value = float(item)
        except (ValueError, TypeError):
            continue
            
        if math.isnan(converted_value) or math.isinf(converted_value):
            continue
            
        if converted_value < 0.0:
            continue
            
        if converted_value > 500.0:
            converted_value = 500.0
            
        cleaned_readings.append(converted_value)
        
    return cleaned_readings

def run_sample_tests() -> None:
    sample_mixed_input = ["12.5", None, -5, "sensor_error", 620.4, 0, 499.9, "350.25", True, False]
    expected_mixed_output = [12.5, 500.0, 0.0, 499.9, 350.25]
    result_mixed = clean_sensor_readings(sample_mixed_input)
    assert result_mixed == expected_mixed_output, f"Expected {expected_mixed_output}, got {result_mixed}"
    print("Test Case 1 (Mixed Inputs & Clipping): Passed ->", result_mixed)

    empty_input = []
    expected_empty_output = []
    result_empty = clean_sensor_readings(empty_input)
    assert result_empty == expected_empty_output, f"Expected {expected_empty_output}, got {result_empty}"
    print("Test Case 2 (Empty List): Passed ->", result_empty)

    all_invalid_input = [None, "fault", -10.5, "N/A", -0.01, False]
    expected_invalid_output = []
    result_invalid = clean_sensor_readings(all_invalid_input)
    assert result_invalid == expected_invalid_output, f"Expected {expected_invalid_output}, got {result_invalid}"
    print("Test Case 3 (All Invalid Entries): Passed ->", result_invalid)

    boundary_input = [0.0, 500.0, 500.01, 10000.0]
    expected_boundary_output = [0.0, 500.0, 500.0, 500.0]
    result_boundary = clean_sensor_readings(boundary_input)
    assert result_boundary == expected_boundary_output, f"Expected {expected_boundary_output}, got {result_boundary}"
    print("Test Case 4 (Boundary & Extreme Values): Passed ->", result_boundary)

if __name__ == "__main__":
    run_sample_tests()
