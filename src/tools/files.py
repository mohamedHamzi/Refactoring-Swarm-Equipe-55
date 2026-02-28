
import os

# Module-level sandbox directory, set once at startup
_SANDBOX_DIR = None


def set_sandbox_dir(directory: str) -> None:
    """Sets the global sandbox directory for all file operations.
    
    Args:
        directory: The root directory that file operations are restricted to.
    """
    global _SANDBOX_DIR
    _SANDBOX_DIR = os.path.realpath(directory)


def validate_sandbox_path(file_path: str, sandbox_dir: str = None) -> str:
    """Validates that a file path resides within the sandbox directory.
    
    Prevents directory traversal (../), symlink escapes, and absolute path abuse.
    Works on both Windows and Linux.
    
    Args:
        file_path: The path to validate.
        sandbox_dir: Override sandbox dir. Uses global _SANDBOX_DIR if None.
        
    Returns:
        The resolved real absolute path if valid.
        
    Raises:
        PermissionError: If the path resolves outside the sandbox.
        ValueError: If no sandbox directory has been configured.
    """
    effective_sandbox = sandbox_dir or _SANDBOX_DIR
    if effective_sandbox is None:
        raise ValueError("Sandbox directory not configured. Call set_sandbox_dir() first.")
    
    resolved_path = os.path.realpath(file_path)
    resolved_sandbox = os.path.realpath(effective_sandbox)
    
    # Ensure the resolved path starts with the sandbox directory
    # Add os.sep to prevent partial matches (e.g. /sandbox2 matching /sandbox)
    if not (resolved_path.startswith(resolved_sandbox + os.sep) or resolved_path == resolved_sandbox):
        raise PermissionError(
            f"🚫 SANDBOX VIOLATION: Access denied.\n"
            f"   Path '{file_path}' resolves to '{resolved_path}'\n"
            f"   which is outside the sandbox '{resolved_sandbox}'."
        )
    
    return resolved_path


def read_file(file_path: str) -> str:
    """Reads a file and returns its content. Enforces sandbox restrictions."""
    try:
        validated_path = validate_sandbox_path(file_path)
        with open(validated_path, 'r', encoding='utf-8') as f:
            return f.read()
    except PermissionError as e:
        return f"Security Error: {e}"
    except Exception as e:
        return f"Error reading file {file_path}: {e}"


def write_file(file_path: str, content: str) -> str:
    """Writes content to a file. Enforces sandbox restrictions."""
    try:
        validated_path = validate_sandbox_path(file_path)
        with open(validated_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {validated_path}"
    except PermissionError as e:
        return f"Security Error: {e}"
    except Exception as e:
        return f"Error writing to file {file_path}: {e}"


def list_files(directory: str) -> list[str]:
    """Lists all files in a directory recursively."""
    files_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            files_list.append(os.path.join(root, file))
    return files_list
