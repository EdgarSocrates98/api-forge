---
sdd: 1
feature: API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N
phase: build
profile: standard
status: draft
upstream:
  path: plan.md
  sha256: "86bd76d09531985e1a6b0ca49c26599c663d6e743197a5eb600521943b1aac2a"
tasks:
  - id: host-http
    status: done
    evidence: sdd/API_FORGE_OBSERVABILITY_HOST_HTTP_REQUESTER_N/evidence/requester-tests.txt
claims: [https-only, allowlisted, no-secret-resolution]
---
# build

Requester host-owned implementado sem cliente HTTP obrigatório no núcleo.
