---
sdd: 1
feature: API_GRAPH_NEPTUNE
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "63c983ea856358c1371b4a05e93e207f9c1e888d3c379c6281b95ae1b9ecbe7c"
results:
  - gate: ruff, ruff format, mypy src/apiforge
    outcome: pass
    evidence: evidence/build-gates.txt
  - gate: full pytest suite
    outcome: pass
    evidence: 1420 passed; release-gate failure explained (contracts registered; pre-existing untracked file) in evidence/build-gates.txt
  - gate: apiforge evals graph-quality
    outcome: pass
    evidence: 85 cases, precision 1.0 per language, recall 1.0
  - gate: agent lint, skills validate, knowledge check, agent-routing, agentic-quality, economy-hardening
    outcome: pass
    evidence: evidence/build-gates.txt
  - gate: field cycle
    outcome: unresolved
    evidence: no graph-backed target repository
---
# verify

Cada achado cita um fato; planos sem dump mantêm cardinalidade `unresolved`; fixtures de plano
são sintéticas e marcadas.
