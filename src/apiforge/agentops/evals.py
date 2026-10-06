"""Local evals for output compaction safety."""

from __future__ import annotations

import re

from apiforge.agentops.compact import CompactedOutput


def evaluate_compaction(original: str, result: CompactedOutput) -> dict[str, object]:
    """Check critical-line recall; never claims byte equality for projections."""
    critical = [
        line.strip()
        for line in original.splitlines()
        if re.search(
            r"AF-[A-Z0-9-]+|error|exception|failed|failure|panic|blocked|refused|denied|warning",
            line,
            re.IGNORECASE,
        )
    ]
    missing = [line for line in critical if line not in result.text]
    return {
        "passed": not missing and result.critical_evidence_preserved,
        "critical_total": len(critical),
        "critical_missing": missing,
        "source_sha256": result.source_sha256,
        "semantic_loss": bool(missing),
    }
