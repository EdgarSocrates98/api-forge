"""Context funnel: measure what each case stage keeps — in bytes, not claims.

Stages: ``api-ir.json`` → ``facts.json`` → ``findings.json`` → the
``summary`` projection of findings. A missing artifact is a named
diagnostic, never a zero silently reported.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apiforge.core.detail import apply_detail_level

_STAGE_FILES = (
    ("api_ir", "api-ir.json"),
    ("facts", "facts.json"),
    ("findings", "findings.json"),
)


def measure_funnel(case_dir: Path) -> dict[str, Any]:
    """Return measured stage sizes and reductions for a persisted case."""
    case_dir = Path(case_dir)
    if not case_dir.is_dir():
        from apiforge.application.analyze import AnalysisError

        raise AnalysisError("AF-INPUT-NOT-FOUND", str(case_dir))

    stages: list[dict[str, Any]] = []
    diagnostics: list[dict[str, str]] = []
    sizes: dict[str, int] = {}
    for stage, name in _STAGE_FILES:
        path = case_dir / name
        if not path.is_file():
            diagnostics.append(
                {
                    "code": "AF-FUNNEL-ARTIFACT-MISSING",
                    "detail": f"{name} absent from {case_dir}",
                }
            )
            continue
        size = len(path.read_bytes())
        sizes[stage] = size
        stages.append({"stage": stage, "file": name, "bytes": size})

    findings_path = case_dir / "findings.json"
    if findings_path.is_file():
        findings = json.loads(findings_path.read_text(encoding="utf-8"))
        projected = apply_detail_level(findings, "summary")
        size = len(json.dumps(projected, sort_keys=True).encode("utf-8"))
        sizes["findings_summary"] = size
        stages.append(
            {"stage": "findings_summary", "file": "findings.json", "bytes": size}
        )

    reduction: dict[str, float] = {}
    pairs = (("facts", "findings"), ("findings", "findings_summary"))
    for high, low in pairs:
        if high in sizes and low in sizes and sizes[high] > 0:
            reduction[f"{high}_to_{low}"] = round(sizes[low] / sizes[high], 4)
    return {
        "case_dir": str(case_dir),
        "stages": stages,
        "reduction": reduction,
        "diagnostics": diagnostics,
    }
