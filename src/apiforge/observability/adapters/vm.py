"""VM metadata adapter with no host mutation."""

from pathlib import Path


def discover(path: Path) -> dict[str, object]:
    return {"path": str(path), "read_only": True, "exists": path.exists()}
