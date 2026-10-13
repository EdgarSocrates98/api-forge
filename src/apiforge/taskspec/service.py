"""Task lifecycle: create, review, seal, ready, run, accept — the verbs.

Invariants held here:

- a review bumps ``revision`` and produces a new ``TaskRevision`` — any
  content change therefore invalidates a prior seal by construction;
- ``seal`` is a distinct verb from ``run``: the signer needs the private
  key, the executor never does;
- ``accept`` requires ``awaiting_supervision`` and an ``accepted_by``
  distinct from the recorded ``executed_by``;
- a run that makes zero progress ends ``blocked`` — never silently retried.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.task import (
    TaskRevision,
    TaskSpec,
    TaskState,
)
from apiforge.core.yaml import StrictYamlError, load_yaml_mapping
from apiforge.taskspec import store
from apiforge.taskspec.machine import require_transition

_CTX_FIELDS = (
    "project",
    "contract",
    "baseline",
    "candidate",
    "input_path",
    "findings",
    "case",
)


def _transition(root: Path, spec: TaskSpec, target: TaskState, event: dict[str, Any]) -> TaskSpec:
    require_transition(spec.state, target)
    updated = spec.model_copy(update={"state": target})
    store.write_spec(store.task_dir(root, spec.id), updated)
    store.record_event(root, spec.id, {"event": f"->{target.value}", **event})
    return updated


def _revision(root: Path, task_id: str, revision: int) -> TaskRevision:
    path = store.task_dir(root, task_id) / "revisions" / f"{revision}.json"
    if not path.is_file():
        raise ContractError(
            "AF-TASK-REVISION-MISSING",
            f"task {task_id!r} has no revision {revision}",
        )
    return TaskRevision.model_validate(json.loads(path.read_text(encoding="utf-8")))


def create_task(root: Path, spec: TaskSpec) -> TaskSpec:
    if spec.state is not TaskState.DRAFT:
        raise ContractError("AF-TASK-TRANSITION", "new tasks start in draft")
    return store.create(root, spec)


def review_task(
    root: Path,
    task_id: str,
    actor: str,
    set_fields: dict[str, str] | None = None,
) -> TaskSpec:
    """Approve the current content — or amend it, which bumps the revision.

    ``set_fields`` applies `field=value` changes to scalars only; any change
    creates a new revision so a prior seal no longer matches.
    """
    spec = store.load(root, task_id)
    allowed = (
        TaskState.DRAFT,
        TaskState.REVIEWED,
        TaskState.REJECTED,
        TaskState.SEALED,  # amending a sealed task yields a new unsealed revision
    )
    if spec.state not in allowed:
        raise ContractError(
            "AF-TASK-TRANSITION",
            f"review allowed from draft/reviewed/rejected/sealed, not {spec.state.value}",
        )
    changes: dict[str, Any] = {}
    for field, value in (set_fields or {}).items():
        if field not in type(spec).model_fields:
            raise ContractError("AF-TASK-FIELD", f"unknown task field {field!r}")
        current = getattr(spec, field)
        if not isinstance(current, (str, int, type(None))):
            raise ContractError(
                "AF-TASK-FIELD", f"field {field!r} is not a scalar — amend via spec file"
            )
        changes[field] = value
    revision = spec.revision + 1
    updated = spec.model_copy(update={"state": TaskState.REVIEWED, "revision": revision, **changes})
    changed = tuple(sorted(changes)) or ("approval",)
    store.save_revision(root, updated, changed)
    store.record_event(
        root,
        task_id,
        {"event": "reviewed", "revision": revision, "by": actor, "changed": changed},
    )
    return updated


def seal_task(root: Path, task_id: str, key_path: Path, actor: str) -> TaskSpec:
    """Ed25519-seal the current revision — key possession, never identity."""
    spec = store.load(root, task_id)
    require_transition(spec.state, TaskState.SEALED)
    revision = _revision(root, task_id, spec.revision)
    if revision.seal_signature_b64 is not None:
        raise ContractError("AF-TASK-SEALED", f"revision {revision.revision} is already sealed")
    from apiforge.report.keys import private_key_fingerprint, sign_payload

    block = {
        "task_id": task_id,
        "revision": revision.revision,
        "content_sha256": revision.content_sha256,
    }
    sealed = revision.model_copy(
        update={
            "sealed_by": actor,
            "seal_signature_b64": sign_payload(key_path, block),
            "public_key_sha256": private_key_fingerprint(key_path),
        }
    )
    store.save_seal(root, sealed)
    return _transition(
        root,
        spec,
        TaskState.SEALED,
        {"revision": revision.revision, "by": actor},
    )


def ready_task(root: Path, task_id: str) -> TaskSpec:
    """sealed -> ready: the plan is bound to the sealed revision."""
    spec = store.load(root, task_id)
    try:
        revision = _revision(root, task_id, spec.revision)
    except ContractError:
        revision = None
    if spec.state is TaskState.REVIEWED and (
        revision is None or revision.seal_signature_b64 is None
    ):
        raise ContractError(
            "AF-TASK-UNSEALED",
            f"revision {spec.revision} is not sealed — run `task seal` first",
        )
    require_transition(spec.state, TaskState.READY)
    if revision is not None and revision.seal_signature_b64 is None:
        raise ContractError(
            "AF-TASK-UNSEALED",
            f"revision {revision.revision} is not sealed — run `task seal` first",
        )
    return _transition(root, spec, TaskState.READY, {"revision": spec.revision})


def _parse_inputs(spec: TaskSpec) -> dict[str, Any]:
    ctx: dict[str, Any] = {}
    for item in spec.inputs:
        key, sep, value = item.partition("=")
        if not sep:
            raise ContractError("AF-TASK-INPUT", f"input {item!r} must be `field=path-or-value`")
        key = key.strip()
        if key in _CTX_FIELDS:
            ctx[key] = Path(value.strip())
        elif key in ("rule_id", "now", "operation_id", "tool"):
            ctx[key] = value.strip()
        elif key.startswith("gate."):
            ctx.setdefault("gate_detail", {})[key[5:]] = value.strip()
        else:
            raise ContractError("AF-TASK-INPUT", f"unknown input field {key!r}")
    return ctx


def load_recipes() -> dict[str, list[str]]:
    """recipe name -> ordered dispatch verbs (package data)."""
    from importlib import resources

    text = resources.files("apiforge.rules").joinpath("recipes.yaml").read_text(encoding="utf-8")
    try:
        data = load_yaml_mapping(text, source="rules/recipes.yaml")
    except (StrictYamlError, ValueError) as exc:
        raise ContractError("AF-RECIPE-INVALID", str(exc)) from exc
    recipes = data.get("recipes")
    if not isinstance(recipes, dict):
        raise ContractError("AF-RECIPE-INVALID", "recipes.yaml lacks 'recipes'")
    return {
        str(name): [str(v) for v in steps]
        for name, steps in recipes.items()
        if isinstance(steps, list)
    }
