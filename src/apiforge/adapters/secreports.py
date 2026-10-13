"""Security report readers: zap / semgrep / trivy / gitleaks -> sec.* facts.

Aggregate counts and identifiers only — gitleaks entries carry rule, file
and line; the secret material is **never** read into a fact.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_EXTRACTOR = "security-report"
_ZAP_RISK = {"0": "info", "1": "low", "2": "medium", "3": "high", "4": "critical"}


def _diag(code: str, message: str, rel: str, digest: str | None) -> Diagnostic:
    source = (
        SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR)
        if digest is not None
        else None
    )
    return Diagnostic(code=code, status=FindingStatus.UNRESOLVED, message=message, source=source)


def _load(
    path: Path, rel: str, input_hashes: dict[str, str], diagnostics: list[Diagnostic]
) -> Any | None:
    if not path.is_file():
        diagnostics.append(_diag("AF-SEC-REPORT-MISSING", f"{rel} missing", rel, None))
        return None
    raw = path.read_bytes()
    input_hashes[rel] = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        diagnostics.append(
            _diag("AF-SEC-REPORT-INVALID", f"{rel}: not valid JSON ({exc})", rel, input_hashes[rel])
        )
        return None


def _fact(
    kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]
) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
        measures=measures,
        attrs=attrs,
    )


def _inventory(
    framework: str,
    root: Path,
    facts: list[Fact],
    diagnostics: list[Diagnostic],
    input_hashes: dict[str, str],
) -> CodeInventory:
    return CodeInventory(
        framework=framework,
        root=str(root),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )


def extract_zap(path: Path) -> CodeInventory:
    """OWASP ZAP JSON report -> `sec.zap.report` (alerts by risk level)."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        by_risk: Counter[str] = Counter()
        alerts = 0
        for site in doc.get("site") or []:
            for alert in (site.get("alerts") or []) if isinstance(site, dict) else []:
                alerts += 1
                by_risk[_ZAP_RISK.get(str(alert.get("riskcode")), "unknown")] += 1
        facts.append(
            _fact(
                "sec.zap.report",
                path.name,
                hashes[path.name],
                {"alerts": alerts},
                {"by_risk": dict(sorted(by_risk.items()))},
            )
        )
    return _inventory("zap", path.parent, facts, diagnostics, hashes)


def extract_semgrep(path: Path) -> CodeInventory:
    """Semgrep --json output -> `sec.semgrep.report` (findings by severity)."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        results = [r for r in doc.get("results") or [] if isinstance(r, dict)]
        by_severity = Counter(
            str(r.get("extra", {}).get("severity", "unknown")).lower() for r in results
        )
        facts.append(
            _fact(
                "sec.semgrep.report",
                path.name,
                hashes[path.name],
                {"findings": len(results)},
                {
                    "by_severity": dict(sorted(by_severity.items())),
                    "rules": sorted({str(r.get("check_id")) for r in results}),
                },
            )
        )
    return _inventory("semgrep", path.parent, facts, diagnostics, hashes)


def extract_trivy(path: Path) -> CodeInventory:
    """trivy --format json -> `sec.trivy.report` (findings by severity/target)."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, dict):
        by_severity: Counter[str] = Counter()
        targets: list[str] = []
        total = 0
        for result in doc.get("Results") or []:
            if not isinstance(result, dict):
                continue
            targets.append(str(result.get("Target", "")))
            for bucket in ("Vulnerabilities", "Misconfigurations", "Secrets"):
                for item in result.get(bucket) or []:
                    total += 1
                    by_severity[str(item.get("Severity", "unknown")).lower()] += 1
        facts.append(
            _fact(
                "sec.trivy.report",
                path.name,
                hashes[path.name],
                {"findings": total},
                {
                    "by_severity": dict(sorted(by_severity.items())),
                    "targets": sorted(t for t in targets if t),
                },
            )
        )
    return _inventory("trivy", path.parent, facts, diagnostics, hashes)


def extract_gitleaks(path: Path) -> CodeInventory:
    """gitleaks report JSON -> `sec.gitleaks.report` — secret never emitted."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    doc = _load(path, path.name, hashes, diagnostics)
    if isinstance(doc, list):
        entries = [e for e in doc if isinstance(e, dict)]
        by_rule = Counter(str(e.get("RuleID", "unknown")) for e in entries)
        facts.append(
            _fact(
                "sec.gitleaks.report",
                path.name,
                hashes[path.name],
                {"leaks": len(entries)},
                {
                    "by_rule": dict(sorted(by_rule.items())),
                    "files": sorted({str(e.get("File")) for e in entries}),
                },
            )
        )
    return _inventory("gitleaks", path.parent, facts, diagnostics, hashes)
