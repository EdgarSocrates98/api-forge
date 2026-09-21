"""``sdd evidence`` — derive a gate's evidence file from a real artifact.

Gates check for ``<feature>/evidence/<satisfied_by>.json``. This verb writes
that file *from* an artifact — hashing the source and extracting the fields
the kind knows how to read — so a gate closes on evidence, not on an
``--override-gate`` override. The source hash makes reuse visible: swap the
artifact and the recorded hash stops matching the file on disk.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from apiforge.core.yaml import StrictYamlError, load_yaml_mapping, split_frontmatter
from apiforge.sdd.models import SddError, load_gates

_PYTEST_TAIL = re.compile(
    r"(\d+)\s+passed|(\d+)\s+failed|(\d+)\s+skipped|(\d+)\s+error"
)


def _extract_plan_tasks(text: str) -> dict[str, Any]:
    meta, _ = split_frontmatter(text)
    if meta is None:
        raise SddError(
            "AF-SDD-EVIDENCE-EXTRACT", "plan.tasks: source has no frontmatter"
        )
    data = load_yaml_mapping(meta, source="plan.md frontmatter")
    tasks = data.get("tasks") or []
    return {
        "tasks": [
            {"id": t.get("id"), "status": t.get("status")}
            for t in tasks
            if isinstance(t, dict)
        ]
    }


def _extract_test_results(text: str) -> dict[str, Any]:
    counts = {"passed": 0, "failed": 0, "skipped": 0, "error": 0}
    for match in _PYTEST_TAIL.finditer(text):
        for name, group in zip(
            ("passed", "failed", "skipped", "error"), match.groups()
        ):
            if group:
                counts[name] += int(group)
    if not any(counts.values()):
        raise SddError(
            "AF-SDD-EVIDENCE-EXTRACT",
            "test.results: source has no pytest tally (N passed/failed)",
        )
    return counts


_EXTRACTORS = {
    "plan.tasks": _extract_plan_tasks,
    "test.results": _extract_test_results,
}


def emit_evidence(
    root: Path,
    feature: str,
    kind: str,
    source: Path,
    now: str,
    *,
    state_dir: Path | None = None,
) -> dict[str, Any]:
    """Write the gate evidence file ``set_phase`` looks for, derived from
    ``source`` — same default location as ``set_phase``
    (``<root>/../.apiforge/sdd/<feature>/evidence/``).

    ``kind`` must be a gate's ``satisfied_by`` — the closed set in
    gates.yaml. ``now`` is explicit (the platform's only clock).
    """
    known = {g.satisfied_by for g in load_gates()}
    if kind not in known:
        raise SddError(
            "AF-SDD-EVIDENCE-KIND",
            f"evidence kind {kind!r} satisfies no gate; known: {sorted(known)}",
        )
    source = Path(source)
    if not source.is_file():
        raise SddError("AF-SDD-EVIDENCE-SOURCE", f"source {source} is not a file")
    raw = source.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    extractor = _EXTRACTORS.get(kind)
    try:
        extracted = extractor(raw.decode("utf-8")) if extractor else {}
    except (StrictYamlError, ValueError) as exc:
        raise SddError(
            "AF-SDD-EVIDENCE-EXTRACT", f"{kind}: cannot read source ({exc})"
        ) from exc

    root = Path(root)
    if not (root / feature).is_dir():
        raise SddError("AF-SDD-NOT-FOUND", f"no feature {feature!r} under {root}")
    if state_dir is None:
        state_dir = root.parent.parent / ".apiforge" / "sdd" / feature
    payload = {
        "extracted": extracted,
        "kind": kind,
        "recorded_at": now,
        "source_path": str(source),
        "source_sha256": digest,
    }
    out = state_dir / "evidence" / f"{kind}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload | {"evidence_file": str(out)}
