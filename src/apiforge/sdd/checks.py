"""``sdd check``: frontmatter schema, upstream hash cascade, gaps vs refusals.

Refusals are hard violations; gaps are conditions that are tolerable while a
phase is ``draft``/``ready`` but block ``done`` (and escalate under
``strict``). Every entry names its code, feature, field and unlock.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from apiforge.core.models import JsonValue
from apiforge.sdd.details import _check_phase_details
from apiforge.sdd.load import discover_features, load_artifact
from apiforge.sdd.models import (
    PHASES,
    SddArtifact,
    SddError,
    SddIssue,
    SddReport,
    SddStatus,
    load_profiles,
)
from apiforge.sdd.phases import _check_meta, _check_upstream, _issue


def _check_feature(
    root: Path,
    name: str,
    files: Mapping[str, Path],
    profiles: Mapping[str, tuple[str, ...]],
    refused: list[SddIssue],
    unresolved: list[SddIssue],
    strict: bool,
) -> None:
    artifacts = {stem: load_artifact(path) for stem, path in files.items()}
    feature_dir = root / name

    for stem in sorted(files):
        if stem not in PHASES:
            unresolved.append(
                _issue(
                    "AF-SDD-UNKNOWN-FILE",
                    name,
                    f"{stem}.md is not a known phase artifact",
                    phase=stem,
                    unlock="rename it or move it out of the feature dir",
                )
            )
    valid: dict[str, SddArtifact] = {}
    for stem, artifact in artifacts.items():
        if artifact.error:
            refused.append(
                _issue(
                    artifact.error,
                    name,
                    f"{stem}.md frontmatter is invalid",
                    phase=stem,
                    field="frontmatter",
                )
            )
        elif stem in PHASES:
            valid[stem] = artifact

    profile = next(
        (
            str(valid[s].meta["profile"])
            for s in PHASES
            if s in valid and valid[s].meta.get("profile")
        ),
        None,
    )
    if profile is None:
        refused.append(
            _issue(
                "AF-SDD-SCHEMA-INVALID",
                name,
                "no artifact declares a profile",
                field="profile",
            )
        )
        required: tuple[str, ...] = ()
    elif profile not in profiles:
        refused.append(
            _issue(
                "AF-SDD-SCHEMA-INVALID",
                name,
                f"unknown profile {profile!r}",
                field="profile",
            )
        )
        required = ()
    else:
        required = profiles[profile]
    for phase in required:
        if phase not in files:
            refused.append(
                _issue(
                    "AF-SDD-PHASE-SKIPPED-UNDECLARED",
                    name,
                    f"required phase {phase!r} has no artifact",
                    phase=phase,
                    field=phase,
                    unlock=f"create {phase}.md or set status: not_required with justification",
                )
            )

    for stem in PHASES:
        art = valid.get(stem)
        if art is None:
            continue
        _check_meta(name, stem, art, refused)
        _check_upstream(name, stem, art, feature_dir, refused)
        _check_phase_details(root, name, stem, art, valid, refused, unresolved, strict)


def check(root: Path, feature: str | None = None, strict: bool = False) -> SddReport:
    """Validate the SDD tree; refusals and gaps are named, never silent."""
    root = Path(root)
    discovery = discover_features(root)
    if feature is not None and feature not in discovery.features:
        raise SddError("AF-SDD-FEATURE-UNKNOWN", feature)
    names = (feature,) if feature else tuple(sorted(discovery.features))
    profiles = load_profiles()
    refused: list[SddIssue] = []
    unresolved: list[SddIssue] = []
    for name in names:
        _check_feature(root, name, discovery.features[name], profiles, refused, unresolved, strict)
    key = lambda i: (i.code, i.feature, i.phase or "", i.field or "", i.message)
    refused.sort(key=key)
    unresolved.sort(key=key)
    return SddReport(
        ok=not refused and not unresolved,
        root=str(root),
        features=tuple(names),
        refused=tuple(refused),
        unresolved=tuple(unresolved),
    )


def status(root: Path) -> SddStatus:
    """Summarize phase status and missing required phases per feature."""

    root = Path(root)
    discovery = discover_features(root)
    profiles = load_profiles()
    features: dict[str, JsonValue] = {}
    for name in sorted(discovery.features):
        files = discovery.features[name]
        phases: dict[str, str] = {}
        profile = "standard"
        for stem in PHASES:
            if stem in files:
                artifact = load_artifact(files[stem])
                if not artifact.error:
                    phases[stem] = str(artifact.meta.get("status", "unknown"))
                    if artifact.meta.get("profile"):
                        profile = str(artifact.meta["profile"])
        missing = [p for p in profiles.get(profile, PHASES) if p not in files]
        features[name] = {
            "profile": profile,
            "phases": phases,
            "missing_required": tuple(missing),
        }
    return SddStatus(root=str(root), features=features)
