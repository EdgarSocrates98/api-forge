"""§43 tool token benchmark: measured response bytes + labeled token estimate.

Samples come from the declared set in ``rules/tool_benchmark.yaml`` — each
entry names a read-only tool and the kwargs to invoke it with. Responses are
serialized to JSON, measured in bytes, and token-estimated with the economy
chars/4 heuristic — always labeled ``estimated``, never presented as counted.
Tools that refuse, raise or are not on the registry land in ``unresolved``.
"""

from __future__ import annotations

import json
import statistics
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_surface import ToolBenchmark, ToolBenchmarkReport

POLICY_INVALID_CODE = "AF-MCP-BENCHMARK-POLICY"
POLICY_PATH = Path(__file__).resolve().parents[1] / "rules" / "tool_benchmark.yaml"


def _load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or POLICY_PATH
    try:
        raw = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except OSError as exc:
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: {exc}") from exc
    if not isinstance(raw.get("samples"), Mapping):
        raise ContractError(POLICY_INVALID_CODE, f"{policy_path}: samples mapping missing")
    return dict(raw["samples"])


def _measure(fn: Any, kwargs: dict[str, Any], root: Path) -> int | None:
    """Invoke one read-only tool inside an isolated root; return response bytes."""
    args = {key: (str(root) if value == "$root" else value) for key, value in kwargs.items()}
    try:
        result = fn(**args)
    except Exception:  # noqa: BLE001 — a refusal still counts as a measured response
        return None
    try:
        return len(json.dumps(result, default=str).encode("utf-8"))
    except (TypeError, ValueError):
        return None


def benchmark_tools(
    samples: dict[str, Any] | None = None,
    *,
    repeats: int = 3,
) -> ToolBenchmarkReport:
    """Run the declared sample set and rank tools by median response bytes."""
    declared = samples if samples is not None else _load_policy()
    from apiforge.economy.tokens import estimate_tokens
    from apiforge.mcp.gateway import full_tools

    known = full_tools()
    unresolved: list[str] = []
    benchmarks: list[ToolBenchmark] = []

    with tempfile.TemporaryDirectory(prefix="af-mcp-bench-") as tmp:
        root = Path(tmp)
        for name in sorted(declared):
            fn = known.get(name)
            spec = declared[name]
            if fn is None:
                unresolved.append(f"sample {name}: tool not on the registry")
                continue
            kwargs = dict(spec.get("kwargs") or {}) if isinstance(spec, Mapping) else {}
            sizes: list[int] = []
            for _ in range(max(1, repeats)):
                size = _measure(fn, kwargs, root)
                if size is not None:
                    sizes.append(size)
            if not sizes:
                unresolved.append(f"sample {name}: every invocation refused or failed")
                continue
            tokens = [int(estimate_tokens(size).get("estimated_tokens") or 0) for size in sizes]
            usefulness: Literal["met", "missed", "unresolved"] = "unresolved"
            if isinstance(spec, Mapping) and "max_bytes" in spec:
                limit = int(spec["max_bytes"])
                usefulness = "met" if statistics.median(sizes) <= limit else "missed"
            benchmarks.append(
                ToolBenchmark(
                    tool=name,
                    samples=len(sizes),
                    median_bytes=int(statistics.median(sizes)),
                    p95_bytes=int(sorted(sizes)[max(0, int(len(sizes) * 0.95) - 1)]),
                    median_tokens_est=int(statistics.median(tokens)),
                    p95_tokens_est=int(sorted(tokens)[max(0, int(len(tokens) * 0.95) - 1)]),
                    usefulness=usefulness,
                )
            )

    benchmarks.sort(key=lambda item: (-item.median_bytes, item.tool))
    return ToolBenchmarkReport(
        tools=tuple(benchmarks),
        ranking=tuple(item.tool for item in benchmarks),
        unresolved=tuple(unresolved),
    )


__all__ = ["benchmark_tools"]
