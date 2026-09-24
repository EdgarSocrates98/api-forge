"""Optional Textual UX with a deterministic headless fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def is_available() -> bool:
    try:
        import textual  # noqa: F401
    except ImportError:
        return False
    return True


def run_tui(root: Path, task_id: str, *, force_fallback: bool = False) -> dict[str, Any]:
    """Run the visual app when installed, otherwise render the same projection."""
    if force_fallback or not is_available():
        from apiforge.tui.fallback import render_fallback

        return render_fallback(root, task_id)
    from apiforge.tui.app import ForgeApp

    ForgeApp(root=root, task_id=task_id).run()
    return {"status": "closed", "task_id": task_id, "surface": "textual"}


__all__ = ["is_available", "run_tui"]
