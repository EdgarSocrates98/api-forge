"""Independent checks for the public capability matrix."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.platform import CapabilityRecord


def _resolve(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def verify_capabilities(
    records: tuple[CapabilityRecord, ...],
    *,
    root: Path | None = None,
) -> dict[str, object]:
    """Return a serializable verification report without mutating the matrix."""
    base = Path(root or Path.cwd())
    gaps: list[str] = []
    seen: set[str] = set()
    for record in records:
        if record.capability_id in seen:
            gaps.append(f"duplicate capability: {record.capability_id}")
        seen.add(record.capability_id)
        if not record.limitations:
            gaps.append(f"{record.capability_id}: limitations are required")
        if not record.verifier:
            gaps.append(f"{record.capability_id}: verifier is required")
        if not record.documentation:
            gaps.append(f"{record.capability_id}: documentation is required")
        elif not _resolve(base, record.documentation).is_file():
            gaps.append(f"{record.capability_id}: documentation missing: {record.documentation}")
        if record.state == "supported" and not record.evidence:
            gaps.append(f"{record.capability_id}: supported capability has no evidence")
    return {
        "ok": not gaps,
        "capability_count": len(records),
        "verified": len(records) - len(gaps),
        "gaps": tuple(sorted(gaps)),
        "capabilities": tuple(record.capability_id for record in records),
    }
