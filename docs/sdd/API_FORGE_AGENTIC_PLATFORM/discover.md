---
sdd: 1
feature: API_FORGE_AGENTIC_PLATFORM
phase: discover
profile: critical
status: done
approaches:
  - id: single-spec
    summary: one spec covering the whole evolution prompt
    verdict: refused -- too large, unreviewable
  - id: per-layer-specs
    summary: spec per architecture layer (contracts, taskspec, graph, index, db, telemetry, autonomy, aws, packs)
    verdict: chosen -- each layer gets spec + plan + implementation
  - id: contracts-only
    summary: deliver only the SDD + contracts v1 as first cycle
    verdict: refused -- acceptance wants an e2e vertical slice
chosen: per-layer-specs
---

# discover -- audit of current state vs the evolution prompt

## Already delivered (do not reimplement)

| Prompt asks | Status |
|---|---|
| FastAPI, Spring Boot, Go/Chi adapters | delivered -- 3-way parity test |
| OpenAPI, AsyncAPI, GraphQL, protobuf/gRPC | delivered -- `model` readers |
| API Gateway, Lambda, Terraform, SAM | delivered -- `collect`/`model` |
| SDD phases, policy action classes, sandbox/worktree, evidence receipts | delivered |
| report build/sign/verify + Ed25519 keys | delivered |
| catalog (48 rules), routing.yaml, `next-step`, `detail_level` | delivered |
| MCP server, measured context funnel, economy ledger, transcript tokens, cost basis | delivered |
| coordinators/executors, playbook, dispatch runner, agent mirrors, debate | delivered |
| `run tool` allowlist (semgrep/trivy/gitleaks/k6), perf readers (jfr/pprof/pyroscope) | delivered |

## Gaps vs the prompt

| Layer | Missing |
|---|---|
| Canonical contracts | Fact/Finding/Receipt lack `version`; TaskSpec, OutcomeBrief, Decision, ActionPlan, Verification, AcceptanceRecord, CapabilityProof, GraphNode/Edge, TelemetryEvent, PerformanceRun, DataAccessIR, RuntimeMatrix absent |
| TaskSpec | states, recipes, budgets, seal, separate acceptance -- absent |
| OutcomeBrief | exists only as answer prose, not an artifact |
| Graphify | graph build/query/impact/trace/coverage/export -- absent |
| TokenSave | funnel exists; local indexes + sha256 cache -- absent |
| Databases | Redis/Valkey, Mongo/DocumentDB, DynamoDB, Neptune -- zero coverage |
| Telemetry | OTel ingest, compare_runs, noise floor, detect_regression, suggest_fix -- absent |
| Autonomy | modes (observe->continuous), runbooks -- absent (action classes exist) |
| Knowledge packs | 30 packs with source_authority/runtime-matrix/evals -- absent |
| AWS breadth | WAF, Cognito, IAM, CloudWatch, SQS/SNS/EventBridge, DynamoDB, ElastiCache, DocumentDB, Neptune -- only api-gateway + lambda exist |

## Verification of the inherited baseline

354 tests passing, 1 skipped (mcp extra absent), ruff/mypy clean,
`check_release.py` PASS at commit `8ba775a`.
