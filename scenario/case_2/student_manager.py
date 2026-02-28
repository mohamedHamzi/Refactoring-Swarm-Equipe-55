import json
import os

# Custom Exceptions
class StudentManagementError(Exception):
    """Base exception for student management operations."""
    pass

class StudentAlreadyExistsError(StudentManagementError):
    """Raised when trying to add a student that already exists."""
    pass

class StudentNotFoundError(StudentManagementError):
    """Raised when a student is not found."""
    pass

class NoGradesError(StudentManagementError):
    """Raised when trying to get an average for a student with no grades."""
    pass

class NoStudentsWithGradesError(StudentManagementError):
    """Raised when no students in the system have grades."""
    pass

class InvalidDataError(StudentManagementError):
    """Raised when imported data is malformed or invalid."""
    pass


class StudentManager:
    """
    Manages student information and their grades.

    Provides functionalities to add, remove, retrieve students,
    add grades, calculate averages, and export/import data.
    """
    def __init__(self) -> None:
        """
        Initializes the StudentManager with empty lists for students and grades.
        """
        self.students: list[dict[str, str | int]] = []
        self.grades: dict[str, dict[str, float | int]] = {}

    def add_student(self, name: str, age: int) -> None:
        """
        Adds a new student to the manager.

        Args:
            name: The name of the student. Must be a non-empty string.
            age: The age of the student. Must be a positive integer.

        Raises:
            ValueError: If name is empty or not a string, or age is not a positive integer.
            StudentAlreadyExistsError: If a student with the given name already exists.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Student name must be a non-empty string.")
        if not isinstance(age, int) or age <= 0:
            raise ValueError("Student age must be a positive integer.")

        if self.get_student(name.strip()):
            raise StudentAlreadyExistsError(f"Student '{name.strip()}' already exists.")

        self.students.append({"name": name.strip(), "age": age})

    def remove_student(self, name: str) -> None:
        """
        Removes a student and their associated grades from the manager.

        Args:
            name: The name of the student to remove.

        Raises:
            StudentNotFoundError: If the student with the given name is not found.
        """
        found = False
        new_students = []
        for s in self.students:
            if s["name"] == name:
                found = True
            else:
                new_students.append(s)

        if not found:
            raise StudentNotFoundError(f"Student '{name}' not found.")

        self.students = new_students
        if name in self.grades:
            del self.grades[name]

    def get_student(self, name: str) -> dict[str, str | int] | None:
        """
        Retrieves a student's information by name.

        Args:
            name: The name of the student to retrieve.

        Returns:
            A dictionary containing student information if found, otherwise None.
        """
        for s in self.students:
            if s["name"] == name:
                return s
        return None

    def add_grade(self, name: str, subject: str, grade: float | int) -> None:
        """
        Adds a grade for a specific student and subject.

        Args:
            name: The name of the student.
            subject: The subject for which the grade is being added.
            grade: The grade value (0-100).

        Raises:
            StudentNotFoundError: If the student does not exist.
            ValueError: If the grade is not a number between 0 and 100.
        """
        if not self.get_student(name):
            raise StudentNotFoundError(f"Student '{name}' not found. Cannot add grade.")
        if not isinstance(grade, (int, float)) or not (0 <= grade <= 100):
            raise ValueError("Grade must be a number between 0 and 100.")
        if not isinstance(subject, str) or not subject.strip():
            raise ValueError("Subject must be a non-empty string.")

        if name not in self.grades:
            self.grades[name] = {}
        self.grades[name][subject.strip()] = grade

    def get_average(self, name: str) -> float:
        """
        Calculates the average grade for a given student.

        Args:
            name: The name of the student.

        Returns:
            The average grade as a float.

        Raises:
            StudentNotFoundError: If the student has no grades recorded.
            NoGradesError: If the student exists but has no grades.
        """
        if name not in self.grades:
            # This implies the student might not exist or just has no grades.
            # We check self.students to differentiate.
            if not self.get_student(name):
                raise StudentNotFoundError(f"Student '{name}' not found.")
            else:
                raise NoGradesError(f"Student '{name}' has no grades recorded.")

        student_grades = self.grades[name]
        if not student_grades:
            raise NoGradesError(f"Student '{name}' has no grades recorded.")

        total = sum(student_grades.values())
        return total / len(student_grades)

    def get_top_student(self) -> str | None:
        """
        Identifies the student with the highest average grade.

        Returns:
            The name of the top student as a string, or None if no students
            have grades or no students are managed.
        """
        if not self.grades:
            return None

        best_student_name = None
        best_avg = -1.0

        for name in self.grades:
            try:
                avg = self.get_average(name)
                if avg > best_avg:
                    best_avg = avg
                    best_student_name = name
            except NoGradesError:
                # Student exists but has no grades, skip them for top student calculation
                pass
            except StudentNotFoundError:
                # This should ideally not happen if name is from self.grades keys
                pass
        return best_student_name

    def export_json(self, filepath: str) -> None:
        """
        Exports student and grade data to a JSON file.

        Args:
            filepath: The path to the file where data will be saved.

        Raises:
            IOError: If there's an issue writing to the file.
            PermissionError: If there are insufficient permissions to write the file.
            OSError: For other operating system related errors.
        """
        data = {
            "students": self.students,
            "grades": self.grades
        }
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except (IOError, PermissionError, OSError) as e:
            raise IOError(f"Error exporting data to '{filepath}': {e}") from e

    def import_json(self, filepath: str) -> None:
        """
        Imports student and grade data from a JSON file.

        Args:
            filepath: The path to the JSON file to load.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            json.JSONDecodeError: If the file content is not valid JSON.
            InvalidDataError: If the loaded JSON data is malformed or missing expected keys.
            OSError: For other operating system related errors.
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: '{filepath}'") from e
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON format in '{filepath}': {e.msg}", e.doc, e.pos) from e
        except (IOError, OSError) as e:
            raise IOError(f"Error importing data from '{filepath}': {e}") from e

        if not isinstance(data, dict):
            raise InvalidDataError("Imported data is not a dictionary.")
        if "students" not in data or not isinstance(data["students"], list):
            raise InvalidDataError("Imported data missing 'students' key or it's not a list.")
        if "grades" not in data or not isinstance(data["grades"], dict):
            raise InvalidDataError("Imported data missing 'grades' key or it's not a dictionary.")

        # Basic validation for student structure
        for student in data["students"]:
            if not isinstance(student, dict) or "name" not in student or "age" not in student:
                raise InvalidDataError("Malformed student entry in imported data.")
            if not isinstance(student["name"], str) or not isinstance(student["age"], int):
                raise InvalidDataError("Invalid type for student name or age in imported data.")

        # Basic validation for grades structure
        for student_name, student_grades in data["grades"].items():
            if not isinstance(student_name, str) or not isinstance(student_grades, dict):
                raise InvalidDataError("Malformed grades entry in imported data.")
            for subject, grade in student_grades.items():
                if not isinstance(subject, str) or not isinstance(grade, (int, float)):
                    raise InvalidDataError("Invalid type for subject or grade in imported data.")

        self.students = data["students"]
        self.grades = data["grades"]


