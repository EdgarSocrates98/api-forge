# DEFINE: API Forge Economy — Freshness Watch, Live Gating, Progressive Verification and Resume Checkpoint (Onda 8)

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | API_FORGE_ECONOMY_FRESHNESS_RESUME |
| **Date** | 2026-09-28 |
| **Author** | define-agent |
| **Status** | ✅ Shipped |
| **Clarity Score** | 14/15 |
| **Source** | [BRAINSTORM](./BRAINSTORM_API_FORGE_ECONOMY_FRESHNESS_RESUME.md) |

---

## Problem Statement

Four economy gaps remain: stale knowledge is only detected pack by pack with a
hand-supplied receipt; nothing stops an agent from paying for live evidence
when a local artifact already answers; an inconclusive test has no declared
next step; and a resumed run re-resolves its profile without the budget it
already spent, with no per-SDD-phase allocation.

## Users

| User | Pain |
|---|---|
| Agent host (Claude/Codex/Devin) | Needs a cheap decision before calling live tools |
| Maintainer | Needs one list of packs that need refresh |
| Release guardian | Needs resumed runs to respect the original envelope |

## Goals

| Priority | Goal |
|---|---|
| MUST | `knowledge watch` lists `refresh_needed` packs from a local upstream manifest |
| MUST | `evidence gate` allows `live_read_only` only for runtime questions; refuses `live_mutation` |
| MUST | `verify escalate` implements static → test → stop / live_read_only → unresolved |
| MUST | resume pins the checkpoint profile and carries spent calls; writes `economy_checkpoint.json` |
| MUST | `economy phase-budget` splits the envelope over SDD phases; verify/secure protected |
| SHOULD | CLI/MCP parity, eval corpus, contract docs, catalog codes |

## Success Criteria

- Watch: fingerprint mismatch, version mismatch, expiry, window → `refresh_needed`; matching → `fresh`; no metadata → `unknown`; no manifest entry → `unresolved`.
- Gate: 100% of static questions in the corpus denied live; 100% runtime questions allowed `live_read_only` only.
- Escalate: every transition in the corpus matches the declared table; no step above `live_read_only`.
- Resume: a resumed run never uses more than `max_calls − calls_used` and never a lower profile than the checkpoint.
- Phase budget: shares sum to 1.0; protected phases never marked `cut`.

## Acceptance Tests

| ID | Scenario | Expected |
|---|---|---|
| AT-001 | pack fingerprint ≠ manifest | `refresh_needed`, reason names fingerprint |
| AT-002 | pack `expires_at` < now | `refresh_needed`, reason expiry |
| AT-003 | question "o campo foi removido?" | `live_allowed=false`, mode `static` |
| AT-004 | question "isso causou erros em produção?" | mode `live_read_only`, receipt required |
| AT-005 | `--mode live_mutation` | refusal `AF-EVIDENCE-MUTATION-REFUSED` with field/unlock |
| AT-006 | static likely + test confirms | action `stop` |
| AT-007 | test inconclusive | next `live_read_only` |
| AT-008 | runtime inconclusive | `unresolved`, never mutation |
| AT-009 | resume with lower `--profile` | effective = checkpoint profile, diagnostic `AF-ECONOMY-RESUME-PINNED` |
| AT-010 | phase usage over budget on build | `AF-BUDGET-PHASE-EXCEEDED`; on verify → `protected_overrun` |

## Out of Scope

Fetching upstream sources, executing live adapters, scheduling watches,
changing SDD gate semantics.

## Constraints

Offline, deterministic, no provider SDK in `src/`, every refusal carries
`AF-*` + `field` + `unlock` and is cataloged.

## Next Step

`/design .claude/sdd/features/DEFINE_API_FORGE_ECONOMY_FRESHNESS_RESUME.md`
