import pytest
import math
from app import calculate_area, Calculator

# --- Tests for calculate_area function ---

def test_calculate_area_positive_radius():
    """
    Test calculate_area with a positive radius.
    """
    radius = 5.0
    expected_area = math.pi * (radius ** 2)
    assert calculate_area(radius) == pytest.approx(expected_area)

def test_calculate_area_zero_radius():
    """
    Test calculate_area with a radius of zero.
    """
    radius = 0.0
    expected_area = 0.0
    assert calculate_area(radius) == pytest.approx(expected_area)

def test_calculate_area_negative_radius():
    """
    Test calculate_area with a negative radius.
    The square of a negative number is positive, so area should be positive.
    """
    radius = -3.0
    expected_area = math.pi * (radius ** 2) # (-3.0)**2 = 9.0
    assert calculate_area(radius) == pytest.approx(expected_area)

def test_calculate_area_float_radius():
    """
    Test calculate_area with a floating-point radius.
    """
    radius = 2.5
    expected_area = math.pi * (radius ** 2)
    assert calculate_area(radius) == pytest.approx(expected_area)

def test_calculate_area_large_radius():
    """
    Test calculate_area with a large radius.
    """
    radius = 1000.0
    expected_area = math.pi * (radius ** 2)
    assert calculate_area(radius) == pytest.approx(expected_area)

# --- Tests for Calculator class ---

@pytest.fixture
def calculator_instance():
    """
    Fixture to provide a fresh Calculator instance for each test.
    """
    return Calculator()

def test_calculator_init(calculator_instance):
    """
    Test that the Calculator initializes with an empty history.
    """
    assert calculator_instance.history == []

# --- Tests for add method ---

def test_calculator_add_positive_numbers(calculator_instance):
    """
    Test add method with two positive numbers.
    """
    assert calculator_instance.add(2, 3) == 5

def test_calculator_add_negative_numbers(calculator_instance):
    """
    Test add method with two negative numbers.
    """
    assert calculator_instance.add(-2, -3) == -5

def test_calculator_add_mixed_numbers(calculator_instance):
    """
    Test add method with a positive and a negative number.
    """
    assert calculator_instance.add(5, -3) == 2
    assert calculator_instance.add(-5, 3) == -2

def test_calculator_add_with_zero(calculator_instance):
    """
    Test add method with zero.
    """
    assert calculator_instance.add(0, 7) == 7
    assert calculator_instance.add(7, 0) == 7
    assert calculator_instance.add(0, 0) == 0

def test_calculator_add_float_numbers(calculator_instance):
    """
    Test add method with floating-point numbers.
    """
    assert calculator_instance.add(2.5, 3.5) == pytest.approx(6.0)
    assert calculator_instance.add(0.1, 0.2) == pytest.approx(0.3)

# --- Tests for divide method ---

def test_calculator_divide_positive_numbers(calculator_instance):
    """
    Test divide method with two positive numbers.
    """
    assert calculator_instance.divide(10, 2) == 5.0

def test_calculator_divide_negative_numbers(calculator_instance):
    """
    Test divide method with two negative numbers.
    """
    assert calculator_instance.divide(-10, -2) == 5.0

def test_calculator_divide_mixed_numbers(calculator_instance):
    """
    Test divide method with a positive and a negative number.
    """
    assert calculator_instance.divide(10, -2) == -5.0
    assert calculator_instance.divide(-10, 2) == -5.0

def test_calculator_divide_by_one(calculator_instance):
    """
    Test divide method when dividing by one.
    """
    assert calculator_instance.divide(7, 1) == 7.0

def test_calculator_divide_zero_by_number(calculator_instance):
    """
    Test divide method when dividing zero by a non-zero number.
    """
    assert calculator_instance.divide(0, 5) == 0.0

def test_calculator_divide_float_numbers(calculator_instance):
    """
    Test divide method with floating-point numbers.
    """
    assert calculator_instance.divide(7.0, 2.0) == pytest.approx(3.5)
    assert calculator_instance.divide(1.0, 3.0) == pytest.approx(0.3333333333333333)

def test_calculator_divide_by_zero_raises_error(calculator_instance):
    """
    Test divide method raises ZeroDivisionError when denominator is zero.
    """
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        calculator_instance.divide(10, 0)

def test_calculator_divide_zero_by_zero_raises_error(calculator_instance):
    """
    Test divide method raises ZeroDivisionError when both numerator and denominator are zero.
    """
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        calculator_instance.divide(0, 0)

# --- Tests for multiply method ---

def test_calculator_multiply_positive_numbers(calculator_instance):
    """
    Test multiply method with two positive numbers.
    """
    assert calculator_instance.multiply(2, 3) == 6

def test_calculator_multiply_negative_numbers(calculator_instance):
    """
    Test multiply method with two negative numbers.
    """
    assert calculator_instance.multiply(-2, -3) == 6

def test_calculator_multiply_mixed_numbers(calculator_instance):
    """
    Test multiply method with a positive and a negative number.
    """
    assert calculator_instance.multiply(5, -3) == -15
    assert calculator_instance.multiply(-5, 3) == -15

def test_calculator_multiply_by_zero(calculator_instance):
    """
    Test multiply method when one of the numbers is zero.
    """
    assert calculator_instance.multiply(0, 7) == 0
    assert calculator_instance.multiply(7, 0) == 0
    assert calculator_instance.multiply(0, 0) == 0

def test_calculator_multiply_float_numbers(calculator_instance):
    """
    Test multiply method with floating-point numbers.
    """
    assert calculator_instance.multiply(2.5, 3.0) == pytest.approx(7.5)
    assert calculator_instance.multiply(0.5, 0.5) == pytest.approx(0.25)

def test_calculator_multiply_large_numbers(calculator_instance):
    """
    Test multiply method with large numbers.
    """
    assert calculator_instance.multiply(1000000, 2000000) == 2000000000000