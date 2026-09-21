"""Autonomy modes — ordered, persisted, and changed through the policy engine.

Modes (least to most autonomous):

- ``observe``: every action is evaluated and recorded; nothing executes.
- ``supervised``: ``allow`` decisions execute; a ``gate`` halts the action
  and names its missing requirements; ``deny`` refuses.
- ``continuous``: like supervised for a single action, but a runbook keeps
  going past ``pending``/``denied`` steps instead of halting — every skip
  is recorded in the ledger.

State lives in ``<root>/.apiforge/autonomy/mode.json`` plus an append-only
``ledger.jsonl``; the file is the record, not a cache. Absent state means
``observe`` — the safest reading of "unknown".
"""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict


class AutonomyMode(StrEnum):
    OBSERVE = "observe"
    SUPERVISED = "supervised"
    CONTINUOUS = "continuous"


_ORDER = {
    AutonomyMode.OBSERVE: 0,
    AutonomyMode.SUPERVISED: 1,
    AutonomyMode.CONTINUOUS: 2,
}


class AutonomyError(ValueError):
    """A refused autonomy operation; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class ModeState(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: AutonomyMode = AutonomyMode.OBSERVE
    set_by: str = ""
    set_at: str | None = None  # explicit --now; never read from the clock
    reason: str = ""


def autonomy_dir(root: Path) -> Path:
    return Path(root) / ".apiforge" / "autonomy"


def load_mode(root: Path) -> ModeState:
    path = autonomy_dir(root) / "mode.json"
    if not path.is_file():
        return ModeState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ModeState.model_validate(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise AutonomyError("AF-AUTONOMY-MODE-CORRUPT", f"{path}: {exc}") from exc


def parse_mode(raw: str) -> AutonomyMode:
    try:
        return AutonomyMode(raw)
    except ValueError:
        raise AutonomyError(
            "AF-AUTONOMY-MODE-UNKNOWN",
            f"{raw!r} not in {[m.value for m in AutonomyMode]}",
        ) from None


def is_escalation(current: AutonomyMode, target: AutonomyMode) -> bool:
    return _ORDER[target] > _ORDER[current]
