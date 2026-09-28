# RefereePacket/v1

`RefereePacket/v1` is the referee input from `debate packet`.

| Field | Meaning |
|---|---|
| `debate_id` / `question` | The debate |
| `capsule_id` | Shared `ctx://` capsule, read once by id |
| `positions` | Latest `PositionDelta/v1` per side |
| `disagreements` | Union of disagreement points |
| `evidence` | Union of every cited id across all submissions — never dropped |
| `packet_bytes` / `naive_bytes` | Capsule content once plus this packet, versus capsule content and all submissions shipped to every side and the referee |
