"""Repository-native Caveman/Cavekit and RTK integration status."""

from __future__ import annotations

import hashlib
from pathlib import Path


def _manifest(root: Path) -> dict[str, str]:
    manifest = root / "vendor" / "MANIFEST.sha256"
    if not manifest.is_file():
        return {}
    entries: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            digest, relative = line.split("  ", 1)
            entries[relative] = digest
    return entries


def native_status(root: Path) -> dict[str, object]:
    """Report native assets and manifest integrity without executing hooks."""
    root = Path(root)
    entries = _manifest(root)
    missing: list[str] = []
    divergent: list[str] = []
    for relative, expected in entries.items():
        path = root / "vendor" / Path(relative)
        if not path.is_file():
            missing.append(relative)
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            divergent.append(relative)
    return {
        "caveman": {
            "vendored": (root / "vendor" / "caveman").is_dir(),
            "skills": (root / "vendor" / "caveman" / "skills").is_dir(),
            "hooks": (root / "vendor" / "caveman" / "src" / "hooks").is_dir(),
            "plugin": (root / "vendor" / "caveman" / "plugins" / "caveman").is_dir(),
        },
        "cavekit": {"vendored": (root / "vendor" / "cavekit").is_dir()},
        "rtk": {
            "config_present": (root / ".rtk" / "filters.toml").is_file(),
            "binary_embedded": False,
            "mode": "project-local-filters; external binary optional",
        },
        "caveman_config": {
            "present": (root / ".caveman" / "config.json").is_file(),
            "default_mode": "full",
        },
        "manifest": {
            "declared_files": len(entries),
            "missing": missing,
            "divergent": divergent,
            "valid": not missing and not divergent,
        },
        "execution": "skills and hooks are host-installed assets; this command only verifies them",
    }
