"""Package-owned asset discovery and content hashing."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

from apiforge.contracts.distribution import AssetStatus
from apiforge.contracts.evidence import EvidenceRecord


@dataclass(frozen=True, slots=True)
class PackageAsset:
    name: str
    path: Path
    sha256: str


def package_root() -> Path:
    """Return the installed package root, never a cwd-controlled mirror."""

    return Path(__file__).resolve().parents[1]


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _walk(root: Path, prefix: str = "") -> list[PackageAsset]:
    assets: list[PackageAsset] = []
    if not root.is_dir():
        return assets
    for item in sorted(root.iterdir(), key=lambda value: value.name):
        relative = f"{prefix}/{item.name}" if prefix else item.name
        if item.is_dir() and item.name != "__pycache__":
            assets.extend(_walk(item, relative))
        elif item.is_file():
            assets.append(PackageAsset(relative, item, _digest(item)))
    return assets


def asset_inventory() -> tuple[PackageAsset, ...]:
    """List packaged host assets and their deterministic hashes."""

    resource = files("apiforge.host_assets")
    root = Path(str(resource))
    return tuple(_walk(root))


def asset_status(*, verify: bool = True) -> tuple[AssetStatus, ...]:
    assets = asset_inventory()
    return tuple(
        AssetStatus(
            asset=item.name,
            path=str(item.path),
            sha256=item.sha256,
            state="present" if verify or item.path.is_file() else "unresolved",
            evidence=EvidenceRecord(
                level="observed", source="importlib.resources", refs=(item.name,)
            ),
        )
        for item in assets
    )


__all__ = ["PackageAsset", "asset_inventory", "asset_status", "package_root"]
