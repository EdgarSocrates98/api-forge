---
sdd: 1
feature: API_FORGE_PRODUCT_DOCUMENTATION_RELEASE_H
phase: verify
profile: standard
status: draft
upstream:
  path: build.md
  sha256: "a2f67972ca57db40f2766399d064721d0df2d8986a63274c6b03477aab3c2211"
results:
  - gate: pytest -q
    outcome: pass
    evidence: evidence/release.txt
  - gate: ruff, mypy, release and full SDD checks
    outcome: pass
    evidence: evidence/release.txt
---
# verify

A publicação só é válida após a suíte completa e a árvore Git limpa.
