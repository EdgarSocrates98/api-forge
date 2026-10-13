# RouteTransitionReceipt/v1

§29-§31 canonical receipt for **every** route promote/demote attempt —
allowed or refused. `modes.jsonl` records *what changed*; the receipt records
*why*: which evidence, which policy gate, which approval.

| Field | Meaning |
|---|---|
| `route` / `candidate` | The `ControlPlaneRoute` being transitioned and its candidate identity |
| `mode` / `previous` | Target mode and the mode in effect before the attempt |
| `governing` | Who governs at the target mode — `candidate` only when the target is `active` |
| `evidence` | The `PromotionEvidence/v1` dump; `{}` on demotion (the safe direction needs none) |
| `policy` | `promotion:assisted`, `promotion:active` or `demotion` — the gate set applied |
| `approval` | `ApprovalGate` id when promotion to `active` required it |
| `fallback` | The route's declared `fallback_route` |
| `rollback` | `evidence.rollback_exists`; `true` on demotion (demotion is itself the rollback path) |
| `allowed` / `code` / `reason` | The verdict and the `AF-GOV-*` refusal when blocked |
| `recorded_at` | Transition timestamp |

Rows append to `.apiforge/control-plane/transitions.jsonl` — never rewritten.
Read back through `transition_receipts(root, route=None)`.

See `docs/decisions/API_FORGE_CONTROL_PLANE_MIGRATION_MAP.md` for the
canonical receipt stores across the decision plane.
