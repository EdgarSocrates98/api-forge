"""Audit the committed uv lock without resolving or fetching dependencies."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r"^\s*([A-Za-z0-9_.-]+)")


def _name(requirement: str) -> str:
    match = NAME.match(requirement)
    return match.group(1).lower().replace("_", "-") if match else requirement.lower()


def main() -> int:
    failures: list[str] = []
    lock_path = ROOT / "uv.lock"
    project_path = ROOT / "pyproject.toml"
    if not lock_path.is_file():
        failures.append("uv.lock is missing")
        print(json.dumps({"schema": "apiforge/lock-audit/v1", "ok": False, "failures": failures}))
        return 1
    lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    project = tomllib.loads(project_path.read_text(encoding="utf-8"))
    packages = lock.get("package") or []
    package_names = {
        str(item.get("name", "")).lower().replace("_", "-")
        for item in packages
        if isinstance(item, dict)
    }
    metadata = next(
        (
            item.get("metadata", {})
            for item in packages
            if isinstance(item, dict) and item.get("name") == "apiforge"
        ),
        {},
    )
    requires_dist = metadata.get("requires-dist", []) if isinstance(metadata, dict) else []
    locked_dist_names = {
        str(item.get("name", "")).lower().replace("_", "-")
        for item in requires_dist
        if isinstance(item, dict)
    }
    declared = list((project.get("project") or {}).get("dependencies") or [])
    extras = (project.get("project") or {}).get("optional-dependencies") or {}
    declared.extend(item for values in extras.values() for item in values)
    for requirement in declared:
        dependency = _name(str(requirement))
        if dependency not in package_names:
            failures.append(f"declared dependency is absent from lock packages: {dependency}")
        if dependency not in locked_dist_names:
            failures.append(f"declared dependency is absent from lock metadata: {dependency}")
    hashed_registry_packages = 0
    for item in packages:
        if not isinstance(item, dict) or item.get("name") == "apiforge":
            continue
        source = item.get("source") or {}
        if not isinstance(source, dict) or source.get("registry") is None:
            continue
        artifacts = []
        sdist = item.get("sdist")
        if isinstance(sdist, dict):
            artifacts.append(sdist)
        artifacts.extend(wheel for wheel in item.get("wheels", []) if isinstance(wheel, dict))
        if not artifacts or not all(
            str(artifact.get("hash", "")).startswith("sha256:") for artifact in artifacts
        ):
            failures.append(f"registry package lacks sha256 artifact hashes: {item.get('name')}")
        else:
            hashed_registry_packages += 1
    report = {
        "schema": "apiforge/lock-audit/v1",
        "lock_version": lock.get("version"),
        "package_count": len(packages),
        "hashed_registry_packages": hashed_registry_packages,
        "ok": not failures,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
