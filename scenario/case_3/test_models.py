import pytest
import threading
import time
from unittest.mock import MagicMock, patch
from models import DataProcessor, DataModelRepository, DataModel
import queue # For thread-safe communication in tests

# --- DataProcessor Tests ---

def test_data_processor_transform_basic():
    """
    Tests the basic functionality of DataProcessor.transform:
    - Adds 'processed_at' timestamp.
    - Copies original data.
    - Updates model.processed state.
    """
    processor = DataProcessor()
    # Mock DataModel for the processor to interact with
    mock_model = MagicMock()
    mock_model.id = "test_id_1"
    mock_model.data = {"key1": "value1", "key2": 123}
    mock_model.processed = False

    transformed_data = processor.transform(mock_model)

    assert "processed_at" in transformed_data
    assert isinstance(transformed_data["processed_at"], float)
    assert transformed_data["key1"] == "value1"
    assert transformed_data["key2"] == 123
    assert mock_model.processed is True # Verify model state updated
    assert transformed_data is not mock_model.data # Ensure a copy is returned

def test_data_processor_transform_empty_payload():
    """
    Tests DataProcessor.transform with an empty data payload.
    """
    processor = DataProcessor()
    mock_model = MagicMock()
    mock_model.id = "test_id_empty"
    mock_model.data = {}
    mock_model.processed = False

    transformed_data = processor.transform(mock_model)

    assert "processed_at" in transformed_data
    assert isinstance(transformed_data["processed_at"], float)
    assert len(transformed_data) == 1 # Only processed_at should be there
    assert mock_model.processed is True

def test_data_processor_transform_updates_model_state():
    """
    Verifies that DataProcessor.transform correctly sets the model's 'processed' attribute to True.
    """
    processor = DataProcessor()
    mock_model = MagicMock()
    mock_model.id = "test_id_state"
    mock_model.data = {"status": "pending"}
    mock_model.processed = False

    processor.transform(mock_model)

    assert mock_model.processed is True

def test_data_processor_transform_with_existing_processed_at():
    """
    Tests that 'processed_at' is updated even if it already exists in the payload.
    """
    processor = DataProcessor()
    mock_model = MagicMock()
    mock_model.id = "test_id_existing_ts"
    mock_model.data = {"key": "value", "processed_at": 100.0}
    mock_model.processed = False

    transformed_data = processor.transform(mock_model)

    assert "processed_at" in transformed_data
    assert transformed_data["processed_at"] != 100.0 # Should be updated to a new timestamp
    assert transformed_data["key"] == "value"
    assert mock_model.processed is True

# --- DataModelRepository Tests ---

def test_repository_init():
    """
    Tests the initialization of DataModelRepository.
    """
    repo = DataModelRepository()
    assert repo._storage == {}
    assert isinstance(repo._lock, threading.Lock)

def test_repository_save_and_get_basic():
    """
    Tests saving and retrieving data payloads from the repository.
    """
    repo = DataModelRepository()
    mock_model = MagicMock()
    mock_model.id = "model_1"
    mock_model.data = {"name": "Test Model 1", "value": 100}

    repo.save(mock_model)
    retrieved_data = repo.get("model_1")

    assert retrieved_data == {"name": "Test Model 1", "value": 100}
    # Ensure the repository stores a copy, not a reference to the original model's data
    assert retrieved_data is not mock_model.data

def test_repository_get_non_existent():
    """
    Tests retrieving data for an ID that does not exist in the repository.
    """
    repo = DataModelRepository()
    retrieved_data = repo.get("non_existent_id")
    assert retrieved_data is None

def test_repository_save_overwrites_existing():
    """
    Tests that saving a model with an existing ID overwrites its data.
    """
    repo = DataModelRepository()
    mock_model_1 = MagicMock()
    mock_model_1.id = "model_overwrite"
    mock_model_1.data = {"version": 1}

    repo.save(mock_model_1)
    assert repo.get("model_overwrite") == {"version": 1}

    mock_model_2 = MagicMock()
    mock_model_2.id = "model_overwrite"
    mock_model_2.data = {"version": 2, "status": "updated"}

    repo.save(mock_model_2)
    assert repo.get("model_overwrite") == {"version": 2, "status": "updated"}

