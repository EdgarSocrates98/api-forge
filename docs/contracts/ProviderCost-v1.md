# ProviderCost/v1

The §19 last hop: a `TokenAccounting` priced under a `ProviderPricing`
row. Every component is declared math; gaps stay named.

| Field | Meaning |
|---|---|
| `provider` / `model` / `currency` | Echoed from the pricing row |
| `components` | Per-field cost (`input`, `output`, `cached_input`, `cache_creation`, `reasoning`) — present only when tokens *and* rate both exist |
| `total` | Sum of components; `null` when nothing could be priced |
| `basis` | Carried from the accounting — an estimated accounting produces an estimated cost |
| `missing_rates` | Rate fields absent where tokens were present |
| `unresolved` | Token fields the provider did not report |

Invariant — NEVER PRICED BY INFERENCE: a provider/model absent from the
catalog refuses with `AF-ECONOMY-PRICING-MISSING`; a token field without
a rate lands in `missing_rates`.
