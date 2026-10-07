---
sdd: 1
feature: API_FORGE_AGENT_PROTOCOL_2_CAVEMAN_RTK_INTEGRATION
phase: architecture
profile: standard
status: done
upstream:
  path: contract.md
  sha256: "52995a19bc8a9984ac7aae917f8beff82fbf4fe0f02a832a5cff1266c2e6a4ea"
files:
  - src/apiforge/agentops/compact.py
  - src/apiforge/agentops/__init__.py
  - src/apiforge/cli.py
  - tests/agentops/test_compact.py
decisions:
  - id: native-adapter
    decision: implementar protocolo local em vez de depender do runtime Caveman/RTK
    rollback: remover módulo agentops e comando context compact; manter detail_level atual
  - id: artifact-authority
    decision: compactação é projeção; o arquivo completo mantém autoridade
    rollback: desabilitar compactação por modo off sem alterar artefatos
  - id: critical-preservation
    decision: linhas com erro, falha, warning, bloqueio, recusa, códigos AF e status HTTP de erro são retidas
    rollback: elevar modo para off se a política não puder provar preservação
---

# architecture

O adaptador é puro e não executa comandos. Ele remove ruído de progresso,
limita linhas por modo e preserva todas as linhas críticas. A saída carrega o
hash do texto original, ponteiro para o artefato completo e uma afirmação
verificável de preservação crítica.

O supervisor, TaskSpec e Verifier permanecem acima desta camada. Nenhuma decisão
de `DONE`, autorização ou promoção depende somente da saída compactada.
