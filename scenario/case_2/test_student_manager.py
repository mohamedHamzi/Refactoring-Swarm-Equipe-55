import pytest
from student_manager import studentManager, calculate_class_average


@pytest.fixture
def manager():
    """Provides a pre-populated student manager."""
    m = studentManager()
    m.add_student("Alice", 20)
    m.add_student("Bob", 22)
    m.add_grade("Alice", "Math", 85)
    m.add_grade("Alice", "Science", 90)
    m.add_grade("Bob", "Math", 70)
    return m


# --- StudentManager Tests ---

def test_add_student(manager):
    """Test adding a student."""
    assert len(manager.students) == 2
    manager.add_student("Charlie", 19)
    assert len(manager.students) == 3


def test_get_student_exists(manager):
    """Test retrieving an existing student."""
    student = manager.get_student("Alice")
    assert student is not None
    assert student["name"] == "Alice"
    assert student["age"] == 20


def test_get_student_not_exists(manager):
    """Test retrieving a non-existent student."""
    assert manager.get_student("Zara") is None


def test_remove_student(manager):
    """Test removing a student."""
    manager.remove_student("Bob")
    assert manager.get_student("Bob") is None
    assert len(manager.students) == 1


def test_remove_student_not_exists(manager):
    """Test removing a student that doesn't exist (should not crash)."""
    manager.remove_student("Nonexistent")
    assert len(manager.students) == 2


def test_add_grade(manager):
    """Test adding a grade."""
    manager.add_grade("Alice", "History", 95)
    assert manager.grades["Alice"]["History"] == 95


def test_get_average(manager):
    """Test average computation."""
    avg = manager.get_average("Alice")
    assert avg == pytest.approx(87.5)  # (85 + 90) / 2


def test_get_average_single_grade(manager):
    """Test average with a single grade."""
    avg = manager.get_average("Bob")
    assert avg == pytest.approx(70.0)


def test_get_top_student(manager):
    """Test finding the top student."""
    top = manager.get_top_student()
    assert top == "Alice"


def test_calculate_class_average(manager):
    """Test class average computation."""
    avg = calculate_class_average(manager)
    # Alice avg = 87.5, Bob avg = 70.0 => class avg = 78.75
    assert avg == pytest.approx(78.75)


def test_get_average_no_grades():
    """Test that getting average with no grades handles gracefully."""
    m = studentManager()
    m.add_student("Empty", 20)
    # This should either return 0 or raise a meaningful error
    # Currently it will crash — the Fixer should fix this
    with pytest.raises((ZeroDivisionError, KeyError)):
        m.get_average("Empty")


def test_calculate_class_average_empty():
    """Test class average with no students."""
    m = studentManager()
    with pytest.raises(ZeroDivisionError):
        calculate_class_average(m)
