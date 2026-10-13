---
name: api-forge-sdd
description: >-
  Conduz mudanças de API pelo Spec-Driven Development do API Forge —
  classificação de risco, perfil (micro/quick/standard/critical/migration),
  fases discover → intent → contract → architecture → plan → build → verify →
  secure → benchmark → ship, ADRs, TaskSpecs seladas, gates por evidência,
  cascata de hashes, rollback e field validation. Use ao iniciar uma feature,
  mudança de contrato, migração, mudança de banco, segurança, performance ou
  infraestrutura; para avançar ou fechar uma fase; quando `sdd check` recusar;
  ou ao decidir se um tema de roadmap justifica uma feature estrutural ("vamos
  começar esta feature", "posso dar ship?", "start a spec"). Não use para
  revisar um único endpoint sem mudança planejada (→ skill do domínio) nem
  para economia de contexto (→ api-forge-context).
compatibility: >-
  Requer `docs/sdd/`, os comandos `apiforge sdd`, `apiforge task` e `apiforge
  runtime`, e o contrato em `docs/sdd-contract.md`.
metadata:
  api-forge-skill: "true"
  version: "1.1"
---

# API Forge — SDD, tasks e gates

O SDD existe para que nenhuma mudança chegue a `ship` apoiada só em intenção.
Cada fase produz um artefato, cada artefato carimba o hash do anterior, e cada
gate abre com evidência — não com flag, texto do agente ou boa vontade.

## Antes de começar

Siga `api-forge-core`. Leia `docs/sdd-contract.md` para o formato dos
artefatos. O estado atual: `apiforge sdd status --root docs/sdd`.

## Procedimento

1. **Classifique o risco antes de escolher o perfil:**
   ```text
   apiforge sdd classify --description "..." --path <p> [--path ...] \
     [--baseline <c> --candidate <c> --protocol openapi|grpc] [--repositories N] --write docs/sdd/<FEATURE>
   ```
   O perfil declarado (`micro`, `quick`, `standard`, `critical`, `migration`)
   nunca fica abaixo do `risk_class`; `sdd check` recusa com
   `AF-SDD-PROFILE-BELOW-RISK`.
2. **Antes de construir**, preencha `discover`, `intent`, `contract`,
   `architecture` e `plan`. Cada fase carrega a skill do domínio
   (`api-forge-discovery`, `-contract`, `-architecture`, ...).
3. **Intent verificável:** critério de sucesso testável, escopo fora,
   decisões abertas e owner.
4. **Tasks atômicas:** cada task tem caminho permitido (writable glob),
   teste ou prova, dependência, risco e rollback.
   ```text
   apiforge task compile ...            # intenção local → TaskSpec draft verificada
   apiforge task create <id> --outcome "..." --writable <glob> --risk <classe>
   apiforge task review <id> → task seal <id> → task plan <id>
   ```
5. **Hashes:** `apiforge sdd stamp` grava o sha256 do upstream; qualquer
   alteração upstream invalida o downstream. `apiforge sdd check --root docs/sdd [--feature F] [--strict]`.
6. **Build** só em sandbox/worktree (`apiforge sandbox apply`, `task run`),
   nunca direto no tree principal.
7. **Verify, secure e benchmark** quando o risco exigir
   (`api-forge-verification`, `api-forge-performance`). Fase dispensada fica
   `not_required` com justificativa.
8. **Evidência e fase:**
   ```text
   apiforge sdd evidence --root docs/sdd --feature F --kind <kind> --from <artefato-real> --now <ISO>
   apiforge sdd set-phase --root docs/sdd --feature F --phase <fase> --status <status> --strict
   ```
   Se a prova não puder existir, use `--override-gate`, `--override-reason`
   e `--override-actor` — override é registrado, nunca silencioso.
9. **Aceite independente:** `apiforge task verify`, `task accept` (aceitante
   ≠ executor) ou `task reject`.
10. **Ship** só com evidence bundle (`apiforge report build|sign|verify`),
    deviations e `unresolved` explícitos. Antes de entregar:
    `apiforge sdd check --root docs/sdd`.

## Execução econômica do runtime

`apiforge runtime run|resume|debate --profile economy|balanced|deep`: o
perfil é preferência, o risco é piso (critical/irreversible ⇒ `deep`). Leia
`economy.status`, `economy.stopped_at` e `economy.codes`: `unresolved` +
`AF-BUDGET-EXHAUSTED` ou `AF-ECONOMY-CEILING` é parcial explícito —
reexecute com perfil maior, nunca complete em silêncio. `L0` significa prova
determinística sem chamada de agente; aceitação continua separada. Antes de
retomar: `apiforge runtime checkpoint <task> <run>`.

## Gates

Evidence unlocks phase gates. Gates são satisfeitos pela presença do
**tipo** de evidência nomeado, derivado de artefato real. Flags, texto do
agente e intenção não substituem evidência.

## Field validation

Temas de roadmap vêm de `apiforge field report` sobre tarefas reais
pré-registradas (`docs/field/README.md`). Nunca abra SDD de feature
estrutural sem tema qualificado (≥5 tarefas verificadas em ≥2 repos) ou
veredito `inconclusive` registrado. O baseline nunca usa
`workspace graph --infer`; `AF-FIELD-FLAG-CONTAMINATION` recusa.
Ciclo: `field record` → `field annotate` → `field verify` (verificador cego)
→ `field report` → `field export`.

## Entrega

Artefatos SDD por fase, plano atômico (TaskSpecs), ADRs, estado dos gates
(`sdd status`), provas por gate, overrides com ator, gaps e próximo passo —
fechando com o Outcome Brief.

Especialistas típicos: `api-planner` (plano), `api-task-spec-reviewer`
(TaskSpec antes do seal), `api-orchestrator` (execução), `api-verifier`
(aceite), `api-release-guardian` (gates e ship).
