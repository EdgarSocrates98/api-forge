# MemoryEvalCaseResult-v1

§24 one memory-axis case verdict.

| Field | Meaning |
|---|---|
| `case_id`/`axis` | identity and one of the eight §24 axes |
| `expected`/`observed` | declared expectation vs observed contract summary |
| `passed` | all expectations held |
| `detail` | failing expectations |

Invariant: the axis vocabulary is closed — undeclared axes refuse the corpus.
