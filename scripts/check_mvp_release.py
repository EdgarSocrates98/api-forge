"""API Forge MVP release gate.

Checks the repository is complete enough to ship the vertical slice:

- required documentation exists;
- production code never imports model/cloud SDKs (openai, anthropic, boto3,
  litellm);
- every catalog rule ID is exercised by at least one test;
- fixture analysis is byte-reproducible across two output directories.

The gate never invokes pytest — it is itself part of the test suite, so a
recursive invocation would deadlock the acceptance pipeline.

Usage: ``python scripts/check_mvp_release.py`` — exits 0 with
``API Forge MVP release gate: PASS`` or prints each failure and exits 1.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

REQUIRED_DOCS = (
    "README.md",
    "docs/architecture/mvp-boundaries.md",
    "docs/security/threat-model-mvp.md",
    "docs/decisions/ADR-001-deterministic-core.md",
    "docs/decisions/ADR-002-api-ir-provenance.md",
)

FORBIDDEN_IMPORT = re.compile(
    r"^\s*(?:import|from)\s+(?:openai|anthropic|boto3|litellm)\b", re.MULTILINE
)

CASE_ARTIFACTS = ("api-ir.json", "facts.json", "findings.json", "case.json")


def _check_docs(root: Path, failures: list[str]) -> None:
    for doc in REQUIRED_DOCS:
        if not (root / doc).is_file():
            failures.append(f"missing required doc: {doc}")


def _check_imports(root: Path, failures: list[str]) -> None:
    for source in sorted((root / "src").rglob("*.py")):
        text = source.read_text(encoding="utf-8")
        match = FORBIDDEN_IMPORT.search(text)
        if match:
            failures.append(f"forbidden import in {source}: {match.group(0).strip()}")


def _check_rule_coverage(root: Path, failures: list[str]) -> None:
    from apiforge.rules.catalog import load_catalog

    test_corpus = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((root / "tests").rglob("*.py"))
    )
    for rule_id in sorted(load_catalog()):
        if rule_id not in test_corpus:
            failures.append(f"catalog rule not exercised by tests: {rule_id}")


def _check_reproducibility(root: Path, failures: list[str]) -> None:
    from apiforge.application.analyze import analyze_project

    contract = Path("tests/fixtures/openapi/orders-v1.yaml")
    project = Path("tests/fixtures/fastapi_orders")
    if not (root / contract).is_file() or not (root / project).is_dir():
        failures.append("release fixtures missing")
        return
    with tempfile.TemporaryDirectory() as tmp:
        first, second = Path(tmp) / "first", Path(tmp) / "second"
        try:
            analyze_project(contract, project, None, first)
            analyze_project(contract, project, None, second)
        except Exception as exc:  # noqa: BLE001 - gate reports, never crashes
            failures.append(f"fixture analysis failed: {exc}")
            return
        for name in CASE_ARTIFACTS:
            if (first / name).read_bytes() != (second / name).read_bytes():
                failures.append(f"analysis not reproducible: {name} differs")


def check_repository(root: Path) -> list[str]:
    """Return the list of gate failures; empty means PASS."""
    root = Path(root)
    failures: list[str] = []
    _check_docs(root, failures)
    _check_imports(root, failures)
    _check_rule_coverage(root, failures)
    _check_reproducibility(root, failures)
    return failures


def main() -> int:
    failures = check_repository(Path(__file__).resolve().parents[1])
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print("API Forge MVP release gate: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
