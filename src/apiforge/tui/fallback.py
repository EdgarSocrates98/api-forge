"""Rich/JSON fallback for headless terminals and minimal installations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.application.experience_projection import project_status


def render_fallback(root: Path, task_id: str, *, emit: bool = True) -> dict[str, Any]:
    """Render the canonical projection and expose an explicit availability gap."""
    snapshot = project_status(root, task_id, surface="fallback")
    payload = snapshot.model_dump(mode="json") | {
        "code": "AF-TUI-UNAVAILABLE",
        "unlock": "install the optional dependency with `pip install apiforge[tui]`",
    }
    if emit:
        try:
            from rich.console import Console
            from rich.panel import Panel

            Console().print(
                Panel(
                    f"[bold]{snapshot.view.title}[/bold]\n"
                    f"Task: {task_id}\nStatus: {snapshot.view.status}\n"
                    f"Gaps: {', '.join(snapshot.view.gaps) or 'none'}\n\n"
                    "Textual is unavailable; JSON projection follows.",
                    title="API Forge fallback",
                )
            )
        except ImportError:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return payload