def calculate_class_average(manager: StudentManager) -> float:
    """
    Calculates the average grade across all students who have grades.

    Args:
        manager: An instance of StudentManager.

    Returns:
        The overall class average as a float. Returns 0.0 if no students have grades.
    """
    if not manager.grades:
        return 0.0

    total_avg = 0.0
    student_count_with_grades = 0
    for name in manager.grades:
        try:
            avg = manager.get_average(name)
            total_avg += avg
            student_count_with_grades += 1
        except NoGradesError:
            # Student exists but has no grades, skip them for class average calculation
            pass
        except StudentNotFoundError:
            # This case should ideally not happen if 'name' comes from manager.grades keys
            pass

    if student_count_with_grades == 0:
        return 0.0
    return total_avg / student_count_with_grades


def main() -> None:
    """
    Main function to demonstrate StudentManager functionality and error handling.
    """
    print("--- Initializing Student Manager ---")
    manager = StudentManager()

    # --- Add Students ---
    print("\n--- Adding Students ---")
    try:
        manager.add_student("Alice", 20)
        manager.add_student("Bob", 22)
        manager.add_student("Charlie", 21)
        print("Students added: Alice, Bob, Charlie")
    except (ValueError, StudentAlreadyExistsError) as e:
        print(f"Error adding student: {e}")

    # Test duplicate student
    try:
        manager.add_student("Alice", 21)
        print("Added duplicate Alice (SHOULD NOT HAPPEN)")
    except StudentAlreadyExistsError as e:
        print(f"Expected error: {e}")
    except ValueError as e:
        print(f"Unexpected error: {e}")

    # Test invalid student input
    try:
        manager.add_student("", 25)
    except ValueError as e:
        print(f"Expected error for empty name: {e}")
    try:
        manager.add_student("David", -5)
    except ValueError as e:
        print(f"Expected error for invalid age: {e}")

    # --- Add Grades ---
    print("\n--- Adding Grades ---")
    try:
        manager.add_grade("Alice", "Math", 85)
        manager.add_grade("Alice", "Science", 90)
        manager.add_grade("Bob", "Math", 70)
        manager.add_grade("Bob", "History", 75)
        print("Grades added for Alice and Bob.")
    except (StudentNotFoundError, ValueError) as e:
        print(f"Error adding grade: {e}")

    # Test adding grade for non-existent student
    try:
        manager.add_grade("Eve", "Art", 95)
    except StudentNotFoundError as e:
        print(f"Expected error for non-existent student: {e}")

    # Test invalid grade
    try:
        manager.add_grade("Alice", "Art", 105)
    except ValueError as e:
        print(f"Expected error for invalid grade: {e}")

    # --- Get Averages ---
    print("\n--- Getting Averages ---")
    try:
        print(f"Alice's average: {manager.get_average('Alice'):.2f}")
    except (StudentNotFoundError, NoGradesError) as e:
        print(f"Error getting Alice's average: {e}")

    try:
        print(f"Bob's average: {manager.get_average('Bob'):.2f}")
    except (StudentNotFoundError, NoGradesError) as e:
        print(f"Error getting Bob's average: {e}")

    # Test student with no grades
    try:
        print(f"Charlie's average: {manager.get_average('Charlie'):.2f}")
    except NoGradesError as e:
        print(f"Expected error for Charlie (no grades): {e}")
    except StudentNotFoundError as e:
        print(f"Unexpected error for Charlie: {e}")

    # --- Top Student ---
    print("\n--- Top Student ---")
    top_student = manager.get_top_student()
    print(f"Top student: {top_student if top_student else 'N/A (no students with grades)'}")

    # --- Class Average ---
    print("\n--- Class Average ---")
    try:
        class_avg = calculate_class_average(manager)
        print(f"Class average: {class_avg:.2f}")
    except NoStudentsWithGradesError as e:
        print(f"Error calculating class average: {e}")

    # --- Remove Student ---
    print("\n--- Removing Student ---")
    try:
        manager.remove_student("Charlie")
        print("Charlie removed.")
    except StudentNotFoundError as e:
        print(f"Error removing Charlie: {e}")

    # Test removing non-existent student
    try:
        manager.remove_student("David")
    except StudentNotFoundError as e:
        print(f"Expected error removing David: {e}")

    # --- Export/Import JSON ---
    print("\n--- Exporting/Importing Data ---")
    filepath = "student_data.json"
    try:
        manager.export_json(filepath)
        print(f"Data exported to {filepath}")

        # Create a new manager to import into
        new_manager = StudentManager()
        new_manager.import_json(filepath)
        print(f"Data imported into new manager from {filepath}")

        print(f"New manager's Alice average: {new_manager.get_average('Alice'):.2f}")
        print(f"New manager's top student: {new_manager.get_top_student()}")

    except (IOError, json.JSONDecodeError, InvalidDataError, StudentManagementError) as e:
        print(f"Error during export/import: {e}")
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Cleaned up {filepath}")

    # Test import with malformed data
    malformed_filepath = "malformed_data.json"
    with open(malformed_filepath, "w") as f:
        f.write('{"students": "not a list", "grades": {}}')
    try:
        malformed_manager = StudentManager()
        malformed_manager.import_json(malformed_filepath)
    except InvalidDataError as e:
        print(f"Expected error for malformed data: {e}")
    finally:
        if os.path.exists(malformed_filepath):
            os.remove(malformed_filepath)

    print("\n--- End of Demonstration ---")


if __name__ == "__main__":
    main()