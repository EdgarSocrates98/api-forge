"""``sdd set-phase``: gated phase transitions.

Under ``strict``, moving a guarded phase to ``ready``/``done`` requires the
gate's evidence kind to be present in the feature's evidence dir — evidence
unlocks, never a flag. An explicit override records who passed over what and
why in ``gate-overrides.json``.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from apiforge.core.io import read_json, write_json
from apiforge.sdd.models import PHASE_STATUS, PhaseChange, SddError, load_gates
from apiforge.sdd.stamp import set_frontmatter_field

_GATED_STATUSES = frozenset({"ready", "done"})


def set_phase(
    root: Path,
    feature: str,
    phase: str,
    status: str,
    *,
    strict: bool = False,
    override: Mapping[str, str] | None = None,
    evidence_dir: Path | None = None,
    state_dir: Path | None = None,
) -> PhaseChange:
    """Transition ``feature/phase`` to ``status``, enforcing gates under strict."""
    root = Path(root)
    if status not in PHASE_STATUS:
        raise SddError("AF-SDD-SCHEMA-INVALID", f"unknown status {status!r}")
    artifact = root / feature / f"{phase}.md"
    if not artifact.is_file():
        raise SddError("AF-SDD-ARTIFACT-MISSING", f"{feature}/{phase}.md")
    state_dir = state_dir or root.parent.parent / ".apiforge" / "sdd" / feature
    evidence_dir = evidence_dir or state_dir / "evidence"

    applied: list[str] = []
    if strict and status in _GATED_STATUSES:
        from apiforge.sdd.evidence_valid import validate_evidence

        profile = _feature_profile(root, feature)
        for gate in load_gates():
            if phase not in gate.guards_phases:
                continue
            if gate.profiles and profile not in gate.profiles:
                continue
            evidence_file = evidence_dir / f"{gate.satisfied_by}.json"
            verdict = validate_evidence(
                evidence_file, feature=feature, expected_kind=gate.satisfied_by
            )
            if verdict["state"] == "valid":
                continue
            if (
                override
                and override.get("gate") == gate.name
                and override.get("reason", "").strip()
                and override.get("actor", "").strip()
            ):
                _record_override(state_dir, gate.name, phase, status, override, verdict["code"])
                applied.append(gate.name)
                continue
            raise SddError(
                verdict["code"] if verdict["code"].startswith("AF-SDD") else "AF-SDD-GATE-BLOCKED",
                f"{gate.name}: evidence {gate.satisfied_by!r} "
                f"{verdict['state']} — {verdict['reason']} "
                f"(produce it via {gate.produced_by!r} or pass --override "
                "with reason+actor)",
            )

    previous = set_frontmatter_field(artifact, "status", status)
    return PhaseChange(
        feature=feature,
        phase=phase,
        previous=previous,
        status=status,
        overrides_applied=tuple(applied),
        changed=previous != status,
    )


def _feature_profile(root: Path, feature: str) -> str:
    """Profile declared in the feature's intent.md frontmatter ("" if absent)."""
    from apiforge.core.yaml import StrictYamlError, load_yaml_mapping, split_frontmatter

    intent = root / feature / "intent.md"
    if not intent.is_file():
        return ""
    try:
        meta, _ = split_frontmatter(intent.read_text(encoding="utf-8"))
        if meta is None:
            return ""
        data = load_yaml_mapping(meta, source=f"{feature}/intent.md frontmatter")
        return str(data.get("profile") or "")
    except StrictYamlError:
        return ""


def _record_override(
    state_dir: Path,
    gate: str,
    phase: str,
    status: str,
    override: Mapping[str, str],
    verdict_code: str = "",
) -> None:
    import time

    record_path = state_dir / "gate-overrides.json"
    record: dict[str, Any] = {"overrides": []}
    if record_path.is_file():
        existing: Any = read_json(record_path)
        if isinstance(existing, dict) and isinstance(existing.get("overrides"), list):
            record = existing
    record["overrides"].append(
        {
            "gate": gate,
            "phase": phase,
            "status": status,
            "reason": str(override.get("reason", "")),
            "actor": str(override.get("actor", "unknown")),
            "evidence_verdict": verdict_code,
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
    )
    write_json(record_path, record)
