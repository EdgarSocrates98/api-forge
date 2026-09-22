"""Append-only runtime artifacts and normalized replay records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.contracts.agentic import AgentArtifact, AgenticRun, TrajectoryEvent
from apiforge.contracts.base import ContractError
from apiforge.taskspec import store as task_store


class RunStore:
    def __init__(self, root: Path, task_id: str, run_id: str) -> None:
        self.root = Path(root)
        self.task_id = task_id
        self.run_id = run_id
        self.directory = task_store.task_dir(self.root, task_id) / "runs" / run_id.replace(":", "-")
        self.directory.mkdir(parents=True, exist_ok=True)

    def _write(self, relative: str, payload: object) -> Path:
        path = self.directory / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return path

    def save_run(self, run: AgenticRun) -> Path:
        return self._write("run.json", run.model_dump(mode="json"))

    def event(self, event: TrajectoryEvent) -> Path:
        path = self.directory / "events.jsonl"
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event.model_dump(mode="json"), sort_keys=True) + "\n")
        return path

    def artifact(self, artifact: AgentArtifact) -> Path:
        return self._write(
            f"artifacts/{artifact.artifact_id.replace(':', '-')}.json",
            artifact.model_dump(mode="json"),
        )

    def json(self, name: str, payload: object) -> Path:
        return self._write(name, payload)

    def replay(self) -> dict[str, object]:
        path = self.directory / "events.jsonl"
        events: list[dict[str, Any]] = []
        if path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    item = json.loads(line)
                    item.pop("created_at", None)
                    item.pop("event_id", None)
                    events.append(item)
        return {"run_id": self.run_id, "events": events}


def content_hash(value: object) -> str:
    try:
        encoded = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ContractError("AF-RUNTIME-HASH", str(exc)) from exc
    return hashlib.sha256(encoded).hexdigest()
