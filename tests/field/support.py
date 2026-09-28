import json
from pathlib import Path
from typing import Any

import yaml

OWN = "sha256:" + "a" * 64
OSS = "oss:open-telemetry/opentelemetry-demo@abc123"


def corpus(root: Path, *, tasks: list[dict[str, Any]] | None = None, **extra: Any) -> Path:
    field = root / "docs" / "field"
    field.mkdir(parents=True, exist_ok=True)
    (field / "hypothesis.md").write_text("# H1\ngraph_gap dominates\n", encoding="utf-8")
    data: dict[str, Any] = {
        "schema": "apiforge/field-corpus/v1",
        "cycle_started_at": None,
        "gate": {"min_tasks_per_theme": 5, "min_repos_per_theme": 2},
        "hypothesis": {"id": "H1", "category": "graph_gap", "refutation": "other theme wins"},
        "repos": [{"ref": OWN, "kind": "own"}, {"ref": OSS, "kind": "oss"}],
        "tasks": tasks
        if tasks is not None
        else [
            {
                "id": "T001",
                "scenario": "incident",
                "repo_ref": OSS,
                "registered_at": "2026-10-01T09:00:00Z",
                "prompt": "checkout latency spike after flag enabled; find cause",
                "ground_truth": {"kind": "injected_failure", "ref": "flag paymentFailure"},
            }
        ],
        **extra,
    }
    path = field / "corpus.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def task(
    task_id: str,
    *,
    scenario: str = "multi_repo",
    repo_ref: str = OSS,
    at: str = "2026-10-01T09:00:00Z",
) -> dict[str, Any]:
    return {
        "id": task_id,
        "scenario": scenario,
        "repo_ref": repo_ref,
        "registered_at": at,
        "prompt": f"task {task_id}",
        "ground_truth": {"kind": "fix_commit", "ref": "deadbeef"},
    }


def runtime_run(
    root: Path,
    run_id: str,
    *,
    calls_used: int = 3,
    updated_at: str = "2026-10-02T10:05:00Z",
    context_bytes: int = 1200,
    cache_hits: int = 2,
    verbs: tuple[str, ...] = ("context.capsule",),
    summary: bool = True,
    checkpoint: bool = True,
    ledger: bool = True,
) -> Path:
    directory = root / ".apiforge" / "tasks" / "task-x" / "runs" / run_id
    directory.mkdir(parents=True, exist_ok=True)
    if summary:
        (directory / "summary.json").write_text(
            json.dumps({"run_id": run_id, "unresolved": {"routing": ["no-route"]}, "errors": []}),
            encoding="utf-8",
        )
    if checkpoint:
        (directory / "economy_checkpoint.json").write_text(
            json.dumps({"run_id": run_id, "calls_used": calls_used, "updated_at": updated_at}),
            encoding="utf-8",
        )
    if ledger:
        path = root / ".apiforge" / "economy.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            for verb in verbs:
                fh.write(
                    json.dumps(
                        {
                            "run_id": run_id,
                            "verb": verb,
                            "source": "graph",
                            "payload_bytes": 0,
                            "cost": {"context_bytes": context_bytes, "cache_hits": cache_hits},
                        }
                    )
                    + "\n"
                )
    return directory


STARTED = "2026-10-02T10:00:00Z"
ENDED = "2026-10-02T10:30:00Z"
