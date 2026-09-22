---
name: api-forge-core
description: Governa qualquer tarefa substantiva de engenharia de API no API Forge. Use quando o usuário pedir análise, planejamento, arquitetura, implementação, revisão, testes, segurança, performance, AWS, bancos, modernização ou operação de APIs; comece pelo caso persistido, evidência e roteamento determinístico.
compatibility: Funciona como skill de projeto em Codex, Claude Code, Devin e GitHub Copilot. Não exige LLM, rede ou ferramenta específica.
metadata:
  api-forge-skill: "true"
  version: "1.0"
---

## Propósito

Trate o API Forge como `deterministic-core + agentic orchestration`. O agente coordena e explica; o core extrai, mede, julga e verifica.

## Protocolo

1. Preserve alterações existentes e leia `AGENT_PROTOCOL.md`.
2. Abra ou crie o caso em `.apiforge/case/` antes de investigar.
3. Execute `apiforge next-step` antes de escolher especialista, quando houver findings.
4. Prefira facts, regras e ferramentas locais a memória do modelo.
5. Não faça afirmações quantitativas sem `fact_id`, fonte e unidade.
6. Preserve `confirmed`, `unresolved`, `refused`, `not_observed` e `inconclusive` separadamente.
7. Faça alterações somente em sandbox, branch ou worktree.
8. Registre ferramenta, versão, comando, resultado, artefato e hash.
9. Escale decisões sensíveis, cloud mutations e ações destrutivas para aprovação.
10. Entregue um handoff com estado, resultado, prova, gaps e próximo passo.

## Roteamento

Escolha a skill mais específica depois do protocolo:

- descoberta e API-IR → `api-forge-discovery`;
- contrato e compatibilidade → `api-forge-contract`;
- arquitetura e escolha de plataforma → `api-forge-architecture`;
- bancos e persistência → `api-forge-data-access`;
- testes, segurança e resiliência → `api-forge-verification`;
- carga, TPS e capacidade → `api-forge-performance`;
- observabilidade e operação → `api-forge-observability`;
- contexto, grafo e handoff → `api-forge-context`;
- SDD e decomposição → `api-forge-sdd`.

## Saída

Use esta estrutura quando o trabalho for substantivo:

```text
Status:
Outcome:
Human action:
Proof:
Gaps:
Next:
Open:
```

