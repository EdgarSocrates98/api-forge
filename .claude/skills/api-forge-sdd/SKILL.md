---
name: api-forge-sdd
description: Conduz mudanças de API pelo SDD do API Forge, da descoberta ao ship, com contratos, ADRs, tasks, gates, evidências, rollback e invalidação por hash. Use para iniciar uma feature, mudança de API, migração, banco, segurança, performance ou infraestrutura.
compatibility: Requer `docs/sdd`, os comandos `apiforge sdd` e o contrato em `docs/sdd-contract.md` quando disponíveis.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Procedimento

1. Escolha o perfil `quick`, `standard`, `critical` ou `migration` pela evidência de risco.
2. Preencha `discover`, `intent`, `contract`, `architecture` e `plan` antes de construir.
3. Toda intenção deve ter sucesso verificável, escopo fora, decisões abertas e owner.
4. Toda task deve possuir caminho permitido, teste ou proof, dependência, risco e rollback.
5. Estampe hashes de upstream; qualquer alteração invalida downstream.
6. Use sandbox/worktree no build.
7. Execute verify, secure e benchmark quando o risco exigir; fases dispensadas devem ser `not_required` com justificativa.
8. Finalize em ship apenas com evidence bundle, deviations e unresolved explícitos.

## Gates

Evidence unlocks phase gates. Flags, texto do agente e intenção não substituem evidência. Se uma prova não puder existir, registre override, motivo e ator.

## Entrega

Entregue artefatos SDD, plano atômico, ADRs, estado dos gates, provas, gaps e próximo passo.

