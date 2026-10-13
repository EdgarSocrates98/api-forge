# SecurityAdversarialReport-v1

§25 the adversarial corpus verdict — local, no external calls.

| Field | Meaning |
|---|---|
| `cases` | per-case `AdversarialCaseResult` |
| `totals` | counts by verdict plus passed |
| `unresolved` | cases that could not run |

Invariant: every attack ran against the real defense module, not a mock.
