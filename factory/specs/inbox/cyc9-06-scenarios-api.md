---
id: cyc9-06
title: scenarios-api-engineering
status: inbox
created: 2026-10-15
owner: api-forge
scope: repo
cycle: 9
wave: 3
priority: p1
risk: medium
agent: codex
source: prompt_evo_cycles.md §9.3 API Engineering
verification:
  - python -m pytest
  - python -m ruff check src tests
  - apiforge sdd check --root docs/sdd
---

# Cenários Forge Lab — API Engineering

## Outcome

Biblioteca versionada de cenários do domínio de APIs com fixtures locais e ground truth: análise OpenAPI, contratos, detecção de breaking changes, testes, performance, evolução de API, diagnóstico de falhas.

## Grill gate

- Problema observado: capacidades do especialista sem cenários mensuráveis para provar precisão/cobertura.
- Usuário afetado: Benchmark Engineer e usuário avaliando o especialista.
- Falha concreta: claims de qualidade sem dataset verificável.
- Decisão: cenários do §9.3 API como fixtures (specs OpenAPI, pares de versões com/sem breaking change) + classificações esperadas, limitados às capacidades suportadas.
- Fora de escopo: serviços externos reais; centralizar motor no the-forge.
- Critério de parada: ao menos um cenário por categoria suportada, executável localmente e integrável ao harness federado.

## Acceptance

- Cenários versionados por categoria: OpenAPI, contratos, breaking changes, testes, performance, evolução, diagnóstico de falhas.
- Cada cenário: fixture + entrada + resultado esperado + classificação (ground truth).
- Execução local; saída compatível com contrato de métricas (cyc9-02).
- Categorias não suportadas → `not_available`, não simuladas.

## Constraints

- Independência: roda sem the-forge/CLI/Portal.

## Pending

- ⚠ Capacidades efetivamente implementadas (baseline cyc0-01); comandos de gate do repo a confirmar.
