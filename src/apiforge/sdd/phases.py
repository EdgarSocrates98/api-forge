"""Per-phase frontmatter rules: meta schema and the upstream hash cascade."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from apiforge.core.io import text_sha256
from apiforge.sdd.models import PHASE_STATUS, PHASES, SddArtifact, SddIssue

PHASE_FIELDS: Mapping[str, tuple[str, ...]] = {
    "discover": ("approaches", "chosen"),
    "intent": ("problem", "success", "out_of_scope"),
    "contract": ("covers",),
    "architecture": ("files", "decisions"),
    "plan": ("tasks",),
    "build": ("tasks", "claims"),
    "verify": ("results",),
    "secure": ("threat_model",),
    "benchmark": ("baseline", "results"),
    "ship": ("deviations", "evidence"),
}


def _issue(
    code: str,
    feature: str,
    message: str,
    *,
    phase: str | None = None,
    field: str | None = None,
    unlock: str | None = None,
) -> SddIssue:
    return SddIssue(
        code=code, feature=feature, message=message, phase=phase, field=field, unlock=unlock
    )


def _rel_exists(root: Path, rel: object) -> bool:
    if not isinstance(rel, str) or not rel:
        return False
    target = (root.parent / rel).resolve()
    base = root.parent.resolve()
    try:
        target.relative_to(base)
    except ValueError:
        return False
    return target.is_file()


def _emit(
    code: str,
    feature: str,
    message: str,
    artifact: SddArtifact,
    refused: list[SddIssue],
    unresolved: list[SddIssue],
    *,
    gap: bool = False,
    strict: bool = False,
    field: str | None = None,
    unlock: str | None = None,
) -> None:
    done = artifact.meta.get("status") == "done"
    sink = refused if (not gap or done or strict) else unresolved
    raw_phase = artifact.meta.get("phase")
    sink.append(
        _issue(
            code,
            feature,
            message,
            phase=str(raw_phase) if raw_phase is not None else None,
            field=field,
            unlock=unlock,
        )
    )


def _check_meta(name: str, stem: str, artifact: SddArtifact, refused: list[SddIssue]) -> None:
    meta = artifact.meta

    def bad(field: str) -> None:
        refused.append(
            _issue(
                "AF-SDD-SCHEMA-INVALID",
                name,
                f"{stem}.md: invalid or missing '{field}'",
                phase=stem,
                field=field,
                unlock="fix the frontmatter to match the sdd contract",
            )
        )

    if meta.get("sdd") != 1:
        bad("sdd")
    if meta.get("feature") != name:
        bad("feature")
    if meta.get("phase") != stem:
        bad("phase")
    status = meta.get("status")
    if status not in PHASE_STATUS:
        bad("status")
    elif status == "not_required" and not meta.get("justification"):
        bad("justification")
    if not meta.get("profile"):
        bad("profile")
    for field in PHASE_FIELDS.get(stem, ()):
        if field not in meta:
            bad(field)


def _check_upstream(
    name: str,
    stem: str,
    artifact: SddArtifact,
    feature_dir: Path,
    refused: list[SddIssue],
) -> None:
    if stem == "discover":
        return
    upstream = artifact.meta.get("upstream")
    if not isinstance(upstream, Mapping) or not upstream.get("path"):
        refused.append(
            _issue(
                "AF-SDD-UPSTREAM-MISSING",
                name,
                f"{stem}.md has no upstream block",
                phase=stem,
                field="upstream",
                unlock="declare the previous phase artifact",
            )
        )
        return
    up_path = str(upstream["path"])
    up_file = feature_dir / up_path
    if not up_file.is_file():
        refused.append(
            _issue(
                "AF-SDD-UPSTREAM-MISSING",
                name,
                f"{stem}.md upstream {up_path!r} does not exist",
                phase=stem,
                field="upstream.path",
                unlock="point upstream at an existing phase artifact",
            )
        )
        return
    up_phase = up_file.stem
    if up_phase in PHASES and PHASES.index(up_phase) >= PHASES.index(stem):
        refused.append(
            _issue(
                "AF-SDD-PHASE-ORDER",
                name,
                f"{stem}.md upstream points at {up_phase}, which is not earlier in the cascade",
                phase=stem,
                field="upstream.path",
                unlock="upstream must reference the immediately earlier phase",
            )
        )
        return
    declared = upstream.get("sha256")
    if declared != text_sha256(up_file):
        refused.append(
            _issue(
                "AF-SDD-UPSTREAM-STALE",
                name,
                f"{stem}.md upstream hash does not match {up_path}",
                phase=stem,
                field="upstream.sha256",
                unlock=f"run `apiforge sdd stamp {stem}.md` to restamp",
            )
        )
