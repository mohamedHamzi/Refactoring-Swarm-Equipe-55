import pytest
import threading
from models import DataModel, SHARED_REGISTRY

def test_circular_dependency():
    # This will fail with an ImportError immediately unless circularity is fixed
    m = DataModel(1, {"value": 10})
    assert m.run_processing()["value"] == 110

def test_shallow_copy_bug():
    original_payload = {"value": 10}
    m = DataModel(2, original_payload)
    m.run_processing()
    
    # If it's a shallow copy, the original payload dictionary was modified.
    # A robust system should keep the original input immutable.
    assert original_payload["value"] == 10 

def test_thread_safety():
    # This tests the SHARED_REGISTRY for race conditions
    def worker(id):
        m = DataModel(id, {"val": id})
        m.save()

    threads = []
    for i in range(100):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
        
    assert len(SHARED_REGISTRY) == 100