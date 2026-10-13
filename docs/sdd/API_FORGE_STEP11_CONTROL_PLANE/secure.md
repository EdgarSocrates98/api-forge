---
sdd: 1
feature: API_FORGE_STEP11_CONTROL_PLANE
phase: secure
profile: critical
status: done
threat_model:
  - premature takeover — shadow/assisted can never govern; only an approved
    gate plus the five §31 requirements activates a candidate
  - silent promotion — transitions are append-only rows with the approval
    id recorded; the yaml stays immutable so history is auditable
  - fallback loops — terminal routes declare no fallback; a degraded
    terminal refuses instead of recursing
  - evidence smuggling — evidence.route must equal the promoted route or
    AF-GOV-MODE-TRANSITION-INVALID refuses
  - shadow pollution — shadow records are a separate append-only ledger;
    corrupt rows refuse AF-GOV-STORE-CORRUPT rather than being skipped
  - trigger smuggling — the trigger vocabulary is closed; undeclared names
    refuse AF-GOV-TRIGGER-INVALID at the CLI boundary
upstream:
  path: verify.md
  sha256: "d8d24e64d925037a4f654bf23fddf3025b073532e635cef6e05abccaf551849a"
---

# secure
