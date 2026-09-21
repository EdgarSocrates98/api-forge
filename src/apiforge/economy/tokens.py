"""Provider tokens: counted from a host transcript, or estimated — never mixed.

A transcript is JSONL written by the host CLI; lines carrying
``message.usage`` (``input_tokens``/``output_tokens``/``cache_*``) are summed
per ``message.model``. Without a transcript the report stays
``tokens_unresolved`` — an estimate over ``payload_bytes`` (chars/4) is only
produced when ``--estimate`` asks for it, and it is labeled, never counted.
Cost requires a ``--cost-basis`` yaml; a model missing from the basis lands
in ``cost_basis_missing``, never priced by inference.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

USAGE_KEYS = (
    "input_tokens",
    "output_tokens",
    "cache_read_input_tokens",
    "cache_creation_input_tokens",
)


class TokenError(ValueError):
    """A refused token/cost computation; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _zero_usage() -> dict[str, int]:
    return {key: 0 for key in USAGE_KEYS} | {"messages": 0}


def read_transcript(path: Path) -> dict[str, Any]:
    """Sum ``message.usage`` per model; unparseable lines are counted, not fatal."""
    if not path.is_file():
        raise TokenError("AF-ECONOMY-TRANSCRIPT-MISSING", f"no transcript at {path}")
    by_model: dict[str, dict[str, int]] = {}
    unparsed = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            unparsed += 1
            continue
        if not isinstance(entry, dict):
            continue
        message = entry.get("message")
        if not isinstance(message, dict):
            continue
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue
        model = str(message.get("model") or entry.get("model") or "unknown")
        bucket = by_model.setdefault(model, _zero_usage())
        bucket["messages"] += 1
        for key in USAGE_KEYS:
            value = usage.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                bucket[key] += value
    return {
        "models": dict(sorted(by_model.items())),
        "unparsed_lines": unparsed,
        "counted": True,
        "transcript": str(path),
    }


def estimate_tokens(payload_bytes: int) -> dict[str, Any]:
    """chars/4 heuristic — labeled estimate, never presented as counted."""
    return {
        "estimated_tokens": payload_bytes // 4,
        "estimation_method": "payload_bytes/4",
        "counted": False,
    }


def _load_basis(path: Path) -> dict[str, dict[str, float]]:
    if not path.is_file():
        raise TokenError("AF-ECONOMY-COST-BASIS-MISSING", f"no cost basis at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TokenError(
            "AF-ECONOMY-COST-BASIS-MISSING", f"{path} is not a model→rates mapping"
        )
    basis: dict[str, dict[str, float]] = {}
    for model, rates in data.items():
        if not isinstance(rates, dict):
            continue
        basis[str(model)] = {
            "input_per_mtok": float(rates.get("input_per_mtok", 0.0)),
            "output_per_mtok": float(rates.get("output_per_mtok", 0.0)),
        }
    return basis


def cost(transcript: dict[str, Any], basis_path: Path) -> dict[str, Any]:
    """Dollar cost per model; models outside the basis are named, not priced."""
    basis = _load_basis(basis_path)
    per_model: dict[str, dict[str, object]] = {}
    missing: list[str] = []
    total = 0.0
    for model, usage in transcript.get("models", {}).items():
        rates = basis.get(model)
        if rates is None:
            missing.append(model)
            continue
        usd = (
            usage["input_tokens"] * rates["input_per_mtok"]
            + usage["output_tokens"] * rates["output_per_mtok"]
        ) / 1_000_000
        per_model[model] = {"usd": round(usd, 6)}
        total += usd
    return {
        "total_usd": round(total, 6),
        "per_model": dict(sorted(per_model.items())),
        "cost_basis_missing": sorted(missing),
        "basis": str(basis_path),
    }
