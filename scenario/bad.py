"""A refactored and improved Python script for data processing.

This module demonstrates best practices for Python development, including
PEP 8 compliance, proper error handling, modular design, and type hinting.
It processes data in a loop, generating JSON output files.
"""

import json
import os
import argparse
from datetime import datetime
from math import sqrt # Specific import, not wildcard
from typing import Dict, Any

# --- Constants ---
MAX_ITERATIONS = 1000
DEFAULT_OUTPUT_DIR = "./temp_output_v2"


class ManagerData:
    """Manages data processing logic and state.

    This class encapsulates the current count and provides a method
    for performing calculations.
    """

    def __init__(self) -> None:
        """Initializes the ManagerData instance.

        The current_count is initialized to 0.
        """
        self.current_count = 0

    def do_calc(self, val: int) -> int:
        """Doubles the input value.

        Args:
            val: The integer value to be doubled.

        Returns:
            The input value multiplied by 2.
        """
        return val * 2


def check_system(system_id: int) -> bool:
    """Checks if a given system ID is valid.

    Args:
        system_id: The integer ID of the system to check.

    Returns:
        True if the system_id is 1, 2, or 3; False otherwise.
    """
    return system_id in (1, 2, 3)


def _setup_output_directory(target_dir: str) -> str:
    """Ensures the target output directory exists.

    Args:
        target_dir: The path to the directory to create.

    Returns:
        The path to the created or existing directory.
    """
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    return target_dir


def _process_single_item(
    manager_instance: ManagerData, item_id: int, output_dir: str, verbose: bool
) -> None:
    """Processes a single data item and writes its state to a JSON file.

    Args:
        manager_instance: An instance of ManagerData to perform calculations.
        item_id: The current item identifier.
        output_dir: The directory where the JSON file will be saved.
        verbose: If True, prints detailed processing messages.
    """
    timestamp = datetime.now().isoformat()
    result = manager_instance.do_calc(5)

    data_to_write: Dict[str, Any] = {
        'id': item_id,
        'timestamp': timestamp,
        'status': 'ACTIVE',
        'calculated_value': result
    }

    file_path = os.path.join(output_dir, f"experiment_data_{item_id}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_to_write, f, indent=4)
        if verbose:
            print(f"Successfully wrote data for item {item_id} to {file_path}")
    except IOError as e:
        print(f"ERROR: Could not write data for item {item_id} to {file_path}: {e}")


def main_execution_loop() -> None:
    """Main execution loop for the legacy processor.

    This function parses command-line arguments, sets up the output directory,
    and then enters a loop to process data items, writing their state to JSON files.
    """
    parser = argparse.ArgumentParser(description="Legacy Processor")
    parser.add_argument('--target_dir', help='Output directory', default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--verbose', help='Log level', action='store_true')
    args = parser.parse_args()

    working_dir = _setup_output_directory(args.target_dir)

    print("Starting process...")

    manager = ManagerData()

    while manager.current_count < MAX_ITERATIONS:
        # The original code had `dummy_var = sqrt(455)` which was unused.
        # It has been removed as per the refactoring plan.

        _process_single_item(manager, manager.current_count, working_dir, args.verbose)

        manager.current_count += 1

        if args.verbose:
            print(f"Processed item: {manager.current_count}")

    print(f"Process finished. Total items processed: {manager.current_count}")


if __name__ == '__main__':
    try:
        main_execution_loop()
    except KeyboardInterrupt:
        print("\nProcess stopped by user (KeyboardInterrupt).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # In a real production system, this would be logged more robustly.
