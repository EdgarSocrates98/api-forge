---
sdd: 1
feature: API_FORGE_CYCLE12_PORTABLE_DIST
phase: secure
profile: standard
status: done
upstream:
  path: verify.md
  sha256: "55046faa9efc1ffd48bf7d82513f4ab606b5d144c5cc1611367095a8a7d53772"
threat_model: packaged distribution — supply-chain and path traversal
checks:
  - AF-KNOW-DOMAIN refuses traversal in domain (CLI+MCP call sites)
  - --allow-url gate on direct references; userinfo redacted
  - writes into site-packages refused
---

# secure

Security review for the distribution slice.
