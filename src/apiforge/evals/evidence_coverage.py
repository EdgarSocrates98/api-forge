"""Deterministic Evidence Coverage calculations."""

from __future__ import annotations

from collections.abc import Iterable

from apiforge.contracts.routing_evolution import CoverageState, EvidenceCoverage


def calculate_evidence_coverage(
    required: Iterable[str],
    available: Iterable[str],
    *,
    limitations: Iterable[str] = (),
) -> EvidenceCoverage:
    """Calculate coverage while preserving missing and limitation states."""
    required_values = tuple(sorted({str(item) for item in required}))
    available_values = tuple(sorted({str(item) for item in available}))
    missing_values = tuple(sorted(set(required_values).difference(available_values)))
    limitation_values = tuple(sorted({str(item) for item in limitations}))
    state: CoverageState
    if not required_values:
        state = "unresolved"
        limitation_values = tuple(
            sorted(set(limitation_values) | {"no required evidence was declared"})
        )
    elif missing_values and available_values:
        state = "partial"
    elif missing_values:
        state = "missing"
    elif limitation_values:
        state = "unresolved"
    else:
        state = "complete"
    return EvidenceCoverage(
        required=required_values,
        available=available_values,
        missing=missing_values,
        state=state,
        limitations=limitation_values,
    )
