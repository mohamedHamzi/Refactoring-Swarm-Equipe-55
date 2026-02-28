import copy
from typing import Any, List, Set

# --- Start of DataModel definition (simulating shared_types.py) ---
# This DataModel is defined here to make the provided code complete and runnable
# within a single file, as per the instructions. In a multi-file project,
# this would typically reside in a separate module like 'shared_types.py'.

class DataModel:
    """
    Represents a data entity with an ID, a mutable data payload, and a processing status.

    Attributes:
        id (int): A unique identifier for the data model.
        data (dict): The mutable data payload associated with the model.
        processed (bool): A flag indicating whether the model has been processed.
    """
    def __init__(self, id: int, data: dict):
        """
        Initializes a new DataModel instance.

        Args:
            id (int): The unique identifier for this model.
            data (dict): The initial data payload.
        """
        self.id = id
        self.data = data
        self.processed = False # Default status
# --- End of DataModel definition ---


class DataProcessor:
    """
    Processes DataModel objects, transforming their data and maintaining a history.

    This processor ensures that transformations on the data payload of a DataModel
    do not inadvertently modify the original model's data by using deep copies.
    It also tracks the processed data in its history.
    """
    def __init__(self):
        """
        Initializes the DataProcessor with an empty history list.
        """
        self.history: List[dict] = []

    def transform(self, model: DataModel) -> dict:
        """
        Transforms the data within a DataModel object.

        If a "value" key is present in the model's data, its value is incremented by 100.
        The model's `processed` flag is set to True, and a deep copy of the transformed
        data is appended to the processor's history.

        Args:
            model: The DataModel object to be transformed.

        Side Effects:
            - Modifies `model.processed` to `True`.
            - Appends a deep copy of the transformed data to `self.history`.

        Returns:
            A deep copy of the transformed data dictionary.
        """
        # Fix: Shallow copy! Use deepcopy to prevent modifying the original model.data
        temp_data: dict = copy.deepcopy(model.data)

        if "value" in temp_data:
            temp_data["value"] += 100

        model.processed = True
        self.history.append(temp_data)
        return temp_data


def bulk_process(items: List[DataModel]) -> bool:
    """
    Checks a list of DataModel objects for duplicate IDs.

    This function efficiently determines if any DataModel object in the provided
    list shares an ID with another object in the same list. It uses a set to
    achieve O(n) time complexity.

    Args:
        items: A list of DataModel objects to check for duplicate IDs.

    Returns:
        True if no duplicate IDs are found, False otherwise.
        Returns True for an empty list as there are no duplicates.
    """
    if not items:
        return True  # No items, so no duplicates

    seen_ids: Set[int] = set()
    for item in items:
        if item.id in seen_ids:
            return False  # Duplicate ID found
        seen_ids.add(item.id)

    return True  # No duplicates found