"""API Forge release gate.

Checks the repository is complete enough to ship:

- required documentation exists (MVP docs, SDD/policy contracts, ADRs,
  templates);
- production code never imports model/cloud SDKs;
- every catalog rule ID is exercised by at least one test;
- fixture analysis is byte-reproducible;
- every ``AF-SDD-*``/``AF-POLICY-*`` code emitted by source is documented and
  every documented code is emitted (parity in both directions);
- ``profiles.yaml`` covers quick/standard/critical/migration and
  ``gates.yaml`` references only known evidence kinds;
- SDD templates parse cleanly;
- an evidence receipt round-trips on the fixture case;
- the threat model names the governance-era threats.

The gate never invokes pytest — it is itself part of the test suite, so a
recursive invocation would deadlock the acceptance pipeline.

Usage: ``python scripts/check_release.py`` — exits 0 with
``API Forge release gate: PASS`` or prints each failure and exits 1.
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
    "docs/sdd-contract.md",
    "docs/policy-contract.md",
    "docs/decisions/ADR-001-deterministic-core.md",
    "docs/decisions/ADR-002-api-ir-provenance.md",
    "docs/decisions/ADR-003-policy-as-data.md",
    "docs/decisions/ADR-004-hash-cascade.md",
    "docs/decisions/ADR-005-correspondence-not-authorship.md",
    "docs/decisions/ADR-006-tree-sitter-language-adapters.md",
    "docs/catalog-contract.md",
)

FORBIDDEN_IMPORT = re.compile(
    r"^\s*(?:import|from)\s+(?:openai|anthropic|boto3|litellm)\b", re.MULTILINE
)

CASE_ARTIFACTS = ("api-ir.json", "facts.json", "findings.json", "case.json")

EXPECTED_PROFILES = {"quick", "standard", "critical", "migration"}

KNOWN_EVIDENCE_KINDS = {
    "contract.document",
    "plan.tasks",
    "test.results",
    "threat.model",
    "benchmark.results",
    "release.receipt",
}

PHASES = (
    "discover",
    "intent",
    "contract",
    "architecture",
    "plan",
    "build",
    "verify",
    "secure",
    "benchmark",
    "ship",
)

THREAT_PHRASES = (
    "tree-sitter",
    "policy tampering",
    "diff path escape",
    "symlinks inside copied trees",
    "frontmatter injection",
    "gate override abuse",
    "worktree index drift",
)


def _check_docs(root: Path, failures: list[str]) -> None:
    for doc in REQUIRED_DOCS:
        if not (root / doc).is_file():
            failures.append(f"missing required doc: {doc}")
    templates = root / "docs" / "sdd" / "templates"
    for phase in PHASES:
        if not (templates / f"{phase}.md").is_file():
            failures.append(f"missing sdd template: {phase}.md")


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


def _source_codes(root: Path, prefix: str) -> set[str]:
    pattern = re.compile(rf'"{prefix}-[A-Z0-9-]+"')
    found: set[str] = set()
    for source in sorted((root / "src").rglob("*.py")):
        found.update(pattern.findall(source.read_text(encoding="utf-8")))
    return {c.strip('"') for c in found}


def _check_code_parity(root: Path, failures: list[str]) -> None:
    for prefix, doc in (
        ("AF-SDD", "docs/sdd-contract.md"),
        ("AF-POLICY", "docs/policy-contract.md"),
        ("AF-CATALOG", "docs/catalog-contract.md"),
        ("AF-ROUTING", "docs/catalog-contract.md"),
        ("AF-SPRING", "docs/catalog-contract.md"),
        ("AF-DETAIL", "docs/catalog-contract.md"),
        ("AF-GO", "docs/catalog-contract.md"),
    ):
        doc_path = root / doc
        if not doc_path.is_file():
            continue  # already reported by _check_docs
        documented = {
            c.strip("`") for c in re.findall(rf"`{prefix}-[A-Z0-9-]+`", doc_path.read_text())
        }
        emitted = _source_codes(root, prefix)
        for code in sorted(emitted - documented):
            failures.append(f"{code} emitted by source but undocumented in {doc}")
        for code in sorted(documented - emitted):
            failures.append(f"{code} documented in {doc} but never emitted")


def _check_catalogs(root: Path, failures: list[str]) -> None:
    from apiforge.sdd.models import load_gates, load_profiles

    try:
        profiles = load_profiles()
        missing = EXPECTED_PROFILES - set(profiles)
        if missing:
            failures.append(f"profiles.yaml missing profiles: {sorted(missing)}")
    except Exception as exc:  # noqa: BLE001
        failures.append(f"profiles.yaml failed to load: {exc}")
    try:
        for gate in load_gates():
            if gate.satisfied_by not in KNOWN_EVIDENCE_KINDS:
                failures.append(
                    f"gates.yaml: {gate.name} references unknown kind {gate.satisfied_by!r}"
                )
    except Exception as exc:  # noqa: BLE001
        failures.append(f"gates.yaml failed to load: {exc}")


def _check_templates(root: Path, failures: list[str]) -> None:
    from apiforge.core.yaml import StrictYamlError, load_yaml_mapping, split_frontmatter

    templates = root / "docs" / "sdd" / "templates"
    for phase in PHASES:
        path = templates / f"{phase}.md"
        if not path.is_file():
            continue  # reported by _check_docs
        try:
            meta, _ = split_frontmatter(path.read_text(encoding="utf-8"))
            data = load_yaml_mapping(meta, source=str(path))
        except (StrictYamlError, ValueError) as exc:
            failures.append(f"template {phase}.md does not parse: {exc}")
            continue
        if data.get("sdd") != 1 or data.get("phase") != phase:
            failures.append(f"template {phase}.md: bad sdd/phase frontmatter")
        if phase != "discover" and not isinstance(data.get("upstream"), dict):
            failures.append(f"template {phase}.md: missing upstream declaration")


def _check_receipt_roundtrip(root: Path, failures: list[str]) -> None:
    from apiforge.application.analyze import analyze_project
    from apiforge.evidence.build import emit_receipt
    from apiforge.evidence.verify import verify_receipt

    contract = Path("tests/fixtures/openapi/orders-v1.yaml")
    project = Path("tests/fixtures/fastapi_orders")
    if not (root / contract).is_file() or not (root / project).is_dir():
        return  # reported by _check_reproducibility
    with tempfile.TemporaryDirectory() as tmp:
        case = Path(tmp) / "case"
        try:
            analyze_project(contract, project, None, case)
            receipt = emit_receipt(case)
            again = emit_receipt(case)
            if receipt != again:
                failures.append("receipt not deterministic on unchanged inputs")
            report = verify_receipt(receipt, root=case)
            if not report["ok"]:
                failures.append(f"receipt round-trip failed: {report['mismatches']}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"receipt round-trip crashed: {exc}")


def _check_routing(root: Path, failures: list[str]) -> None:
    from apiforge.application.next_step import load_routing
    from apiforge.rules.catalog import load_areas
    from apiforge.sdd.models import PHASES

    try:
        routes = load_routing()
        areas = set(load_areas())
        phases = set(PHASES)
    except Exception as exc:  # noqa: BLE001
        failures.append(f"routing/catalog load failed: {exc}")
        return
    for route in routes:
        if route.phase not in phases:
            failures.append(f"routing.yaml: unknown phase {route.phase!r}")
        if route.dominant_area not in areas:
            failures.append(f"routing.yaml: unknown area {route.dominant_area!r}")


def _check_lab_and_boundary(root: Path, failures: list[str]) -> None:
    for name, glob in (("orders-spring", "*.java"), ("orders-go", "*.go")):
        lab = root / "tests" / "labs" / name
        if not lab.is_dir() or not any(lab.rglob(glob)):
            failures.append(f"{name} parity lab missing {glob} sources")
    for source in sorted((root / "src").rglob("*.py")):
        text = source.read_text(encoding="utf-8")
        if "tree_sitter" in text and not any(
            f"adapters/{a}" in source.as_posix() for a in ("spring", "go")
        ):
            failures.append(f"tree_sitter import outside adapters.spring: {source}")


def _check_threat_model(root: Path, failures: list[str]) -> None:
    path = root / "docs" / "security" / "threat-model-mvp.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8").lower()
    for phrase in THREAT_PHRASES:
        if phrase not in text:
            failures.append(f"threat model missing threat: {phrase}")


def check_repository(root: Path) -> list[str]:
    """Return the list of gate failures; empty means PASS."""
    root = Path(root)
    failures: list[str] = []
    _check_docs(root, failures)
    _check_imports(root, failures)
    _check_rule_coverage(root, failures)
    _check_reproducibility(root, failures)
    _check_code_parity(root, failures)
    _check_catalogs(root, failures)
    _check_templates(root, failures)
    _check_receipt_roundtrip(root, failures)
    _check_routing(root, failures)
    _check_lab_and_boundary(root, failures)
    _check_threat_model(root, failures)
    return failures


def main() -> int:
    failures = check_repository(Path(__file__).resolve().parents[1])
    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print("API Forge release gate: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
