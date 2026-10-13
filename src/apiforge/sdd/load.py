"""Discover SDD features and load phase artifacts."""

from __future__ import annotations

import re
from pathlib import Path

from apiforge.core.yaml import StrictLoadError, load_yaml_mapping, split_frontmatter
from apiforge.sdd.models import FeatureDiscovery, SddArtifact, SkippedEntry

_FEATURE_NAME = re.compile(r"^[A-Z0-9_]+$")


def discover_features(root: Path) -> FeatureDiscovery:
    """Map ``<FEATURE>/<phase>.md`` under ``root``; everything else is named."""
    root = Path(root)
    features: dict[str, dict[str, Path]] = {}
    skipped: list[SkippedEntry] = []
    if not root.is_dir():
        return FeatureDiscovery(
            root=root,
            skipped=(SkippedEntry(name=root.name or str(root), reason="root is not a directory"),),
        )
    for entry in sorted(root.iterdir(), key=lambda p: p.name):
        if not entry.is_dir():
            skipped.append(SkippedEntry(name=entry.name, reason="not a directory"))
        elif not _FEATURE_NAME.fullmatch(entry.name):
            skipped.append(
                SkippedEntry(name=entry.name, reason="not a feature dir name (^[A-Z0-9_]+$)")
            )
        else:
            phases = {
                item.stem: item
                for item in sorted(entry.iterdir(), key=lambda p: p.name)
                if item.is_file() and item.suffix == ".md"
            }
            features[entry.name] = phases
    return FeatureDiscovery(root=root, features=features, skipped=tuple(skipped))


def load_artifact(path: Path) -> SddArtifact:
    """Parse one artifact; frontmatter problems become named errors."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return SddArtifact(path=path, error="AF-DOC-NOT-UTF8")
    block, body = split_frontmatter(text)
    if block is None:
        return SddArtifact(path=path, body=text, error="AF-SDD-FRONTMATTER")
    try:
        meta = load_yaml_mapping(block, source=path.name)
    except StrictLoadError as exc:
        if exc.code == "AF-YAML-NOT-MAPPING":
            return SddArtifact(path=path, body=body, error="AF-SDD-FRONTMATTER")
        return SddArtifact(path=path, body=body, error=exc.code)
    return SddArtifact(path=path, meta=meta, body=body)
