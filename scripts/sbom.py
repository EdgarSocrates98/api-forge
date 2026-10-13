"""Emit deterministic CycloneDX SBOM from committed uv.lock metadata."""

from __future__ import annotations

import argparse
import hashlib
import json
import tomllib
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _purl(name: str, version: str) -> str:
    return f"pkg:pypi/{name.lower().replace('_', '-')}@{version}"


def build(lock_path: Path) -> dict[str, Any]:
    raw = lock_path.read_bytes()
    lock = tomllib.loads(raw.decode("utf-8"))
    packages = [item for item in lock.get("package", []) if isinstance(item, dict)]
    components: list[dict[str, Any]] = []
    dependencies: list[dict[str, Any]] = []
    for item in sorted(packages, key=lambda row: str(row.get("name", ""))):
        name = str(item.get("name", ""))
        version = str(item.get("version", "editable"))
        ref = _purl(name, version)
        component: dict[str, Any] = {
            "type": "application" if name == "apiforge" else "library",
            "bom-ref": ref,
            "name": name,
            "version": version,
            "purl": ref,
            "properties": [{"name": "api-forge:lock-source", "value": str(item.get("source", {}))}],
        }
        hashes: list[dict[str, str]] = []
        for artifact_key in ("sdist", "wheels"):
            artifacts = item.get(artifact_key, [])
            if isinstance(artifacts, dict):
                artifacts = [artifacts]
            for artifact in artifacts:
                if isinstance(artifact, dict) and str(artifact.get("hash", "")).startswith(
                    "sha256:"
                ):
                    hashes.append({"alg": "SHA-256", "content": str(artifact["hash"])[7:]})
        if hashes:
            component["hashes"] = hashes
        components.append(component)
        dependency_names = []
        for dependency in item.get("dependencies", []):
            if isinstance(dependency, dict) and dependency.get("name"):
                dependency_names.append(str(dependency["name"]))
        dependencies.append(
            {
                "ref": ref,
                "dependsOn": sorted(
                    _purl(
                        str(dep),
                        next(
                            str(row.get("version", "editable"))
                            for row in packages
                            if str(row.get("name", "")).lower() == str(dep).lower()
                        ),
                    )
                    for dep in dependency_names
                ),
            }
        )
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.UUID(hex=digest[:32])}",
        "version": 1,
        "metadata": {
            "tools": [{"vendor": "API Forge", "name": "scripts/sbom.py"}],
            "properties": [{"name": "api-forge:lock-sha256", "value": digest}],
        },
        "components": components,
        "dependencies": dependencies,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", type=Path, default=ROOT / "uv.lock")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = build(args.lock)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
