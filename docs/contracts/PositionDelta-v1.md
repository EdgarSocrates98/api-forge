# PositionDelta/v1

`PositionDelta/v1` is a debate position as a contract, not prose.

| Field | Meaning |
|---|---|
| `side` / `position` | Side and a one-line position |
| `evidence` | `fact:` ids cited (required by `debate submit`) |
| `disagreements` | `{point, reason}` rows (`--disagree point=reason`) |
| `risks` | Risks the side accepts or flags |
| `confidence` | Optional 0.0-1.0 |
