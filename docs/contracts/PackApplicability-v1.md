# PackApplicability-v1

§29 optional version/runtime applicability declared by a Knowledge Pack.

| Field | Meaning |
|---|---|
| `versions` | upstream versions the pack content applies to |
| `runtimes` | runtime/language versions the pack applies to |

Invariant: declared metadata only — an empty tuple means "no declared
applicability", never "applies to everything".
