"""
This module provides a simple calculator class and a function to calculate the area of a circle.
"""

import math

def calculate_area(radius: float) -> float:
    """
    Calculates the area of a circle given its radius.

    Args:
        radius (float): The radius of the circle.

    Returns:
        float: The calculated area of the circle.
    """
    return math.pi * radius ** 2

class Calculator:
    """
    A simple calculator class that performs basic arithmetic operations
    and keeps a history of operations (though not fully implemented in this version).
    """
    def __init__(self) -> None:
        """
        Initializes the Calculator with an empty history list.
        """
        self.history: list = []

    def add(self, a: float, b: float) -> float:
        """
        Adds two numbers together.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The sum of a and b.
        """
        return a + b

    def divide(self, a: float, b: float) -> float:
        """
        Divides the first number by the second number.

        Args:
            a (float): The numerator.
            b (float): The denominator.

        Returns:
            float: The result of the division.

        Raises:
            ZeroDivisionError: If the denominator b is zero.
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero.")
        return a / b

    def multiply(self, a: float, b: float) -> float:
        """
        Multiplies two numbers together.

        Args:
            a (float): The first number.
            b (float): The second number.

        Returns:
            float: The product of a and b.
        """
        return a * b