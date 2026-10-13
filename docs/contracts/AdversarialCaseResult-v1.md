# AdversarialCaseResult-v1

§25 one synthesized attack against one defense surface.

| Field | Meaning |
|---|---|
| `case_id`/`attack_class` | case identity and §25 class |
| `defense` | the exercised surface |
| `expected`/`observed` | `refused`/`contained`/`escaped` |
| `code` | the AF code the defense emitted |
| `passed` | expected == observed (+ code match when declared) |
| `detail` | observed reason |

Invariant: `escaped` means the defense failed — the case fails loudly.
