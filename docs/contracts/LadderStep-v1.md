# LadderStep/v1

`LadderStep/v1` records one escalation level reached during a runtime run; the
ordered list is returned as `economy.ladder`.

| Field | Meaning |
|---|---|
| `level` | `L0` deterministic proof · `L1` partial deterministic evidence · `L2` primary + risk-required roles · `L3` escalation review · `L4` debate room · `L5` human gate |
| `action` | What the supervisor did at this level |
| `trigger` | Deterministic reason (`start`, `low_confidence`, `unresolved`, `conflict`, debate/gate reasons, proof refs) |
| `calls` | Agent calls spent at this level |
