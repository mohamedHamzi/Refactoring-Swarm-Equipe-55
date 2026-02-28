from processor import DataModel, DataProcessor, bulk_process
import pytest
import copy

class TestDataModel:
    """
    Tests for the DataModel class.
    """
    def test_datamodel_init(self):
        """
        Test DataModel initialization with basic data.
        """
        model_id = 1
        model_data = {"key": "value", "number": 10}
        model = DataModel(model_id, model_data)

        assert model.id == model_id
        assert model.data == model_data
        assert model.processed is False

    def test_datamodel_empty_data(self):
        """
        Test DataModel initialization with an empty dictionary for data.
        """
        model_id = 2
        model_data = {}
        model = DataModel(model_id, model_data)

        assert model.id == model_id
        assert model.data == model_data
        assert model.processed is False

    def test_datamodel_data_is_mutable_reference(self):
        """
        Verify that the `data` attribute is a reference to the passed dictionary,
        which means external modifications would affect it if not handled by processor.
        """
        original_data = {"a": 1}
        model = DataModel(3, original_data)
        assert model.data is original_data

        original_data["b"] = 2
        assert model.data == {"a": 1, "b": 2}

class TestDataProcessor:
    """
    Tests for the DataProcessor class.
    """
    def test_dataproces_init(self):
        """
        Test DataProcessor initialization.
        """
        processor = DataProcessor()
        assert isinstance(processor.history, list)
        assert len(processor.history) == 0

    def test_dataproces_transform_with_value_key(self):
        """
        Test transformation when the 'value' key is present in data.
        Ensures value is incremented, model is marked processed, history is updated,
        and original model data is not modified.
        """
        processor = DataProcessor()
        original_data = {"name": "test", "value": 50}
        model = DataModel(1, copy.deepcopy(original_data)) # Use deepcopy to ensure original_data is truly separate

        transformed_data = processor.transform(model)

        # Assert returned data
        assert transformed_data == {"name": "test", "value": 150}
        # Assert model state
        assert model.processed is True
        assert model.data == original_data # Original model data should remain unchanged
        # Assert history
        assert len(processor.history) == 1
        assert processor.history[0] == {"name": "test", "value": 150}
        # Ensure history stores a deep copy, not a reference to transformed_data
        transformed_data["new_key"] = "modified"
        assert processor.history[0] == {"name": "test", "value": 150}

    def test_dataproces_transform_without_value_key(self):
        """
        Test transformation when the 'value' key is not present in data.
        Ensures data remains unchanged, model is marked processed, history is updated,
        and original model data is not modified.
        """
        processor = DataProcessor()
        original_data = {"name": "test", "age": 30}
        model = DataModel(2, copy.deepcopy(original_data))

        transformed_data = processor.transform(model)

        # Assert returned data
        assert transformed_data == {"name": "test", "age": 30}
        # Assert model state
        assert model.processed is True
        assert model.data == original_data # Original model data should remain unchanged
        # Assert history
        assert len(processor.history) == 1
        assert processor.history[0] == {"name": "test", "age": 30}

    def test_dataproces_transform_empty_data(self):
        """
        Test transformation with an empty data dictionary.
        """
        processor = DataProcessor()
        original_data = {}
        model = DataModel(3, copy.deepcopy(original_data))

        transformed_data = processor.transform(model)

        # Assert returned data
        assert transformed_data == {}
        # Assert model state
        assert model.processed is True
        assert model.data == original_data # Original model data should remain unchanged
        # Assert history
        assert len(processor.history) == 1
        assert processor.history[0] == {}

    def test_dataproces_transform_multiple_calls(self):
        """
        Test multiple transformation calls and verify history accumulation.
        """
        processor = DataProcessor()
        model1_data = {"value": 10}
        model1 = DataModel(1, copy.deepcopy(model1_data))

        model2_data = {"key": "data"}
        model2 = DataModel(2, copy.deepcopy(model2_data))

        transformed_data1 = processor.transform(model1)
        transformed_data2 = processor.transform(model2)

        assert transformed_data1 == {"value": 110}
        assert transformed_data2 == {"key": "data"}

        assert model1.processed is True
        assert model2.processed is True

        assert len(processor.history) == 2
        assert processor.history[0] == {"value": 110}
        assert processor.history[1] == {"key": "data"}

        assert model1.data == model1_data # Original data untouched
        assert model2.data == model2_data # Original data untouched

    def test_dataproces_transform_history_deep_copy_integrity(self):
        """
        Ensure that the data appended to history is a deep copy and
        subsequent modifications to the returned transformed data or original model data
        do not affect the history.
        """
        processor = DataProcessor()
        original_data = {"value": 10, "list_data": [1, 2]}
        model = DataModel(1, copy.deepcopy(original_data))

        transformed_data = processor.transform(model)

        # Modify the returned transformed_data
        transformed_data["value"] = 999
        transformed_data["list_data"].append(3)
        transformed_data["new_key"] = "added"

        # Check history: it should be unaffected by changes to `transformed_data`
        assert processor.history[0] == {"value": 110, "list_data": [1, 2]}

        # Modify the original model's data *after* transformation
        model.data["value"] = 500
        model.data["list_data"].append(4)
        model.data["another_key"] = "original_modified"

        # Check history again: it should still be unaffected
        assert processor.history[0] == {"value": 110, "list_data": [1, 2]}
        # Check model's data: it should reflect the post-transformation modifications
        assert model.data == {"value": 500, "list_data": [1, 2, 4], "another_key": "original_modified"}


