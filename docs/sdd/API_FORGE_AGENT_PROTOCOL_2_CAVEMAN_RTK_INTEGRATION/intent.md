---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: intent
profile: standard
status: done
upstream:
  path: discover.md
  sha256: "0edaa86e193c964ad753e82581cf8fdea40fa5134dd14cde0c32dd5036b65f88"
problem: >
  Agentes recebem saídas ruidosas e não têm uma política nativa, verificável e
  multiplataforma para reduzi-las sem perder evidência crítica.
success:
  - compact-output-contract
  - critical-evidence-preserved
  - caveman-mode-vocabulary
  - cli-offline-compact
  - economy-measurable
out_of_scope:
  - executar comandos externos
  - instalar binários Caveman ou RTK
  - chamar AWS, bancos ou provedores de modelo
  - compactar código-fonte, contratos ou artefatos estruturados sem parser
owner: api-forge-runtime
---

# intent

Criar o primeiro slice do Agent Protocol 2.0: compactação determinística
compatível com o comportamento RTK/Caveman, preservando a autoridade dos
artefatos completos, do TaskSpec e do Verifier.
