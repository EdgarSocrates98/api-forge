---
name: api-forge-sdd
description: Conduz mudanças de API pelo SDD do API Forge, da descoberta ao ship, com contratos, ADRs, tasks, gates, evidências, rollback e invalidação por hash. Use para iniciar uma feature, mudança de API, migração, banco, segurança, performance ou infraestrutura.
compatibility: Requer `docs/sdd`, os comandos `apiforge sdd` e o contrato em `docs/sdd-contract.md` quando disponíveis.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Classifique o risco antes de escolher o perfil: `apiforge sdd classify --description "..." --path <p> [--baseline <c> --candidate <c>] --write docs/sdd/<FEATURE>`. O perfil declarado (`micro`, `quick`, `standard`, `critical` ou `migration`) nunca pode ficar abaixo do `risk_class`; `sdd check` recusa com `AF-SDD-PROFILE-BELOW-RISK`.
2. Preencha `discover`, `intent`, `contract`, `architecture` e `plan` antes de construir.
3. Toda intenção deve ter sucesso verificável, escopo fora, decisões abertas e owner.
4. Toda task deve possuir caminho permitido, teste ou proof, dependência, risco e rollback.
5. Estampe hashes de upstream; qualquer alteração invalida downstream.
6. Use sandbox/worktree no build.
7. Execute verify, secure e benchmark quando o risco exigir; fases dispensadas devem ser `not_required` com justificativa.
8. Finalize em ship apenas com evidence bundle, deviations e unresolved explícitos.

## Execução econômica do runtime

`apiforge runtime run|resume|debate --profile economy|balanced|deep`: o perfil é preferência, o risco é piso (critical/irreversible ⇒ `deep`). Leia `economy.status`, `economy.stopped_at` e `economy.codes` no resultado: `unresolved` + `AF-BUDGET-EXHAUSTED` ou `AF-ECONOMY-CEILING` é parcial explícito — reexecute com perfil maior, nunca complete em silêncio. `L0` significa prova determinística sem chamada de agente; aceitação continua separada.

## Gates

Evidence unlocks phase gates. Flags, texto do agente e intenção não substituem evidência. Se uma prova não puder existir, registre override, motivo e ator.

## Entrega

Entregue artefatos SDD, plano atômico, ADRs, estado dos gates, provas, gaps e próximo passo.

## Field validation

Roadmap themes come from `apiforge field report` over pre-registered real tasks (`docs/field/README.md`). Nunca abra SDD de feature estrutural sem tema qualificado (≥5 tarefas verificadas em ≥2 repos) ou veredito `inconclusive` registrado. Baseline nunca usa `workspace graph --infer`; `AF-FIELD-FLAG-CONTAMINATION` recusa.