def test_repository_thread_safety_save():
    """
    Tests the thread-safe saving mechanism of the repository.
    Multiple threads save different models concurrently.
    """
    repo = DataModelRepository()
    num_threads = 10
    models_to_save = []
    for i in range(num_threads):
        mock_model = MagicMock()
        mock_model.id = f"thread_model_{i}"
        mock_model.data = {"thread_num": i, "data": f"payload_{i}"}
        models_to_save.append(mock_model)

    def save_model_task(model):
        repo.save(model)

    threads = []
    for model in models_to_save:
        thread = threading.Thread(target=save_model_task, args=(model,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    assert len(repo._storage) == num_threads
    for model in models_to_save:
        retrieved_data = repo.get(model.id)
        assert retrieved_data == model.data

def test_repository_thread_safety_get():
    """
    Tests the thread-safe retrieval mechanism of the repository.
    Multiple threads get data concurrently.
    """
    repo = DataModelRepository()
    # Pre-populate some data
    repo._storage["model_a"] = {"value": "A"}
    repo._storage["model_b"] = {"value": "B"}

    num_threads = 10
    results_queue = queue.Queue()

    def get_model_task(model_id):
        data = repo.get(model_id)
        results_queue.put((model_id, data))

    threads = []
    for i in range(num_threads):
        model_id = "model_a" if i % 2 == 0 else "model_b"
        thread = threading.Thread(target=get_model_task, args=(model_id,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Verify that all expected data was retrieved without errors
    retrieved_counts = {"model_a": 0, "model_b": 0}
    while not results_queue.empty():
        model_id, data = results_queue.get()
        if model_id == "model_a":
            assert data == {"value": "A"}
            retrieved_counts["model_a"] += 1
        elif model_id == "model_b":
            assert data == {"value": "B"}
            retrieved_counts["model_b"] += 1
    
    assert retrieved_counts["model_a"] == num_threads // 2 + (num_threads % 2)
    assert retrieved_counts["model_b"] == num_threads // 2
    # This test primarily ensures no deadlocks or exceptions during concurrent reads.

# --- DataModel Tests ---

def test_data_model_init():
    """
    Tests the initialization of a DataModel instance.
    """
    mock_repo = MagicMock(spec=DataModelRepository)
    mock_processor = MagicMock(spec=DataProcessor)
    model_id = "init_model"
    payload = {"data_key": "data_value"}

    model = DataModel(model_id, payload, mock_repo, mock_processor)

    assert model.id == model_id
    assert model.data == payload
    assert model.processed is False
    assert model._repository is mock_repo
    assert model._processor is mock_processor

def test_data_model_save_delegates_to_repository():
    """
    Tests that DataModel.save delegates the call to its injected repository.
    """
    mock_repo = MagicMock(spec=DataModelRepository)
    mock_processor = MagicMock(spec=DataProcessor)
    model = DataModel("save_model", {"key": "value"}, mock_repo, mock_processor)

    model.save()

    mock_repo.save.assert_called_once_with(model)

def test_data_model_run_processing_delegates_to_processor():
    """
    Tests that DataModel.run_processing delegates the call to its injected processor
    and returns the result from the processor.
    """
    mock_repo = MagicMock(spec=DataModelRepository)
    mock_processor = MagicMock(spec=DataProcessor)
    # Configure the mock processor to return a specific value
    expected_transformed_data = {"original": "data", "processed_at": 123.45}
    mock_processor.transform.return_value = expected_transformed_data

    model = DataModel("process_model", {"key": "value"}, mock_repo, mock_processor)

    transformed_data = model.run_processing()

    mock_processor.transform.assert_called_once_with(model)
    assert transformed_data == expected_transformed_data

def test_data_model_initial_processed_state():
    """
    Verifies that a new DataModel instance has 'processed' set to False by default.
    """
    mock_repo = MagicMock(spec=DataModelRepository)
    mock_processor = MagicMock(spec=DataProcessor)
    model = DataModel("initial_state_model", {"status": "new"}, mock_repo, mock_processor)

    assert model.processed is False

def test_data_model_integration_with_processor_state_update():
    """
    Tests the integration between DataModel and DataProcessor,
    specifically verifying that the DataModel's 'processed' state is updated
    by the real DataProcessor.
    """
    processor = DataProcessor() # Use a real processor
    mock_repo = MagicMock(spec=DataModelRepository) # Mock repo as it's not the focus

    model = DataModel("integration_model", {"item": "A"}, mock_repo, processor)

    assert model.processed is False
    transformed_data = model.run_processing()
    assert model.processed is True # DataModel's 'processed' attribute should be updated by the processor
    assert "processed_at" in transformed_data
    assert transformed_data["item"] == "A"

def test_data_model_integration_with_repository_data_persistence():
    """
    Tests the integration between DataModel and DataModelRepository,
    verifying that DataModel correctly persists its data via the real repository.
    """
    repo = DataModelRepository() # Use a real repository
    mock_processor = MagicMock(spec=DataProcessor) # Mock processor as it's not the focus

    model_id = "persistence_model"
    initial_data = {"item": "B", "count": 5}
    model = DataModel(model_id, initial_data, repo, mock_processor)

    model.save()

    retrieved_data = repo.get(model_id)
    assert retrieved_data == initial_data
    assert retrieved_data is not initial_data # Ensure repository stores a copy of the data