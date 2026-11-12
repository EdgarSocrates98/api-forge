# SDD Baseline — api-forge (Onda 0)

- SHA `e722e2abd392` · branch `release/cycle-2.7-patch-version` · `.git` present · ~133 dirty files (pré-existentes)
- Python ≥3.12 · suíte `tests/sdd/` (checks/evidence/load/stamp/risk)
- SDD: `src/apiforge/sdd/` (9 módulos) · 10 fases · gates.yaml 6 gates · profiles.yaml 5 perfis (critical≡migration)
- Skill canônica `.agents/skills/api-forge-sdd/`; mirrors via `scripts/sync_skills.py`; parity no CI
- CLI `apiforge sdd {check|status|stamp|classify|set-phase|evidence}`

## Findings

| # | Sev | Finding | Evidência |
|---|---|---|---|
| F1 | P0 | `set_phase()` — `evidence_dir/<x>.json is_file()` ⇒ gate pass; zero validação de conteúdo | service.py:48-50 |
| F2 | P0 | `failed>0` não bloqueia — "10 passed, 50 failed" destrava verify gate | evidence.py:37-48 |
| F3 | P0 | `source_sha256` gravado mas nunca verificado no gate | evidence.py:83 |
| F4 | P1 | Overrides: reason/actor vazios permitidos, sem timestamp, todos os gates dispensáveis, JSON sem assinatura | service.py:72-90 |
| F5 | P1 | Gates opt-in — só `--strict` + status ready/done; `not_required`/`superseded` bypass total | service.py:19,44 |
| F6 | P1 | `_PYTEST_TAIL` faz finditer no arquivo inteiro — qualquer "N passed" conta | evidence.py:21,39 |
| F7 | P1 | `sdd check` ausente do CI sobre docs/sdd | ci.yml |
| F8 | P1 | Códigos AF-SDD-* não catalogados (regra AGENTS) | docs/catalog-contract.md |
| F9 | P2 | `sdd set-phase` sem `--evidence-dir` — evidence emitida onde o gate não olha | cli_governance.py:151-194 |
| F10 | P2 | `status()` default silencioso profile→standard | checks.py:166 |
| F11 | P2 | critical≡migration (listas idênticas) | profiles.yaml:6-7 |
| F12 | P2 | `gates.produced_by` nomeiam comandos inexistentes | gates.yaml |

## Capacidades preservadas

Frontmatter cirúrgico (stamp preserva EOL/BOM), extractores pytest-tally, refusal taxonomy AF-SDD-*, risk classify determinístico, contract tooling (openapi diff/grpc compat/contract-intel), skill parity CI.
