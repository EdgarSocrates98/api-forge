---
sdd: 1
feature: API_FORGE_STEP11_LAB_KNOWLEDGE
phase: contract
profile: critical
status: done
covers:
  - freshness-vocabulary
  - pack-applicability
  - knowledge-drift
  - knowledge-impact-graph
  - lab-scenario-catalog
  - agentic-doctor
  - supply-chain-audit
  - ci-parity-wheel
  - unresolved-honesty
contracts:
  - PackApplicability/v1
  - KnowledgeDrift/v1
  - KnowledgeImpactReport/v1
  - AgenticDoctorSection/v1
  - AgenticDoctorReport/v1
  - LabScenario/v1
  - LabReport/v1
refusal_codes:
  - AF-LAB-CATALOG-MISSING
  - AF-LAB-CATALOG-INVALID
  - AF-LAB-CELL-INVALID
  - AF-LAB-CELL-CONFLICT
  - AF-LAB-CELL-UNDECLARED
  - AF-DOCTOR-CASE-INVALID
  - AF-DOCTOR-MEMORY-QUARANTINE
  - AF-DOCTOR-TRUST-POLICY-MISSING
  - AF-DOCTOR-TRUST-POLICY-INVALID
  - AF-DOCTOR-EVAL-CORPUS-README
  - AF-DOCTOR-EVAL-CORPUS-PARSE
  - AF-DOCTOR-SDD-CHAIN-GAP
upstream:
  path: intent.md
  sha256: "7501182c49454ae621402de4929870abbbb63dbc3e7b17c8487bcc9047db12b6"
---

# contract

`FreshnessState` is extended additively with `verified`, `conflicted`
and `deprecated`; `PackFreshness` gains `last_validated` and an
optional `applies_to` block (`PackApplicability`); `SignalFreshness`
becomes the canonical `FreshnessState` so scorecard freshness flows
unchanged into routing signals. Downstream trust sets treat `verified`
as fresh-or-better and `conflicted`/`deprecated` as untrusted — the
champion lane accepts `{"fresh", "verified"}` and observed-value
exclusion adds the two new untrusted states.

`KnowledgeDrift` rolls `SourceObservation` receipts into one verdict
per pack: `verified` requires hash+version+window agreement, receipt
disagreement produces `conflicted` with the disagreeing pairs named,
`expires_at` produces `deprecated`, missing receipts produce
`unresolved` — never averaged, never inferred.

`KnowledgeImpactReport` carries declared source→pack→rule→skill→eval
nodes and edges (`NodeKind` gains `knowledge`, `skill`, `source`); the
agent→knowledge edge is named unresolved because no declared carrier
exists.

`LabScenario`/`LabReport` model the §28 catalog: every cell carries a
kind and either coverage pointers (fixture/eval/proof) or a declared
gap — both, or neither, refuses. `AgenticDoctorReport` aggregates
eight planes (`AgenticDoctorSection` each) with findings, unlocks and
unresolved.
