"""§29 knowledge-drift eval — drift verdicts over declared pack+receipt cases.

Each case materializes a synthetic pack (pack.yaml + source_authority)
under an isolated root and a list of SourceObservation receipts, then
compares the rolled-up KnowledgeDrift state, conflicts and unresolved
against the declared expectation. Fully offline; nothing fetches.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.knowledge import SourceObservation
from apiforge.knowledge.drift import detect_pack_drift
from apiforge.knowledge.loader import load_pack


def _materialize_pack(root: Path, spec: dict[str, Any]) -> Path:
    pack_dir = root / str(spec.get("domain", "eval-pack"))
    pack_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        f"domain: {spec.get('domain', 'eval-pack')}",
        f"version: {int(spec.get('pack_version', 1))}",
        "areas: []",
        "rule_ids: []",
    ]
    freshness = spec.get("freshness")
    if freshness:
        rendered = ", ".join(
            f"{k}: {json.dumps(v) if isinstance(v, str) else v}" for k, v in freshness.items()
        )
        lines.append(f"freshness: {{{rendered}}}")
    (pack_dir / "pack.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    source = spec.get("source") or {}
    (pack_dir / "source_authority.yaml").write_text(
        "sources:\n"
        f"  - name: {source.get('name', 'eval-source')}\n"
        f"    url: {source.get('url', 'https://example.com')}\n"
        f"    authority: {source.get('authority', 'project-docs')}\n"
        f"    verified: '{source.get('verified', '2026-09-20')}'\n",
        encoding="utf-8",
    )
    return pack_dir


def _receipt(raw: dict[str, Any]) -> SourceObservation:
    return SourceObservation(
        source=str(raw.get("source", "eval-source")),
        observed_at=str(raw["observed_at"]),
        source_hash=raw.get("source_hash"),
        source_version=raw.get("source_version"),
        receipt_ref=str(raw.get("receipt_ref", "receipt:eval:1")),
    )


def run_knowledge_drift(corpus: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    failed: list[str] = []
    for case_path in sorted(Path(corpus).glob("*.yaml")):
        raw = yaml.safe_load(case_path.read_text(encoding="utf-8")) or {}
        case_id = str(raw.get("id", case_path.stem))
        with tempfile.TemporaryDirectory(prefix="af-drift-eval-") as tmp:
            case_root = Path(tmp)
            try:
                pack_dir = _materialize_pack(case_root, raw.get("pack") or {})
                pack = load_pack(pack_dir)
                receipts = tuple(_receipt(entry) for entry in raw.get("receipts") or [])
                drift = detect_pack_drift(pack, receipts, now=str(raw["now"]))
                expect = raw.get("expect") or {}
                problems: list[str] = []
                if expect.get("state") and drift.state != expect["state"]:
                    problems.append(f"state {drift.state} != {expect['state']}")
                if expect.get("conflicts_min") is not None and (
                    len(drift.conflicts) < int(expect["conflicts_min"])
                ):
                    problems.append(f"conflicts {len(drift.conflicts)} < {expect['conflicts_min']}")
                if expect.get("unresolved") is True and not drift.unresolved:
                    problems.append("expected unresolved entries, got none")
                if expect.get("unresolved") is False and drift.unresolved:
                    problems.append(f"unexpected unresolved: {list(drift.unresolved)}")
                results.append(
                    {
                        "id": case_id,
                        "state": drift.state,
                        "conflicts": len(drift.conflicts),
                        "passed": not problems,
                        "problems": problems,
                    }
                )
                if problems:
                    failed.append(case_id)
            except ContractError as exc:
                results.append({"id": case_id, "passed": False, "problems": [str(exc)]})
                failed.append(case_id)
    return {
        "schema": "apiforge/knowledge-drift-evals/v1",
        "totals": {"cases": len(results), "failed": len(failed), "failed_ids": failed},
        "cases": results,
        "passed": not failed,
    }


__all__ = ["run_knowledge_drift"]