class TestBulkProcess:
    """
    Tests for the bulk_process function.
    """
    def test_bulk_process_empty_list(self):
        """
        Test with an empty list of DataModel objects.
        """
        assert bulk_process([]) is True

    def test_bulk_process_single_item(self):
        """
        Test with a single DataModel object.
        """
        model = DataModel(1, {})
        assert bulk_process([model]) is True

    def test_bulk_process_no_duplicates(self):
        """
        Test with a list of DataModel objects with unique IDs.
        """
        models = [
            DataModel(1, {}),
            DataModel(2, {}),
            DataModel(3, {})
        ]
        assert bulk_process(models) is True

    def test_bulk_process_with_duplicates_at_start(self):
        """
        Test with duplicate IDs at the beginning of the list.
        """
        models = [
            DataModel(1, {}),
            DataModel(1, {}),
            DataModel(2, {})
        ]
        assert bulk_process(models) is False

    def test_bulk_process_with_duplicates_at_end(self):
        """
        Test with duplicate IDs at the end of the list.
        """
        models = [
            DataModel(1, {}),
            DataModel(2, {}),
            DataModel(2, {})
        ]
        assert bulk_process(models) is False

    def test_bulk_process_with_duplicates_in_middle(self):
        """
        Test with duplicate IDs in the middle of the list.
        """
        models = [
            DataModel(1, {}),
            DataModel(2, {}),
            DataModel(1, {}),
            DataModel(3, {})
        ]
        assert bulk_process(models) is False

    def test_bulk_process_all_duplicates(self):
        """
        Test with all DataModel objects having the same ID.
        """
        models = [
            DataModel(5, {}),
            DataModel(5, {}),
            DataModel(5, {})
        ]
        assert bulk_process(models) is False

    def test_bulk_process_large_list_no_duplicates(self):
        """
        Test with a large list of unique DataModel objects.
        """
        models = [DataModel(i, {}) for i in range(1000)]
        assert bulk_process(models) is True

    def test_bulk_process_large_list_with_duplicates(self):
        """
        Test with a large list containing one duplicate.
        """
        models = [DataModel(i, {}) for i in range(1000)]
        models.append(DataModel(500, {})) # Add a duplicate
        assert bulk_process(models) is False

    def test_bulk_process_ids_zero_and_negative(self):
        """
        Test with zero and negative IDs, ensuring they are handled correctly.
        """
        models_unique = [
            DataModel(0, {}),
            DataModel(-1, {}),
            DataModel(10, {})
        ]
        assert bulk_process(models_unique) is True

        models_duplicate = [
            DataModel(0, {}),
            DataModel(-1, {}),
            DataModel(0, {})
        ]
        assert bulk_process(models_duplicate) is False

        models_negative_duplicate = [
            DataModel(1, {}),
            DataModel(-5, {}),
            DataModel(-5, {})
        ]
        assert bulk_process(models_negative_duplicate) is False