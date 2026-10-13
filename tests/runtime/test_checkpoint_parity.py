"""§17 semantic-checkpoint parity: continuous vs checkpoint→fresh-resume.

A deterministic staged executor runs twice: once continuously, once paused at
step k, checkpointed, terminated and resumed from a *freshly loaded* checkpoint
only. Effective state (decisions, facts, unresolved, tool path, result) must be
identical — the checkpoint, not the transcript, is the source of truth.
"""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.agentic_memory import SemanticCheckpoint
from apiforge.runtime.semantic_checkpoint import (
    build_checkpoint,
    equivalent,
    load_checkpoint,
    save_checkpoint,
)

_STEPS = ("analyze", "select", "verify", "synthesize", "report")


def _execute(state: dict[str, list[str]], steps: tuple[str, ...]) -> dict[str, list[str]]:
    """Advance a run deterministically; the same inputs always produce the
    same decisions, facts, unresolved items and tool path."""
    for step in steps:
        state["decisions"].append(f"decision:{step}")
        # position in the accumulated fact list is the global step index, so a
        # resumed run produces the same fact ids as a continuous one
        state["facts"].append(f"fact:{step}:{len(state['facts'])}")
        state["tool_path"].append(f"tool:{step}")
        if step == "verify":
            state["unresolved"].append("provider_tokens_unresolved")
    state["result"] = [f"result:{steps[-1]}"]
    return state


def _empty_state() -> dict[str, list[str]]:
    return {
        "decisions": [],
        "facts": [],
        "unresolved": [],
        "tool_path": [],
        "result": [],
    }


def _state_from_checkpoint(checkpoint: SemanticCheckpoint) -> dict[str, list[str]]:
    """Rebuild run state from checkpoint fields only — the fresh process sees
    nothing else."""
    tool_path = checkpoint.tool_state.get("tool_path", [])
    return {
        "decisions": list(checkpoint.decisions_accepted),
        "facts": list(checkpoint.facts_still_valid),
        "unresolved": list(checkpoint.unresolved),
        "tool_path": [str(item) for item in tool_path],
        "result": [],
    }


def _checkpoint_from_state(
    task_id: str, run_id: str, state: dict[str, list[str]], now: str
) -> SemanticCheckpoint:
    return build_checkpoint(
        task_id=task_id,
        run_id=run_id,
        task_state="paused",
        current_objective="finish the staged run",
        created_at=now,
        decisions_accepted=tuple(state["decisions"]),
        facts_still_valid=tuple(state["facts"]),
        unresolved=tuple(state["unresolved"]),
        tool_state={"tool_path": tuple(state["tool_path"])},
        next_actions=tuple(step for step in _STEPS if f"decision:{step}" not in state["decisions"]),
    )


def test_resume_after_termination_matches_continuous_run(tmp_path: Path) -> None:
    task_id, run_id = "task-parity", "run-parity"
    continuous = _execute(_empty_state(), _STEPS)

    cut = 2
    partial = _execute(_empty_state(), _STEPS[:cut])
    checkpoint = _checkpoint_from_state(task_id, run_id, partial, "2026-10-05T10:00:00Z")
    save_checkpoint(tmp_path, checkpoint)
    del partial  # terminated: nothing survives but the checkpoint file

    loaded = load_checkpoint(tmp_path, task_id, run_id)
    resumed = _state_from_checkpoint(loaded)
    _execute(resumed, _STEPS[cut:])

    assert resumed == continuous
    # rebuilding the checkpoint from resumed-prefix state is equivalent too
    rebuilt = _checkpoint_from_state(
        task_id, run_id, _execute(_empty_state(), _STEPS[:cut]), "2026-10-05T11:00:00Z"
    )
    assert equivalent(loaded, rebuilt)


def test_equivalence_ignores_identity_but_not_state(tmp_path: Path) -> None:
    base = _checkpoint_from_state(
        "t", "r", _execute(_empty_state(), _STEPS[:1]), "2026-10-05T10:00:00Z"
    )
    divergent = base.model_copy(update={"unresolved": ("new-gap",)})
    assert not equivalent(base, divergent)
