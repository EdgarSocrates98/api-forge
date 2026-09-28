# ProviderCapability/v1

`ProviderCapability/v1` rows come from `rules/providers.yaml` (`apiforge economy providers`).
The Economy Plane reasons over these capabilities, never over provider names.

| Field | Meaning |
|---|---|
| `provider` / `tier` | Descriptor name and tier T1 (cheap/local), T2 (strong general), T3 (strongest/reviewer) |
| `structured_output` / `tool_calling` / `deferred_tools` | Declared host/model capabilities |
| `context_window` / `reports_usage` / `cost_tier` / `local` | Declared limits and cost class |
