---
sdd: 1
feature: API_FORGE_STEP11_TOKEN_ECONOMICS
phase: secure
profile: critical
status: done
threat_model:
  - fabricated pricing — no price is hardcoded in source; the shipped catalog
    is empty and every row declares provider/model/effective_at/currency/source;
    unknown provider/model refuses AF-ECONOMY-PRICING-MISSING
  - basis laundering — estimated rows require a declared estimation_method,
    unresolved rows reject token counts, and ledger rollups never merge bases
  - silent incompleteness — token fields the provider did not report land in
    ProviderCost.unresolved, rates missing for reported fields land in
    missing_rates, reconciliation axes missing on either side stay named
  - false gain claims — calibration_error only exists when both sides carry a
    value; a zero estimate against a positive observation cannot express a
    ratio and stays unresolved
  - tampered usage rows — ledger files are append-only jsonl; malformed lines
    are counted as unparsed_rows, never silently dropped
upstream:
  path: verify.md
  sha256: "c11c6f5573a46825d3cff5a372094c9f58bf2cc3dc730431708bb875e26e5c65"
---

# secure
