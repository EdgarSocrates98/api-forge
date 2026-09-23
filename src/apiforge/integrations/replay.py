"""Deterministic replay adapter for change-control bundles."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from apiforge.contracts.change_control import ChangeBundle
from apiforge.core.io import read_json


class ReplayAdapterError(ValueError):
    """A replay artifact is missing, malformed or not a change bundle."""

    def __init__(
        self,
        code: str,
        detail: str,
        *,
        field: str = "replay bundle",
        unlock: str = "provide a valid af-change-bundle/1 artifact and retry",
    ) -> None:
        self.code = code
        self.detail = detail
        self.field = field
        self.unlock = unlock
        super().__init__(f"{code}: {detail} (field={field}; unlock={unlock})")


class ReplayAdapter:
    """Load an immutable bundle without network access or provider mutation."""

    name = "artifact-replay"

    def load(self, path: Path) -> ChangeBundle:
        try:
            raw = read_json(path)
            if not isinstance(raw, dict):
                raise ReplayAdapterError("AF-CHANGE-REPLAY-SHAPE", "bundle must be a JSON object")
            return ChangeBundle.model_validate(raw)
        except FileNotFoundError as exc:
            raise ReplayAdapterError("AF-CHANGE-REPLAY-MISSING", str(path)) from exc
        except ValidationError as exc:
            raise ReplayAdapterError("AF-CHANGE-REPLAY-CONTRACT", str(exc)) from exc
