"""CLI projections for governed memory, blackboard and semantic checkpoints."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

import typer

memory_app = typer.Typer(name="memory", help="Governed append-only agent memory.", no_args_is_help=True)
blackboard_app = typer.Typer(name="blackboard", help="Structured append-only shared state.", no_args_is_help=True)


def _payload(value: str) -> object:
    path = Path(value)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def register(app: typer.Typer, runtime_app: typer.Typer) -> None:
    app.add_typer(memory_app)
    app.add_typer(blackboard_app)

    @memory_app.command("propose")
    def memory_propose(
        scope: str = typer.Option(..., "--scope"),
        origin: str = typer.Option(..., "--origin"),
        payload: str = typer.Option(..., "--payload", help="JSON value or JSON file."),
        proposed_by: str = typer.Option(..., "--by"),
        reason: str = typer.Option(..., "--reason"),
        created_at: str = typer.Option(..., "--now"),
        observed_at: str | None = typer.Option(None, "--observed-at"),
        expires_at: str | None = typer.Option(None, "--expires-at"),
        trust_level: str = typer.Option("candidate", "--trust"),
        provenance: list[str] = typer.Option([], "--provenance"),
        evidence: list[str] = typer.Option([], "--evidence"),
        environment: str | None = typer.Option(None, "--environment"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.cli import _echo_json, _run
        from apiforge.memory.store import propose_memory

        _echo_json(
            _run(lambda: propose_memory(
                root, scope=scope, origin=origin, payload=_payload(payload), proposed_by=proposed_by,
                reason=reason, created_at=created_at, observed_at=observed_at, expires_at=expires_at,
                trust_level=trust_level, provenance=tuple(provenance), evidence_refs=tuple(evidence),
                environment_fingerprint=environment,
            )),
            detail_level,
        )

    @memory_app.command("persist")
    def memory_persist(
        candidate_id: str = typer.Option(..., "--candidate-id"),
        policy: str = typer.Option("default", "--policy"),
        now: str = typer.Option(..., "--now"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_memory import MemoryPolicy
        from apiforge.memory.store import load_candidate, persist_candidate

        _echo_json(_run(lambda: persist_candidate(
            root, load_candidate(root, candidate_id), MemoryPolicy(policy_id=policy), now=now
        )), detail_level)

    @memory_app.command("search")
    def memory_search(
        term: list[str] = typer.Option([], "--term"),
        scope: list[str] = typer.Option([], "--scope"),
        environment: str | None = typer.Option(None, "--environment"),
        minimum_trust: str = typer.Option("unknown", "--minimum-trust"),
        now: str | None = typer.Option(None, "--now"),
        include_invalidated: bool = typer.Option(False, "--include-invalidated"),
        max_results: int = typer.Option(20, "--max-results"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_memory import MemoryQuery, MemoryScope, TrustLevel
        from apiforge.memory.store import query_memory

        query = MemoryQuery(
            terms=tuple(term), scopes=tuple(cast(MemoryScope, item) for item in scope),
            environment_fingerprint=environment, now=now,
            minimum_trust=cast(TrustLevel, minimum_trust), include_invalidated=include_invalidated,
            max_results=max_results,
        )
        _echo_json(_run(lambda: query_memory(root, query)), detail_level)

    @memory_app.command("invalidate")
    def memory_invalidate(
        memory_id: str = typer.Option(..., "--memory-id"),
        reason: str = typer.Option(..., "--reason"),
        by: str = typer.Option(..., "--by"),
        now: str = typer.Option(..., "--now"),
        evidence: list[str] = typer.Option([], "--evidence"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.cli import _echo_json, _run
        from apiforge.memory.store import invalidate_memory

        _echo_json(_run(lambda: invalidate_memory(
            root, memory_id, reason=reason, invalidated_by=by, created_at=now, evidence_refs=tuple(evidence)
        )), detail_level)

    @blackboard_app.command("append")
    def blackboard_append(
        task_id: str = typer.Option(..., "--task-id"),
        scope: str = typer.Option(..., "--scope"),
        kind: str = typer.Option(..., "--kind"),
        origin: str = typer.Option(..., "--origin"),
        payload: str = typer.Option(..., "--payload", help="JSON value or JSON file."),
        now: str = typer.Option(..., "--now"),
        trust_level: str = typer.Option("unknown", "--trust"),
        taint: list[str] = typer.Option([], "--taint"),
        provenance: list[str] = typer.Option([], "--provenance"),
        evidence: list[str] = typer.Option([], "--evidence"),
        supersedes: list[str] = typer.Option([], "--supersedes"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.blackboard.store import append_entry
        from apiforge.cli import _echo_json, _run

        _echo_json(_run(lambda: append_entry(
            root, task_id=task_id, scope=scope, kind=kind, origin=origin, payload=_payload(payload),
            created_at=now, trust_level=trust_level, taint=tuple(taint), provenance=tuple(provenance),
            evidence_refs=tuple(evidence), supersedes=tuple(supersedes),
        )), detail_level)

    @blackboard_app.command("query")
    def blackboard_query(
        task_id: str = typer.Option(..., "--task-id"),
        kind: list[str] = typer.Option([], "--kind"),
        scope: str | None = typer.Option(None, "--scope"),
        term: list[str] = typer.Option([], "--term"),
        max_results: int = typer.Option(50, "--max-results"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.blackboard.store import query_entries
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_memory import BlackboardKind, BlackboardQuery

        query = BlackboardQuery(
            task_id=task_id, kinds=tuple(cast(BlackboardKind, item) for item in kind),
            scope=scope, terms=tuple(term), max_results=max_results,
        )
        _echo_json(_run(lambda: query_entries(root, query)), detail_level)

    @runtime_app.command("semantic-checkpoint")
    def semantic_checkpoint(
        state_file: Path = typer.Option(..., "--state", help="JSON object matching SemanticCheckpoint fields."),
        task_id: str = typer.Option(..., "--task-id"),
        run_id: str = typer.Option(..., "--run-id"),
        now: str = typer.Option(..., "--now"),
        root: Path = typer.Option(Path("."), "--root"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        from apiforge.cli import _echo_json, _run
        from apiforge.runtime.semantic_checkpoint import build_checkpoint, save_checkpoint

        def work() -> dict[str, object]:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            checkpoint = build_checkpoint(task_id=task_id, run_id=run_id, created_at=now, **data)
            return {"checkpoint": checkpoint.model_dump(mode="json"), "path": str(save_checkpoint(root, checkpoint))}

        _echo_json(_run(work), detail_level)


__all__ = ["blackboard_app", "memory_app", "register"]
