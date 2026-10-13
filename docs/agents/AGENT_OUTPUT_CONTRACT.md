# Agent Output Contract

Agents propose; the deterministic supervisor decides. Every specialist output
is persisted as `AgentArtifact/v1` and must contain:

- a recommendation;
- evidence references to facts, receipts or declared sources;
- assumptions separated from observations;
- risks and unresolved gaps;
- a verifier that can independently test the recommendation;
- bounded confidence when confidence is meaningful.

An agent cannot widen a `TaskSpec`, invoke a tool outside the policy allowlist,
approve its own output or promote a recommendation to `DONE`. Missing evidence
must remain unresolved. The supervisor may request another specialist, open a
debate room or require human supervision.

Good recommendations explain why a technique or architecture fits the stated
need, list alternatives and trade-offs, and identify what would change the
decision. They never invent versions, cost, throughput, permissions, indexes,
lag or provider guarantees.

## Minimum recommendation shape

```yaml
recommendation: "..."
facts:
  - fact_id: "fact:..."
    observation: "..."
assumptions:
  - "..."
alternatives:
  - option: "..."
    tradeoffs: ["..."]
risks: ["..."]
unresolved: ["..."]
evidence_refs: ["receipt:...", "fact:..."]
verifier: "tests/... or an explicit read-only check"
confidence: 0.0
```

No change-control, os campos acima são obrigatórios no contrato
`Recommendation/v1`. A recomendação deve transformar a necessidade observada
em uma decisão técnica verificável: boas práticas, técnica ou arquitetura,
alternativas e trade-offs. O agent não deve preencher lacunas com memória de
provider; deve marcar `unresolved` e apontar o próximo verificador.

`confidence` é limitado a `0..1` e não compensa evidência ausente. Uma
recomendação pode ser útil e ainda terminar em `REVIEW`, `DECIDE` ou `BLOCKED`;
esses estados não podem ser reescritos como `DONE`.

## Architectural guidance

Agents devem primeiro reformular a necessidade e as restrições, depois
recomendar uma técnica ou arquitetura com alternativas e trade-offs. Devem
preferir a menor mudança verificável, identificar a evidência necessária para
mover de `heuristic`/`unresolved` para `supported` e nomear rollback antes de
qualquer ação externa. Consulte o [guia de uso da plataforma](../guides/API_FORGE_PLATFORM_USAGE.md)
para as seis verticais e a fronteira de comandos públicos.
