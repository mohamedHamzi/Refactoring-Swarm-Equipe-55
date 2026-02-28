import threading
from typing import Any, Dict, Optional, TYPE_CHECKING

# To resolve potential circular imports if DataProcessor were in a separate file
# and needed to import DataModel for type hinting, we would use TYPE_CHECKING.
# For this consolidated example, DataProcessor is defined first.
# However, for consistency with the plan's examples of forward references,
# we use string literals for type hints in DataModel's __init__.

# Dummy DataProcessor for demonstration purposes.
# In a real scenario, this would typically be in a separate file (e.g., processor.py).
class DataProcessor:
    """
    A dummy data processor for demonstration.
    In a real application, this would contain actual data transformation logic.
    """
    def transform(self, model: 'DataModel') -> Dict[str, Any]:
        """
        Transforms the data of a given DataModel instance.
        For demonstration, it just adds a 'processed_at' timestamp.

        Args:
            model: The DataModel instance whose data needs to be transformed.

        Returns:
            A dictionary representing the transformed data.
        """
        print(f"Processing data for model {model.id}...")
        # Simulate some processing
        import time # Local import, not a top-level module import
        time.sleep(0.01)
        processed_data = model.data.copy()
        processed_data['processed_at'] = time.time()
        model.processed = True # Update model's state
        print(f"Model {model.id} processed.")
        return processed_data


class DataModelRepository:
    """
    A repository class for managing DataModel instances' data.
    It provides thread-safe storage and retrieval of model data payloads.
    """
    def __init__(self) -> None:
        """
        Initializes the DataModelRepository with an empty storage dictionary
        and a threading lock for thread-safe access.
        """
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def save(self, model: 'DataModel') -> None:
        """
        Saves the data payload of a DataModel instance to the repository
        in a thread-safe manner.

        Args:
            model: The DataModel instance whose data payload is to be saved.
        """
        with self._lock:
            # Storing the model's data payload, not the entire model object
            self._storage[model.id] = model.data
        print(f"Model {model.id} data saved to repository.")

    def get(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the data payload for a given model ID from the repository
        in a thread-safe manner.

        Args:
            model_id: The ID of the model whose data payload to retrieve.

        Returns:
            The data payload (a dictionary) of the model if found, otherwise None.
        """
        with self._lock:
            return self._storage.get(model_id)


class DataModel:
    """
    Represents a data model with a unique identifier, a data payload,
    and a processing status. It interacts with a DataModelRepository for
    persistence and a DataProcessor for data transformations, demonstrating
    dependency injection.
    """
    def __init__(self, id: str, payload: Dict[str, Any], repository: 'DataModelRepository', processor: 'DataProcessor') -> None:
        """
        Initializes a new DataModel instance with its ID, payload,
        and injected dependencies for repository and processor.

        Args:
            id: A unique string identifier for the data model.
            payload: A dictionary containing the data content of the model.
            repository: An instance of DataModelRepository for handling data persistence.
            processor: An instance of DataProcessor for performing data transformations.
        """
        self.id: str = id
        self.data: Dict[str, Any] = payload
        self.processed: bool = False
        self._repository: 'DataModelRepository' = repository
        self._processor: 'DataProcessor' = processor

    def save(self) -> None:
        """
        Delegates the saving of the DataModel's current state to its
        associated DataModelRepository. The repository handles the actual
        storage mechanism and thread-safety.
        """
        self._repository.save(self)
        print(f"Model {self.id} requested save to repository.")

    def run_processing(self) -> Dict[str, Any]:
        """
        Triggers the data processing for this model by invoking the
        transform method of its associated DataProcessor.

        Returns:
            A dictionary representing the transformed data, as returned by the processor.
        """
        return self._processor.transform(self)