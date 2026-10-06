"""§21 Provider Pricing: declared versioned catalog, never inferred."""

from __future__ import annotations

from pathlib import Path

from apiforge.contracts.token_economics import ProviderPricing, TokenAccounting
from apiforge.economy.pricing import cost_for, describe_catalog, load_pricing, price_for


def _row(**kw: object) -> ProviderPricing:
    base = {
        "provider": "p",
        "model": "m",
        "effective_at": "2026-01-01",
        "currency": "USD",
        "source": "declared:test",
        "input_per_mtok": 2.0,
        "output_per_mtok": 10.0,
        "cached_input_per_mtok": 0.5,
        "cache_creation_per_mtok": 3.0,
    }
    return ProviderPricing(**(base | kw))  # type: ignore[arg-type]


def _catalog(tmp_path: Path, rows: list[dict[str, object]]) -> Path:
    path = tmp_path / "pricing.yaml"
    import yaml

    path.write_text(
        yaml.safe_dump({"schema": "apiforge/provider-pricing/v1", "entries": rows}),
        encoding="utf-8",
    )
    return path


def test_load_pricing(tmp_path: Path) -> None:
    path = _catalog(tmp_path, [_row().model_dump(mode="json")])
    catalog = load_pricing(path)
    assert len(catalog) == 1
    assert catalog[0].input_per_mtok == 2.0


def test_load_empty_catalog(tmp_path: Path) -> None:
    assert load_pricing(_catalog(tmp_path, [])) == ()


def test_load_missing_file(tmp_path: Path) -> None:
    assert load_pricing(tmp_path / "nope.yaml") == ()


def test_price_for_latest_effective_at() -> None:
    old = _row(effective_at="2025-01-01", input_per_mtok=1.0)
    new = _row(effective_at="2026-01-01", input_per_mtok=2.0)
    assert price_for([old, new], "p", "m") is new
    # order independent
    assert price_for([new, old], "p", "m") is new


def test_price_for_respects_horizon() -> None:
    old = _row(effective_at="2025-01-01", input_per_mtok=1.0)
    new = _row(effective_at="2026-06-01", input_per_mtok=2.0)
    resolved = price_for([old, new], "p", "m", at="2026-01-15")
    assert resolved is old


def test_price_for_no_eligible_row() -> None:
    new = _row(effective_at="2026-06-01")
    assert price_for([new], "p", "m", at="2025-01-01") is None


def test_price_for_missing_model() -> None:
    assert price_for([_row()], "p", "other") is None


def test_price_for_iso_datetime_at() -> None:
    old = _row(effective_at="2025-01-01")
    new = _row(effective_at="2026-01-01T00:00:00Z")
    resolved = price_for([old, new], "p", "m", at="2026-02-01T12:00:00+00:00")
    assert resolved is new


def test_cost_for_full_accounting() -> None:
    pricing = _row()
    usage = TokenAccounting(
        basis="observed",
        input_tokens=1_000_000,
        output_tokens=500_000,
        cached_input_tokens=200_000,
        cache_creation_tokens=100_000,
    )
    cost = cost_for(usage, pricing)
    assert cost.components["input"] == 2.0
    assert cost.components["output"] == 5.0
    assert cost.components["cached_input"] == 0.1
    assert cost.components["cache_creation"] == 0.3
    assert cost.total == 7.4
    assert "reasoning_tokens" in cost.unresolved
    assert cost.basis == "observed"


def test_cost_for_missing_rate_named() -> None:
    pricing = _row(cached_input_per_mtok=None)
    usage = TokenAccounting(basis="observed", cached_input_tokens=100)
    cost = cost_for(usage, pricing)
    assert "cached_input_per_mtok" in cost.missing_rates
    assert "cached_input" not in cost.components


def test_cost_for_estimated_keeps_label() -> None:
    usage = TokenAccounting(basis="estimated", input_tokens=10, estimation_method="x")
    cost = cost_for(usage, _row())
    assert cost.basis == "estimated"


def test_cost_for_empty_components_total_none() -> None:
    usage = TokenAccounting(basis="unresolved", source="x")
    cost = cost_for(usage, _row())
    assert cost.total is None
    assert set(cost.unresolved) == {
        "input_tokens",
        "output_tokens",
        "cached_input_tokens",
        "cache_creation_tokens",
        "reasoning_tokens",
    }


def test_describe_catalog() -> None:
    info = describe_catalog([_row()])
    assert info["count"] == 1
    assert info["entries"][0]["source"] == "declared:test"
