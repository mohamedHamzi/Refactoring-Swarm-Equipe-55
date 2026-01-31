import pytest
import math # Added import math
from bad import compute_stats, calculate_variance, Processor, main
import io
import sys

# Test cases for compute_stats
def test_compute_stats_valid_data():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    mean, variance = compute_stats(data)
    assert pytest.approx(mean) == 3.0
    assert pytest.approx(variance) == 2.5

def test_compute_stats_empty_data():
    mean, variance = compute_stats([])
    assert mean == 0.0
    assert variance == 0.0

def test_compute_stats_single_element():
    data = [5.0]
    mean, variance = compute_stats(data)
    assert mean == 5.0
    assert variance == 0.0 # Variance for single element is 0.0 (len < 2)

# Test cases for calculate_variance
def test_calculate_variance_valid_data():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    mean = 3.0
    variance = calculate_variance(data, mean)
    assert pytest.approx(variance) == 2.5

def test_calculate_variance_empty_data():
    variance = calculate_variance([], 0.0)
    assert variance == 0.0

def test_calculate_variance_single_element():
    variance = calculate_variance([5.0], 5.0)
    assert variance == 0.0

# Test cases for Processor class
def test_processor_init():
    p = Processor([1.0, 2.0])
    assert p.values == [1.0, 2.0]
    assert p.cache == {}

def test_processor_process_first_call():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    p = Processor(data)
    result = p.process()
    # Expected: mean = 3.0, variance = 2.5, normalized = 3.0 / sqrt(2.5)
    assert pytest.approx(result) == 3.0 / math.sqrt(2.5)
    assert "result" in p.cache
    assert pytest.approx(p.cache["result"]) == 3.0 / math.sqrt(2.5)

def test_processor_process_cached_call():
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    p = Processor(data)
    first_result = p.process() # Populate cache
    second_result = p.process() # Should use cache
    assert first_result == second_result
    # Verify that compute_stats and normalize are not called again (mocking would be better for this)
    # For now, just check the result is the same and cache is populated.

def test_processor_normalize_valid_inputs():
    p = Processor([]) # Values don't matter for normalize
    avg = 10.0
    var = 4.0
    normalized_value = p.normalize(avg, var)
    assert pytest.approx(normalized_value) == 10.0 / math.sqrt(4.0)

def test_processor_normalize_non_positive_variance():
    p = Processor([])
    with pytest.raises(ValueError, match="Variance must be positive for normalization."):
        p.normalize(10.0, 0.0)
    with pytest.raises(ValueError, match="Variance must be positive for normalization."):
        p.normalize(10.0, -1.0)

# Test main function output
def test_main_function_output(capsys):
    main()
    captured = capsys.readouterr()
    # Calculate expected output based on data = [1.0, 2.0, 3.0, 4.0, 5.0]
    # Mean = 3.0, Variance = 2.5
    expected_output_value = 3.0 / math.sqrt(2.5)
    assert captured.out.strip() == f"Result is: {expected_output_value}"
