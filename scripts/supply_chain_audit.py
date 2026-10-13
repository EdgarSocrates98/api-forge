"""Offline supply-chain audit (§30).

Deterministic, local-only checks:

- dependency inventory parsed from pyproject.toml (declared, never fetched);
- ``pip check`` environment consistency;
- vendored asset parity against ``vendor/MANIFEST.sha256``;
- eval corpus consistency (every corpus directory has a README and every
  yaml parses);
- MCP surface lock (the declared tool count stays within the pinned
  registry — drift is enforced by tests, reported here for the audit).

CVE/advisory scanning needs an external vulnerability database — that is
a declared external boundary and stays ``unresolved`` here rather than
being faked with stale data.

Exit code: 0 when every local check passes, 1 otherwise.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _deps_inventory(failures: list[str]) -> dict[str, object]:
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.is_file():
        failures.append("pyproject.toml missing")
        return {}
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    project = data.get("project", {})
    deps = list(project.get("dependencies", []))
    extras = {k: list(v) for k, v in (project.get("optional-dependencies") or {}).items()}
    unpinned = [
        d
        for d in deps + [x for v in extras.values() for x in v]
        if not any(op in d for op in (">=", "==", "~=", "<", ">"))
    ]
    if unpinned:
        failures.append(f"unpinned declared dependencies: {sorted(unpinned)}")
    return {
        "dependencies": deps,
        "extras": extras,
        "requires_python": project.get("requires-python", ""),
        "unpinned": unpinned,
    }


def _pip_check(failures: list[str], unresolved: list[str]) -> str:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        check=False,
        text=True,
        cwd=ROOT,
        timeout=120,
    )
    output = (result.stdout + result.stderr).strip().splitlines()
    summary = output[0] if output else "pip check produced no output"
    if "No module named pip" in summary:
        unresolved.append(
            "pip check unavailable in this interpreter (uv venv without pip); "
            "the CI job runs it where pip exists"
        )
        return "skipped: no pip module in this interpreter"
    if result.returncode != 0:
        failures.append(f"pip check failed: {summary}")
    return summary


def _vendor_parity(failures: list[str]) -> str:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import vendor_caveman

        diffs = vendor_caveman.check()
    except (ImportError, OSError, RuntimeError, ValueError) as exc:
        failures.append(f"vendor parity check could not run: {exc}")
        return f"error: {exc}"
    if diffs:
        failures.extend(diffs)
        return f"{len(diffs)} divergence(s)"
    return "vendor/ matches MANIFEST.sha256"


def _corpus_consistency(failures: list[str]) -> dict[str, int]:
    import yaml

    corpus_root = ROOT / "evals" / "corpus"
    corpora = cases = 0
    if not corpus_root.is_dir():
        failures.append("evals/corpus missing")
        return {"corpora": 0, "cases": 0}
    for directory in sorted(p for p in corpus_root.iterdir() if p.is_dir()):
        corpora += 1
        if not (directory / "README.md").is_file():
            failures.append(f"{directory.name}: corpus README missing")
        for yaml_path in sorted(directory.glob("*.yaml")):
            cases += 1
            try:
                yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                failures.append(f"{directory.name}/{yaml_path.name}: {exc}")
    return {"corpora": corpora, "cases": cases}


def _surface_lock() -> dict[str, int]:
    try:
        from apiforge.mcp.gateway import full_tools

        return {"mcp_tools": len(full_tools())}
    except (ImportError, RuntimeError, ValueError) as exc:
        return {"mcp_tools": -1, "error": str(exc)}  # type: ignore[dict-item]


def main() -> int:
    failures: list[str] = []
    unresolved = [
        (
            "CVE/advisory scanning requires an external vulnerability "
            "database — declared external boundary, never faked offline"
        )
    ]
    report = {
        "schema": "apiforge/supply-chain-audit/v1",
        "checks": {
            "dependency_inventory": _deps_inventory(failures),
            "pip_check": _pip_check(failures, unresolved),
            "vendor_parity": _vendor_parity(failures),
            "eval_corpus": _corpus_consistency(failures),
            "surface_lock": _surface_lock(),
        },
        "unresolved": unresolved,
        "failed": 0,
        "ok": True,
    }
    report["failed"] = len(failures)
    report["failures"] = failures
    report["ok"] = not failures
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
