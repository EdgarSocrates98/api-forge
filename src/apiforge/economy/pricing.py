"""§21 Provider Pricing: versioned price catalog — declared, never inferred.

Prices come from a yaml catalog (``rules/provider_pricing.yaml`` or a
caller-supplied file with the same schema), never from hardcoded source
constants. ``price_for`` resolves the most recent ``effective_at`` row at
or before the requested instant; a provider/model absent from the catalog
returns ``None`` and callers report the gap as unresolved.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.token_economics import (
    ProviderCost,
    ProviderPricing,
    TokenAccounting,
)

PRICING_FILE = Path(__file__).resolve().parent.parent / "rules" / "provider_pricing.yaml"

# (accounting field, rate field, cost component name)
_RATE_MAP: tuple[tuple[str, str, str], ...] = (
    ("input_tokens", "input_per_mtok", "input"),
    ("output_tokens", "output_per_mtok", "output"),
    ("cached_input_tokens", "cached_input_per_mtok", "cached_input"),
    ("cache_creation_tokens", "cache_creation_per_mtok", "cache_creation"),
    ("reasoning_tokens", "reasoning_per_mtok", "reasoning"),
)


def load_pricing(path: Path = PRICING_FILE) -> tuple[ProviderPricing, ...]:
    """Load a pricing catalog yaml; malformed rows are refused loudly."""
    if not path.is_file():
        return ()
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return ()
    rows = data.get("entries")
    if not isinstance(rows, list):
        return ()
    return tuple(ProviderPricing.model_validate(row) for row in rows)


def _at(value: str) -> datetime:
    """Parse an effective_at/date-ish string; naive dates count as UTC."""
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    for candidate in (text, f"{text}T00:00:00+00:00"):
        try:
            stamp = datetime.fromisoformat(candidate)
        except ValueError:
            continue
        return stamp if stamp.tzinfo else stamp.replace(tzinfo=UTC)
    return datetime.min.replace(tzinfo=UTC)


def price_for(
    catalog: tuple[ProviderPricing, ...] | list[ProviderPricing],
    provider: str,
    model: str,
    *,
    at: str | None = None,
) -> ProviderPricing | None:
    """Most recent effective row for ``provider``+``model`` at ``at``.

    ``at=None`` resolves at the latest declared effective_at (catalog order
    independent). Rows effective *after* ``at`` never leak into the past.
    """
    rows = [row for row in catalog if row.provider == provider and row.model == model]
    if not rows:
        return None
    if at is None:
        return max(rows, key=lambda row: _at(row.effective_at))
    horizon = _at(at)
    eligible = [row for row in rows if _at(row.effective_at) <= horizon]
    if not eligible:
        return None
    return max(eligible, key=lambda row: _at(row.effective_at))


def cost_for(accounting: TokenAccounting, pricing: ProviderPricing) -> ProviderCost:
    """Price an observed/estimated accounting — components declared only.

    A token field the provider did not report lands in ``unresolved``; a
    token field present without a matching rate lands in ``missing_rates``.
    Neither is ever guessed.
    """
    components: dict[str, float] = {}
    missing_rates: list[str] = []
    unresolved: list[str] = []
    for field, rate_field, component in _RATE_MAP:
        tokens = getattr(accounting, field)
        rate = getattr(pricing, rate_field)
        if tokens is None:
            unresolved.append(field)
        elif rate is None:
            missing_rates.append(rate_field)
        else:
            components[component] = round(tokens * rate / 1_000_000, 6)
    return ProviderCost(
        provider=pricing.provider,
        model=pricing.model,
        currency=pricing.currency,
        components=components,
        total=round(sum(components.values()), 6) if components else None,
        basis=accounting.basis,
        missing_rates=tuple(sorted(missing_rates)),
        unresolved=tuple(sorted(unresolved)),
    )


def describe_catalog(
    catalog: tuple[ProviderPricing, ...] | list[ProviderPricing],
) -> dict[str, Any]:
    """Compact projection of a catalog for CLI output."""
    return {
        "entries": [
            {
                "provider": row.provider,
                "model": row.model,
                "effective_at": row.effective_at,
                "currency": row.currency,
                "source": row.source,
            }
            for row in catalog
        ],
        "count": len(catalog),
    }


__all__ = [
    "PRICING_FILE",
    "cost_for",
    "describe_catalog",
    "load_pricing",
    "price_for",
]
