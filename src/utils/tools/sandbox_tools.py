from pathlib import Path

BASE_SANDBOX = Path("sandbox").resolve()

def ensure_safe_path(path: Path) -> Path:
    """
    Ensures the given path is inside the sandbox directory.
    Prevents path traversal attacks.
    """
    resolved_path = path.resolve()

    if not str(resolved_path).startswith(str(BASE_SANDBOX)):
        raise ValueError(f"Unsafe path detected: {resolved_path}")

    return resolved_path