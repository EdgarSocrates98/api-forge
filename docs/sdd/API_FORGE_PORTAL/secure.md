---
sdd: 1
feature: API_FORGE_PORTAL
phase: secure
profile: standard
status: draft
upstream:
  path: verify.md
  sha256: "a97fb9bfaba4aa1ad973559e11eafb358cd0e8664d7348d280e383a1fdff3262"
threat_model: >
  Servidor local-only (127.0.0.1) para um único operador. Ameaças declaradas:
  acesso sem token de sessão (mitigado: 403 em /api/v1/*; teste
  test_bootstrap_exige_sessao), mutação sem consentimento (mitigado: plan_token
  HMAC + confirm explícito; PORTAL-PLAN-STALE/PORTAL-CONFIRM), path escape nos
  args de analyze (mitigado: resolução confinada ao workspace; AF-PORTAL-INPUT),
  execução arbitrária via intent (mitigado: tabela fixa de verbos seguros;
  AF-PORTAL-AMBIGUOUS) e launch de host sem TTY (mitigado: retorna
  launch_command, nunca subprocess). Sem TLS por desenho — loopback single-user.
---

# secure

Matriz herdada do portal_core (sessão, plan tokens, confirmação) mais as
fronteiras específicas do api-forge (sandbox de workspace no analyze).
