"""Pure evidence-gate inputs for routing evolution."""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.contracts.routing_evolution import EvidenceCoverage
from apiforge.evals.evidence_coverage import calculate_evidence_coverage


def build_evidence_coverage(
    required_evidence: Iterable[str],
    available_evidence: Iterable[str],
    *,
    limitations: Iterable[str] = (),
) -> EvidenceCoverage:
    """Build the immutable coverage record consumed by promotion."""
    return calculate_evidence_coverage(
        required_evidence,
        available_evidence,
        limitations=limitations,
    )
