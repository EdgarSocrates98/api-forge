---
sdd: 1
feature: API_FORGE_AGENTOPS_CONTROL_PLANE_2
phase: secure
profile: standard
status: done
upstream:
  path: verify.md
  sha256: "33b11f5285c5d4881b8353f6dedd88ab68b00441df01a9390b1b45278e2f414f"
threat_model: docs/security/threat-model-mvp.md
---

# secure

O Control Plane não executa comandos, não acessa rede e não autoriza mutações.
Estados terminais, limites de chamadas e dependências inválidas são recusados
com códigos `AF-CONTROL-*`.
