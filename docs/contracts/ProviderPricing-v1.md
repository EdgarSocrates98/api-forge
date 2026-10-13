# ProviderPricing/v1

§21 versioned price row — declared in a yaml catalog
(`rules/provider_pricing.yaml` or caller `--pricing`), never hardcoded
in source.

| Field | Meaning |
|---|---|
| `provider` / `model` | What the price applies to |
| `effective_at` | When the price takes effect; `price_for` resolves the latest row at or before the requested instant |
| `currency` | ISO-style currency label (e.g. `USD`) |
| `source` | Where the price was declared from (operator sheet, official page, …) |
| `input_per_mtok` / `output_per_mtok` | Per-million-token rates |
| `cached_input_per_mtok` / `cache_creation_per_mtok` / `reasoning_per_mtok` | Optional rates for the §20 extended fields |

A `null` rate means the price is unknown: `cost_for` reports it under
`missing_rates`, never infers one.
