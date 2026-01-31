import math

"""
This module provides functions for statistical computations and a Processor class
to perform a sequence of operations including caching.
"""


def compute_stats(data: list[float]) -> tuple[float, float]:
    """
    Computes the mean and sample variance of a list of numbers.

    Args:
        data: A list of numeric values (floats or ints).

    Returns:
        A tuple containing the mean and the sample variance.
        Returns (0.0, 0.0) if the input data list is empty.
    """
    if not data:
        return 0.0, 0.0

    total = 0.0
    for x in data:
        total += x

    avg = total / len(data)
    var = calculate_variance(data, avg)

    return avg, var


def calculate_variance(data: list[float], mean: float) -> float:
    """
    Calculates the sample variance of a list of numbers given their mean.

    Args:
        data: A list of numeric values (floats or ints).
        mean: The pre-calculated mean of the data.

    Returns:
        The sample variance of the data. Returns 0.0 if data has less than 2 elements.
    """
    if len(data) < 2:
        return 0.0

    sum_squared_diff = 0.0
    for x in data:
        sum_squared_diff += (x - mean) ** 2

    # Corrected denominator for sample variance
    return sum_squared_diff / (len(data) - 1)


class Processor:
    """
    A class to process a list of values, compute statistics, normalize them,
    and cache the result.
    """

    def __init__(self, values: list[float]) -> None:
        """
        Initializes the Processor with a list of values.

        Args:
            values: A list of numeric values to be processed.
        """
        self.values = values
        self.cache: dict[str, float] = {}

    def process(self) -> float:
        """
        Processes the stored values by computing statistics, normalizing them,
        and caching the result. If the result is already cached, it returns
        the cached value.

        Returns:
            The normalized result of the statistical computation.
        """
        if "result" in self.cache:
            return self.cache["result"]

        avg, var = compute_stats(self.values)
        result = self.normalize(avg, var)

        self.cache["result"] = result
        return result

    def normalize(self, avg: float, var: float) -> float:
        """
        Normalizes the average using the square root of the variance.

        Args:
            avg: The average of the data.
            var: The variance of the data.

        Returns:
            The normalized value (avg / sqrt(var)).

        Raises:
            ValueError: If variance is non-positive, as sqrt(var) would be
                        undefined for negative or lead to division by zero for zero.
        """
        if var <= 0:
            raise ValueError("Variance must be positive for normalization.")

        return avg / math.sqrt(var)


def main() -> None:
    """
    Main function to demonstrate the Processor class with sample data.
    """
    data = [1.0, 2.0, 3.0, 4.0, 5.0]

    p = Processor(data)
    result = p.process()

    print(f"Result is: {result}")


if __name__ == "__main__":
    main()
