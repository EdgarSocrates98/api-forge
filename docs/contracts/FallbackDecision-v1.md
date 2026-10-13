# FallbackDecision/v1

§32 routing when an active route degrades. Every active route declares a
`fallback_route`; a degraded route with none refuses rather than silently
continuing.

| Field | Meaning |
|---|---|
| `trigger` | One of the five §32 triggers, or `null` |
| `action` | `continue_active`, `use_fallback` or `refuse` |
| `fallback_route` | The declared destination when `use_fallback` |
| `code` | `AF-GOV-FALLBACK-MISSING` when degraded with no declared fallback |
