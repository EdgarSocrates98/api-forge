"""§23 the live-eval layer: deterministic tier observed, provider tier
declared ``deferred_external`` until a provider adapter plus human
approval exists. The layer never gates CI on the provider tier — an
undeclared provider run reports ``unresolved``, never a fabricated
pass/fail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.eval_plane import LiveEvalLayer, LiveEvalReport

LAYER_FILE = Path(__file__).resolve().parent.parent / "rules" / "live_evals.yaml"

_RUNNERS = {
    "agentic_quality": "apiforge.evals.agentic_quality:run_agentic_quality",
    "security_adversarial": "apiforge.evals.security_adversarial:run_security_adversarial",
    "memory_evals": "apiforge.evals.memory_evals:run_memory_evals",
    "trace_grading": "apiforge.evals.trace_grading:run_trace_grading",
}


def load_layer(path: Path = LAYER_FILE) -> LiveEvalLayer:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    layer = raw.get("layer") or {}
    declared = layer.get("deterministic_evals") or ()
    unknown = [row.get("runner") for row in declared if row.get("runner") not in _RUNNERS]
    if unknown:
        raise ContractError(
            "AF-EVALS-LIVE-LAYER", f"live_evals.yaml declares unknown runners: {unknown}"
        )
    return LiveEvalLayer(
        profiles=tuple(layer.get("profiles") or ("economy", "balanced", "deep")),
        metrics=tuple(layer.get("metrics") or ()),
        deterministic_evals=tuple(str(row.get("id")) for row in declared),
        corpus_refs=tuple(str(row.get("corpus")) for row in declared),
        provider_tier=str(layer.get("provider_tier", "deferred_external")),  # type: ignore[arg-type]
    )


def _runner(name: str) -> Any:
    import importlib

    module_name, _, func = _RUNNERS[name].partition(":")
    return getattr(importlib.import_module(module_name), func)


def run_live_evals(path: Path = LAYER_FILE, *, root: Path | None = None) -> dict[str, Any]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    declared = (raw.get("layer") or {}).get("deterministic_evals") or ()
    layer = load_layer(path)
    base = root or Path(".")
    deterministic: dict[str, Any] = {}
    for row in declared:
        corpus = base / str(row.get("corpus"))
        try:
            result = _runner(str(row.get("runner")))(Path(corpus))
            deterministic[str(row.get("id"))] = {
                "passed": bool(result.get("passed")),
                "totals": result.get("totals"),
            }
        except ContractError as exc:
            deterministic[str(row.get("id"))] = {
                "passed": False,
                "error": str(exc),
            }
    unresolved = [
        (
            "provider tier deferred_external: no provider adapter declared; "
            "live model calls are a human-gated external boundary, never run by the core"
        )
    ]
    report = LiveEvalReport(
        layer=layer,
        deterministic={key: value for key, value in deterministic.items()},
        provider_status="deferred_external",
        unresolved=tuple(unresolved),
    )
    failed = [key for key, row in deterministic.items() if not row.get("passed")]
    return {
        "schema": "apiforge/live-evals/v1",
        "report": report.model_dump(mode="json"),
        "totals": {
            "evals": len(deterministic),
            "failed": len(failed),
            "failed_ids": failed,
        },
        "passed": not failed,
    }


__all__ = ["load_layer", "run_live_evals"]
