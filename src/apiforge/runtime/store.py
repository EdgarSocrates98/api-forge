"""Append-only runtime artifacts and normalized replay records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.contracts.agentic import AgentArtifact, AgenticRun, TrajectoryEvent
from apiforge.contracts.base import ContractError
from apiforge.contracts.routing import RoutingDecision, RoutingPlan
from apiforge.contracts.routing_evolution import PromotionGate
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
        temporary = path.with_name(f"{path.name}.tmp")
        temporary.write_text(
            json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        temporary.replace(path)
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

    def save_routing(self, decision: RoutingDecision) -> Path:
        return self._write("routing.json", decision.model_dump(mode="json"))

    def save_routing_plan(self, plan: RoutingPlan) -> Path:
        return self._write("routing-plan.json", plan.model_dump(mode="json"))

    def save_evolution(self, gate: PromotionGate) -> Path:
        return self._write("evolution.json", gate.model_dump(mode="json"))

    def load_evolution(self) -> PromotionGate | None:
        path = self.directory / "evolution.json"
        if not path.is_file():
            return None
        try:
            return PromotionGate.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError("AF-RUNTIME-EVOLUTION", f"{path}: {exc}") from exc

    def load_routing(self) -> RoutingDecision | None:
        path = self.directory / "routing.json"
        if not path.is_file():
            return None
        try:
            return RoutingDecision.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError("AF-RUNTIME-ROUTING", f"{path}: {exc}") from exc

    def load_routing_plan(self) -> RoutingPlan | None:
        path = self.directory / "routing-plan.json"
        if not path.is_file():
            return None
        try:
            return RoutingPlan.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except (OSError, UnicodeDecodeError, ValueError) as exc:
            raise ContractError("AF-RUNTIME-ROUTING-PLAN", f"{path}: {exc}") from exc

    def load_run(self) -> AgenticRun | None:
        path = self.directory / "run.json"
        if not path.is_file():
            return None
        return AgenticRun.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def load_artifact(self, artifact_id: str) -> AgentArtifact | None:
        path = self.directory / "artifacts" / f"{artifact_id.replace(':', '-')}.json"
        if not path.is_file():
            return None
        return AgentArtifact.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def artifact_for_invocation(self, invocation_id: str) -> AgentArtifact | None:
        directory = self.directory / "artifacts"
        if not directory.is_dir():
            return None
        for path in sorted(directory.glob("*.json")):
            artifact = AgentArtifact.model_validate(json.loads(path.read_text(encoding="utf-8")))
            if artifact.invocation_id == invocation_id:
                return artifact
        return None

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
