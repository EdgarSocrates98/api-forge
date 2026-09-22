---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: discover
profile: standard
status: done
approaches:
  - id: vendor-copy
    summary: copiar Caveman e RTK integralmente para o núcleo
    verdict: refused -- cria dependência de host e duplica o deterministic-core
  - id: adapters-native
    summary: adaptar comportamentos por contratos locais, com fallback offline
    verdict: chosen -- preserva portabilidade e governança do API Forge
  - id: prompt-only
    summary: documentar regras sem código nem métricas
    verdict: refused -- não permite verificar economia ou perda de evidência
chosen: adapters-native
---

# discover

O Spark Forge possui Caveman vendorizado, filtros RTK, workflows de investigação,
compressão e economia observável. O API Forge já possui `detail_level`, context
funnel, cache por SHA-256, Graphify, TaskSpec e ledger de bytes, mas não possui
um contrato comum para compactar saídas de ferramentas nem modos Caveman nativos.

## Constraints

- local e CI first;
- nenhum provider de modelo ou rede no núcleo;
- saída compacta nunca substitui o artefato completo;
- erros, códigos AF, falhas, warnings e evidências críticas são preservados;
- comandos não são executados pelo compactador;
- transformação determinística e auditável por SHA-256.

## Initial slice

Adicionar `apiforge.agentops.compact`, modos Caveman interoperáveis e
`apiforge context compact` para artefatos UTF-8. Workflows especializados e
adapters de host ficam para as próximas tasks.
