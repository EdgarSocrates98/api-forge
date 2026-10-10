# `apiforge` command reference

Generated from the real CLI parser by `doc_inventory.py` + `doc_reference.py`. Do not hand-edit generated sections — write between `keep:start`/`keep:end` markers. Status vocabulary: `available` unless marked otherwise.

## Groups

- [`agentops`](#agentops) — 17 command(s)
- [`agents`](#agents) — 6 command(s)
- [`analyze`](#analyze) — 1 command(s)
- [`autonomy`](#autonomy) — 7 command(s)
- [`blackboard`](#blackboard) — 3 command(s)
- [`brief`](#brief) — 2 command(s)
- [`build`](#build) — 2 command(s)
- [`cache`](#cache) — 3 command(s)
- [`capabilities`](#capabilities) — 3 command(s)
- [`change-control`](#change-control) — 7 command(s)
- [`collect`](#collect) — 27 command(s)
- [`context`](#context) — 9 command(s)
- [`contract`](#contract) — 3 command(s)
- [`contract-intel`](#contract-intel) — 3 command(s)
- [`control`](#control) — 7 command(s)
- [`debate`](#debate) — 5 command(s)
- [`devin`](#devin) — 4 command(s)
- [`diff`](#diff) — 2 command(s)
- [`discover`](#discover) — 1 command(s)
- [`dispatch`](#dispatch) — 2 command(s)
- [`distribution`](#distribution) — 5 command(s)
- [`doctor`](#doctor) — 1 command(s)
- [`economy`](#economy) — 17 command(s)
- [`evals`](#evals) — 33 command(s)
- [`evidence`](#evidence) — 5 command(s)
- [`evolve`](#evolve) — 1 command(s)
- [`experience`](#experience) — 4 command(s)
- [`field`](#field) — 6 command(s)
- [`forge`](#forge) — 9 command(s)
- [`governance`](#governance) — 2 command(s)
- [`governor`](#governor) — 6 command(s)
- [`graph`](#graph) — 9 command(s)
- [`grpc`](#grpc) — 10 command(s)
- [`index`](#index) — 3 command(s)
- [`init`](#init) — 1 command(s)
- [`inspect`](#inspect) — 1 command(s)
- [`install`](#install) — 7 command(s)
- [`integration`](#integration) — 5 command(s)
- [`judge`](#judge) — 1 command(s)
- [`knowledge`](#knowledge) — 12 command(s)
- [`lab`](#lab) — 2 command(s)
- [`mcp`](#mcp) — 5 command(s)
- [`memory`](#memory) — 8 command(s)
- [`migration`](#migration) — 5 command(s)
- [`model`](#model) — 73 command(s)
- [`next-step`](#next-step) — 1 command(s)
- [`observability`](#observability) — 7 command(s)
- [`perf`](#perf) — 10 command(s)
- [`plan`](#plan) — 3 command(s)
- [`platform`](#platform) — 2 command(s)
- [`playbook`](#playbook) — 1 command(s)
- [`policy`](#policy) — 2 command(s)
- [`report`](#report) — 5 command(s)
- [`resume`](#resume) — 1 command(s)
- [`review`](#review) — 1 command(s)
- [`route`](#route) — 4 command(s)
- [`rules`](#rules) — 3 command(s)
- [`run`](#run) — 3 command(s)
- [`runtime`](#runtime) — 20 command(s)
- [`sandbox`](#sandbox) — 3 command(s)
- [`sdd`](#sdd) — 7 command(s)
- [`slice`](#slice) — 3 command(s)
- [`status`](#status) — 1 command(s)
- [`task`](#task) — 12 command(s)
- [`tui`](#tui) — 1 command(s)
- [`verify`](#verify) — 3 command(s)
- [`workspace`](#workspace) — 7 command(s)

## agentops

### `agentops`

Host-neutral Caveman/RTK protocols, workflows and adapters.

**Syntax**

```text
apiforge agentops
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops activation-plan`

Build a host activation plan; no host configuration is mutated.

**Syntax**

```text
apiforge agentops activation-plan <host> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `host` | yes | — | claude, gpt-codex, devin or copilot. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops compare`

§55 deterministic a/b over quality/tokens/cost/latency/context/evidence/tools/agents.

**Syntax**

```text
apiforge agentops compare <run_a> <run_b> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_a` | yes | — | Baseline run id. |
| `run_b` | yes | — | Candidate run id. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops filters`

List closed command filters used by the RTK adapter.

**Syntax**

```text
apiforge agentops filters [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops hosts`

List host adapters for Claude, GPT/Codex, Devin and Copilot.

**Syntax**

```text
apiforge agentops hosts [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops inspect`

§53–§54 sectioned report for one run; sections never drop silently.

**Syntax**

```text
apiforge agentops inspect <run_id> [risk] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | Run id present in the local ledgers. |
| `risk` | no | — | Declared run risk (micro/low/medium/high). |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops native`

Inspect repository-native Caveman/Cavekit assets and RTK configuration.

**Syntax**

```text
apiforge agentops native [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops negotiate`

Resolve a capability intersection from local host declarations.

**Syntax**

```text
apiforge agentops negotiate <capability> [host] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `capability` | yes | — | — |
| `host` | no | — | Limit to one or more declared hosts. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops parity`

Audit host discovery and capability parity without invoking a host.

**Syntax**

```text
apiforge agentops parity [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops projection`

Declared economical projection for a host, with measured surface bytes.

**Syntax**

```text
apiforge agentops projection <host> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `host` | yes | — | claude|gpt-codex|devin|copilot. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops prompt`

Stable prompt prefix (hashed) and the run-specific suffix.

**Syntax**

```text
apiforge agentops prompt <capability> [task] [expertise] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `capability` | yes | — | — |
| `task` | no | — | — |
| `expertise` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops timeline`

Render ordered ledger/span/token events with missing-order evidence.

**Syntax**

```text
apiforge agentops timeline <run_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | Run id present in the local ledgers. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops tool`

Inspect one Tool Adapter contract.

**Syntax**

```text
apiforge agentops tool <name> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `name` | yes | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops tools`

List typed Tool Adapters and their safety/evidence metadata.

**Syntax**

```text
apiforge agentops tools [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops waste`

§56–§57 waste detector; every finding labeled observed/estimated/hypothesis.

**Syntax**

```text
apiforge agentops waste <run_id> [risk] [policy] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | Run id present in the local ledgers. |
| `risk` | no | — | Declared run risk (micro/low/medium/high). |
| `policy` | no | — | rules/agentops_waste.yaml override. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops workflow`

Render one workflow plan; execution remains governed by TaskSpec.

**Syntax**

```text
apiforge agentops workflow <name> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `name` | yes | — | Workflow name. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops workflows`

List deterministic Caveman-inspired API workflows.

**Syntax**

```text
apiforge agentops workflows [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## agents

### `agents`

Publish coordinator profiles to host-native mirrors.

**Syntax**

```text
apiforge agents
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agents audit`

Anti-agentic-theater gate: unique capability/expertise/validator/tool/decision role.

**Syntax**

```text
apiforge agents audit [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Repository root. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agents check`

Report render drift for all three hosts — the release gate fails on the same check.

**Syntax**

```text
apiforge agents check [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Repository root. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agents lint`

Agent contract lint: sections, word budget, English, description, access, owned tools.

**Syntax**

```text
apiforge agents lint [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Repository root. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agents references`

Every agent name in rules/code/tests/evals is a coordinator or an active alias.

**Syntax**

```text
apiforge agents references [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Repository root. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agents sync`

Render `.agents/agents/`, `.claude/agents/` and `.codex/agents/` from `agents/*.md`.

**Syntax**

```text
apiforge agents sync [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Repository root. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## analyze

### `analyze`

Run the full deterministic slice and persist a case.

**Syntax**

```text
apiforge analyze <contract> <project> [baseline] [out_dir] [fail_on] [framework] [upstream] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `contract` | yes | — | OpenAPI 3.1 document. |
| `project` | yes | — | FastAPI project root. |
| `baseline` | no | — | Baseline OpenAPI document to diff against. |
| `out_dir` | no | — | Case output directory. |
| `fail_on` | no | — | Exit 4 on confirmed findings at this severity or worse. |
| `framework` | no | — | fastapi|spring|go|auto (detected from files). |
| `upstream` | no | — | Bounded foreign facts (apiforge/upstream-facts/v1) persisted with the case under their original provenance; never judged as local evidence. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## autonomy

### `autonomy`

Autonomy modes (observe->continuous) and runbooks on the policy engine.

**Syntax**

```text
apiforge autonomy
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy heal`

Self-healing pipeline: detect->explain->propose->authorize->execute->
verify->compare->accept|rollback. Every transition is policy-decided and
ledgered; rollback restores the snapshot of --writable-path files.

**Syntax**

```text
apiforge autonomy heal [root] [findings] [action_class] [writable_path] [project] [contract] [baseline] [candidate] [input_path] [case] [now] [actor] [detail] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `findings` | no | — | — |
| `action_class` | no | — | Declared autonomy class for the execute transition. |
| `writable_path` | no | — | Path the pipeline may snapshot/restore. |
| `project` | no | — | — |
| `contract` | no | — | — |
| `baseline` | no | — | — |
| `candidate` | no | — | — |
| `input_path` | no | — | — |
| `case` | no | — | — |
| `now` | no | — | — |
| `actor` | no | — | — |
| `detail` | no | — | — |
| `policy` | no | — | — |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy ledger`

Read the append-only autonomy ledger.

**Syntax**

```text
apiforge autonomy ledger [root] [tail] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `tail` | no | — | Last N entries; 0 = all. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy run`

Evaluate one action under the current mode; execute only on allow.

**Syntax**

```text
apiforge autonomy run <verb> [action_class] [args] [target] [detail] [root] [project] [contract] [baseline] [candidate] [input_path] [findings] [case] [now] [actor] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `verb` | yes | — | Dispatchable verb. |
| `action_class` | no | — | Declared autonomy class. |
| `args` | no | — | — |
| `target` | no | — | — |
| `detail` | no | — | key=value pairs. |
| `root` | no | — | — |
| `project` | no | — | — |
| `contract` | no | — | — |
| `baseline` | no | — | — |
| `candidate` | no | — | — |
| `input_path` | no | — | — |
| `findings` | no | — | — |
| `case` | no | — | — |
| `now` | no | — | — |
| `actor` | no | — | — |
| `policy` | no | — | — |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy runbook`

Run a runbook under the current mode — halting is mode-defined.

**Syntax**

```text
apiforge autonomy runbook <name> [root] [project] [contract] [baseline] [candidate] [input_path] [findings] [case] [now] [actor] [detail] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `name` | yes | — | Runbook in rules/runbooks.yaml. |
| `root` | no | — | — |
| `project` | no | — | — |
| `contract` | no | — | — |
| `baseline` | no | — | — |
| `candidate` | no | — | — |
| `input_path` | no | — | — |
| `findings` | no | — | — |
| `case` | no | — | — |
| `now` | no | — | — |
| `actor` | no | — | — |
| `detail` | no | — | — |
| `policy` | no | — | — |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy set`

Change the autonomy mode — itself a policy-gated action.

**Syntax**

```text
apiforge autonomy set <mode> <by> [root] [now] [reason] [detail] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `mode` | yes | — | observe|supervised|continuous. |
| `by` | yes | — | Actor making the change. |
| `root` | no | — | Workspace root. |
| `now` | no | — | Explicit timestamp; the only clock source. |
| `reason` | no | — | — |
| `detail` | no | — | Gate satisfaction as key=value (e.g. approval=op). |
| `policy` | no | — | — |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy status`

Current mode, who set it, and the ledger size.

**Syntax**

```text
apiforge autonomy status [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Workspace root. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## blackboard

### `blackboard`

Structured append-only shared state.

**Syntax**

```text
apiforge blackboard
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `blackboard append`

**Syntax**

```text
apiforge blackboard append <task_id> <scope> <kind> <origin> <payload> <now> [trust_level] [taint] [provenance] [evidence] [supersedes] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `scope` | yes | — | — |
| `kind` | yes | — | — |
| `origin` | yes | — | — |
| `payload` | yes | — | JSON value or JSON file. |
| `now` | yes | — | — |
| `trust_level` | no | — | — |
| `taint` | no | — | — |
| `provenance` | no | — | — |
| `evidence` | no | — | — |
| `supersedes` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `blackboard query`

**Syntax**

```text
apiforge blackboard query <task_id> [kind] [scope] [term] [max_results] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `kind` | no | — | — |
| `scope` | no | — | — |
| `term` | no | — | — |
| `max_results` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## brief

### `brief`

Outcome Briefs — DONE is refused while mandatory gaps exist.

**Syntax**

```text
apiforge brief
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `brief show`

Render the Outcome Brief for a task — DONE is refused, not advised.

**Syntax**

```text
apiforge brief show <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | Task id to brief. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## build

### `build`

Generate code skeletons — evaluated in the sandbox, promoted via worktree only.

**Syntax**

```text
apiforge build
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `build endpoint`

Synthesize a Spring endpoint skeleton; main tree is never touched.

**Syntax**

```text
apiforge build endpoint <contract> <operation_id> <project> [write_diff] [into_worktree] [approve] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `contract` | yes | — | OpenAPI 3.1 document. |
| `operation_id` | yes | — | operationId to build. |
| `project` | yes | — | Java project root. |
| `write_diff` | no | — | Also write the emitted unified diff to a file. |
| `into_worktree` | no | — | Promote generated files into this git worktree. |
| `approve` | no | — | Record approval evidence for the sensitive-class gate. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## cache

### `cache`

Advisory layered cache — reuse only fresh evidence, invalidate by dependency.

**Syntax**

```text
apiforge cache
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `cache invalidate`

Drop only the capsule selections whose dependencies intersect the change set.

**Syntax**

```text
apiforge cache invalidate [changed] [base] [head] [root] [case_dir] [cache_home] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `changed` | no | — | Changed file (repeatable). |
| `base` | no | — | — |
| `head` | no | — | — |
| `root` | no | — | — |
| `case_dir` | no | — | — |
| `cache_home` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `cache stats`

Entries, bytes, expired and corrupt counts per layer and tier, plus policies.

**Syntax**

```text
apiforge cache stats [root] [cache_home] [layer] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `cache_home` | no | — | Shared cache tier. |
| `layer` | no | — | Check one layer's policy. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## capabilities

### `capabilities`

Inspect the evidence-backed public capability matrix.

**Syntax**

```text
apiforge capabilities
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `capabilities list`

List public capabilities and their explicit support boundaries.

**Syntax**

```text
apiforge capabilities list [capability_id] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `capability_id` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `capabilities verify`

Verify documentation, limitations and evidence requirements.

**Syntax**

```text
apiforge capabilities verify [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## change-control

### `change-control`

Govern API, Git and CI/CD changes with read-only evidence.

**Syntax**

```text
apiforge change-control
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control collect`

Collect GitHub context with a GET-only adapter into a replay bundle.

**Syntax**

```text
apiforge change-control collect <repository> <base_sha> <head_sha> [out_bundle] [pull_number] [contract] [baseline] [project] [api_base] [origin] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `repository` | yes | — | GitHub owner/repository. |
| `base_sha` | yes | — | 40-character base commit SHA. |
| `head_sha` | yes | — | 40-character head commit SHA. |
| `out_bundle` | no | — | Sanitized bundle output path. |
| `pull_number` | no | — | — |
| `contract` | no | — | — |
| `baseline` | no | — | — |
| `project` | no | — | — |
| `api_base` | no | — | — |
| `origin` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control publish`

Publish the canonical result to JUnit, Markdown, SARIF and HTML.

**Syntax**

```text
apiforge change-control publish <run_dir> [junit] [markdown] [sarif] [html] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_dir` | yes | — | Output directory from change-control run. |
| `junit` | no | — | JUnit XML output path. |
| `markdown` | no | — | Markdown report output path. |
| `sarif` | no | — | SARIF JSON output path. |
| `html` | no | — | Standalone HTML output path. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control run`

Run analyze -> next-step -> graph -> evidence -> brief from a bundle.

**Syntax**

```text
apiforge change-control run <bundle> [out_dir] [framework] [phase] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `bundle` | yes | — | Provider-neutral af-change-bundle/1 JSON. |
| `out_dir` | no | — | Governed output directory. |
| `framework` | no | — | fastapi|spring|go|auto (detected from files). |
| `phase` | no | — | Canonical SDD phase for routing. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control serve`

Serve a local or authenticated TLS read-only UI and IDE bridge.

**Syntax**

```text
apiforge change-control serve <run_dir> [host] [port] [token_env] [tls_cert] [tls_key] [trust_proxy]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_dir` | yes | — | Output directory from change-control run. |
| `host` | no | — | — |
| `port` | no | — | — |
| `token_env` | no | — | — |
| `tls_cert` | no | — | — |
| `tls_key` | no | — | — |
| `trust_proxy` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control surface`

Export a canonical IDE/UI projection without changing its semantics.

**Syntax**

```text
apiforge change-control surface <run_dir> [surface] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_dir` | yes | — | Output directory from change-control run. |
| `surface` | no | — | — |
| `out` | no | — | Optional projection JSON path. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control verify`

Verify that a change-control result still references existing artifacts.

**Syntax**

```text
apiforge change-control verify <run_dir> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_dir` | yes | — | Output directory from change-control run. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## collect

### `collect`

Collect AWS artifacts into offline dumps (the only family that touches AWS).

**Syntax**

```text
apiforge collect
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect alb`

**Syntax**

```text
apiforge collect alb <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | Load balancer ARN. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect api-gateway`

Fetch one REST API's configuration into an offline dump.

**Syntax**

```text
apiforge collect api-gateway <api_id> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `api_id` | yes | — | REST API id. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect cloudwatch`

**Syntax**

```text
apiforge collect cloudwatch <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | Alarm name prefix. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect cognito`

Fetch the user pool and its app clients into an offline dump.

**Syntax**

```text
apiforge collect cognito <user_pool_id> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `user_pool_id` | yes | — | User pool id. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect docdb`

**Syntax**

```text
apiforge collect docdb <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | DocDB cluster identifier. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect dynamodb`

**Syntax**

```text
apiforge collect dynamodb <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | DynamoDB table name. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect ec2`

**Syntax**

```text
apiforge collect ec2 <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | EC2 instance id — posture only, never user-data. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect ecs`

**Syntax**

```text
apiforge collect ecs <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | ECS cluster name — collects every service in it. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect eks`

**Syntax**

```text
apiforge collect eks <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | EKS cluster name. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect elasticache`

**Syntax**

```text
apiforge collect elasticache <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | ElastiCache replication group id. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect eventbridge`

Fetch the bus, its rules and their targets into an offline dump.

**Syntax**

```text
apiforge collect eventbridge <bus_name> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `bus_name` | yes | — | Event bus name. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect iam-role`

Fetch one role, its attached policies and inline policy documents.

**Syntax**

```text
apiforge collect iam-role <role_name> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `role_name` | yes | — | IAM role name. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect kms`

**Syntax**

```text
apiforge collect kms <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | KMS key id or ARN. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect lambda`

Fetch one Lambda function's configuration into an offline dump.

**Syntax**

```text
apiforge collect lambda <function_name> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `function_name` | yes | — | Lambda function name. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect msk`

**Syntax**

```text
apiforge collect msk <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | MSK cluster ARN. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect neptune`

**Syntax**

```text
apiforge collect neptune <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | Neptune cluster identifier. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect neptune-explain`

Read-only explain/profile over the neptunedata allowlist; receipt in manifest.

**Syntax**

```text
apiforge collect neptune-explain <endpoint> <language> <out_dir> [query] [query_file] [profile] [reader_endpoint] [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `endpoint` | yes | — | Neptune endpoint URL (https://host:8182). |
| `language` | yes | — | gremlin|opencypher (sparql: dump only). |
| `out_dir` | yes | — | Dump directory to write. |
| `query` | no | — | Literal query text. |
| `query_file` | no | — | File holding the query. |
| `profile` | no | — | Executing plan (profile/dynamic); needs --reader-endpoint. |
| `reader_endpoint` | no | — | Declared reader; must equal --endpoint for --profile. |
| `now` | no | — | Explicit ISO8601 collection timestamp. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect rds`

**Syntax**

```text
apiforge collect rds <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | RDS instance or Aurora cluster identifier. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect s3`

**Syntax**

```text
apiforge collect s3 <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | S3 bucket name — posture only, never objects. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect secrets`

**Syntax**

```text
apiforge collect secrets <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | Secret name or ARN — metadata only, value never read. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect sns`

Fetch one topic's attributes and subscriptions into an offline dump.

**Syntax**

```text
apiforge collect sns <topic_arn> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `topic_arn` | yes | — | SNS topic ARN. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect sqs`

Fetch one queue's attribute set into an offline dump.

**Syntax**

```text
apiforge collect sqs <queue_url> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `queue_url` | yes | — | SQS queue URL. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect stepfunctions`

**Syntax**

```text
apiforge collect stepfunctions <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | State machine ARN. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect vpc-endpoints`

**Syntax**

```text
apiforge collect vpc-endpoints <identifier> <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `identifier` | yes | — | VPC id. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect waf`

Fetch one WebACL's configuration into an offline dump.

**Syntax**

```text
apiforge collect waf <web_acl_id> <web_acl_name> [scope] <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `web_acl_id` | yes | — | WebACL id. |
| `web_acl_name` | yes | — | WebACL name. |
| `scope` | no | — | REGIONAL or CLOUDFRONT. |
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect xray`

Fetch X-Ray sampling rules and encryption config.

**Syntax**

```text
apiforge collect xray <out_dir> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `out_dir` | yes | — | Dump directory to write. |
| `now` | no | — | Explicit ISO8601 collection timestamp (the only clock). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## context

### `context`

Measured context accounting — the funnel, in bytes per stage.

**Syntax**

```text
apiforge context
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context capsule`

Minimal sufficient evidence for one operation as ctx:// refs under a byte budget.

**Syntax**

```text
apiforge context capsule <target> [root] [case_dir] [budget_bytes] [level] [impact] [action] [objective] [run_id] [no_cache] [cache_home] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `target` | yes | — | Operation, e.g. 'POST /orders'. |
| `root` | no | — | — |
| `case_dir` | no | — | Default <root>/.apiforge/case. |
| `budget_bytes` | no | — | — |
| `level` | no | — | Max expansion level L0-L4. |
| `impact` | no | — | direct|transitive|all. |
| `action` | no | — | — |
| `objective` | no | — | — |
| `run_id` | no | — | — |
| `no_cache` | no | — | Skip L3/L4 cache lookups. |
| `cache_home` | no | — | Shared cache tier. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context compact`

Compact a command artifact while preserving critical evidence.

**Syntax**

```text
apiforge context compact <input_path> [command] [mode] [max_lines] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `input_path` | yes | — | UTF-8 command output artifact. |
| `command` | no | — | Logical command name. |
| `mode` | no | — | Caveman mode: off|lite|full|ultra|wenyan. |
| `max_lines` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context delta`

What changed, which operations it impacts and which capsules to build — delta first.

**Syntax**

```text
apiforge context delta [base] [head] [changed] [root] [case_dir] [invalidate] [cache_home] [limit] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `base` | no | — | Base ref (read-only git diff). |
| `head` | no | — | Head ref; default worktree. |
| `changed` | no | — | Changed file (repeatable). |
| `root` | no | — | — |
| `case_dir` | no | — | — |
| `invalidate` | no | — | Drop affected selections. |
| `cache_home` | no | — | — |
| `limit` | no | — | Bound each carried collection; counts stay truthful. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context expand`

Return one ctx object after verifying its sha256.

**Syntax**

```text
apiforge context expand <uri> [root] [run_id] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `uri` | yes | — | ctx://sha256/<hex> emitted by `context capsule`. |
| `root` | no | — | — |
| `run_id` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context funnel`

Measure what each case stage keeps — bytes, never claims.

**Syntax**

```text
apiforge context funnel <case_dir> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case_dir` | yes | — | Persisted case directory (api-ir/facts/findings). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context gc`

Expired/corrupt cache entries, orphan cache objects and unreferenced ctx objects.

**Syntax**

```text
apiforge context gc [root] [apply] [cache_home] [limit] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `apply` | no | — | Delete; default only reports. |
| `cache_home` | no | — | — |
| `limit` | no | — | Bound each carried collection; counts stay truthful. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context quality`

Measured context quality + minimum-sufficient decision for one capsule.

**Syntax**

```text
apiforge context quality <capsule> <run_id> [root] [required] [gate] [cache_hits] [cache_lookups] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `capsule` | yes | — | Recorded capsule JSON (`context capsule ... > capsule.json`). |
| `run_id` | yes | — | — |
| `root` | no | — | — |
| `required` | no | — | ctx:// uri declared required for recall (repeatable). |
| `gate` | no | — | strict|evidence|permissive. |
| `cache_hits` | no | — | — |
| `cache_lookups` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context resolve`

**Syntax**

```text
apiforge context resolve [root] [scope] [target] [impact] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `scope` | no | — | — |
| `target` | no | — | — |
| `impact` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## contract

### `contract`

List and inspect the canonical versioned contracts.

**Syntax**

```text
apiforge contract
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `contract list`

List the registered canonical contracts.

**Syntax**

```text
apiforge contract list [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `contract show`

Emit the JSON schema of a canonical contract.

**Syntax**

```text
apiforge contract show <name> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `name` | yes | — | Contract name, e.g. TaskSpec/v1. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## contract-intel

### `contract-intel`

Unify contract impact analysis and build an offline API Digital Twin.

**Syntax**

```text
apiforge contract-intel
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `contract-intel impact`

Classify compatibility and expose affected contract references.

**Syntax**

```text
apiforge contract-intel impact <protocol> <baseline> <candidate> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `protocol` | yes | — | openapi or grpc. |
| `baseline` | yes | — | — |
| `candidate` | yes | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `contract-intel twin`

Create a no-network Digital Twin plan and optionally simulate a scenario.

**Syntax**

```text
apiforge contract-intel twin <contract> <protocol> [dependency] [scenario] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `contract` | yes | — | — |
| `protocol` | yes | — | openapi or grpc. |
| `dependency` | no | — | Declared downstream dependency. |
| `scenario` | no | — | Simulate one scenario after planning. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## control

### `control`

Decision Control Plane lifecycle: shadow, assisted, active and fallback.

**Syntax**

```text
apiforge control
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control demote`

§32: step a route back one stage — the safe direction is always open.

**Syntax**

```text
apiforge control demote <route> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `route` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control eval`

§29-§32: who governs this evaluation under the route's mode.

**Syntax**

```text
apiforge control eval <route> [candidate] [legacy] [confidence] [evidence] [trigger] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `route` | yes | — | — |
| `candidate` | no | — | Candidate decision JSON. |
| `legacy` | no | — | Legacy decision JSON. |
| `confidence` | no | — | — |
| `evidence` | no | — | — |
| `trigger` | no | — | §32 trigger names. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control promote`

§30-§31: one lifecycle step; ACTIVE requires the five requirements.

**Syntax**

```text
apiforge control promote <route> <evidence> [approval] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `route` | yes | — | — |
| `evidence` | yes | — | PromotionEvidence JSON or file. |
| `approval` | no | — | ApprovalGate JSON. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control routes`

§28: every declared route with its effective lifecycle mode.

**Syntax**

```text
apiforge control routes [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control shadow`

§29: recorded parallel-run observations for a route.

**Syntax**

```text
apiforge control shadow [route] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `route` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control triggers`

§32: map declared signals to the closed trigger vocabulary.

**Syntax**

```text
apiforge control triggers [confidence] [min_confidence] [evidence_incomplete] [security_issue] [provider_issue] [budget_issue] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `confidence` | no | — | — |
| `min_confidence` | no | — | — |
| `evidence_incomplete` | no | — | — |
| `security_issue` | no | — | — |
| `provider_issue` | no | — | — |
| `budget_issue` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## debate

### `debate`

Record specialist disagreement — positions cite fact_ids, a referee closes.

**Syntax**

```text
apiforge debate
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `debate close`

Close as resolved (--decision) or unresolved (no --decision).

**Syntax**

```text
apiforge debate close <case> <debate> <referee> [decision] <now> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | yes | — | Case directory. |
| `debate` | yes | — | Debate id. |
| `referee` | yes | — | Who closes the debate. |
| `decision` | no | — | The decision; omit to record unresolved. |
| `now` | yes | — | ISO8601 timestamp. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `debate open`

Open a debate over a question with named sides.

**Syntax**

```text
apiforge debate open <case> <question> <sides> <now> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | yes | — | Case directory. |
| `question` | yes | — | What is disputed. |
| `sides` | yes | — | Comma-separated side names. |
| `now` | yes | — | ISO8601 timestamp — the only clock. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `debate packet`

Referee input: shared capsule id + one position delta per side + disagreements.

**Syntax**

```text
apiforge debate packet <case> <debate> [capsule] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | yes | — | Case directory. |
| `debate` | yes | — | Debate id. |
| `capsule` | no | — | Shared ctx:// capsule id. |
| `root` | no | — | Where the capsule was built. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `debate submit`

Append a position — every position must cite fact_id evidence.

**Syntax**

```text
apiforge debate submit <case> <debate> <side> <position> <evidence> [disagree] [risk] [confidence] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | yes | — | Case directory. |
| `debate` | yes | — | Debate id. |
| `side` | yes | — | Which side this position serves. |
| `position` | yes | — | The position text. |
| `evidence` | yes | — | Comma-separated fact_id citations. |
| `disagree` | no | — | Position delta: 'point=reason' (repeatable). |
| `risk` | no | — | Position delta risk (repeatable). |
| `confidence` | no | — | 0.0-1.0. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## devin

### `devin`

Generate and inspect offline-first payloads for Devin Desktop, CLI and Cloud.

**Syntax**

```text
apiforge devin
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `devin capabilities`

Report Devin capability declarations plus local CLI observation.

**Syntax**

```text
apiforge devin capabilities [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `devin payload`

Create a Devin payload; this command never starts Devin or mutates Git.

**Syntax**

```text
apiforge devin payload <objective> [surface] [task_kind] [root] [title] [permission_mode] [sandbox] [model] [platform] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `objective` | yes | — | Objective to send to Devin. |
| `surface` | no | — | desktop, cli or cloud. |
| `task_kind` | no | — | discovery, planning, implementation, verification, review or handoff. |
| `root` | no | — | — |
| `title` | no | — | — |
| `permission_mode` | no | — | — |
| `sandbox` | no | — | — |
| `model` | no | — | — |
| `platform` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `devin probe`

Observe whether a local Devin CLI executable is available on PATH.

**Syntax**

```text
apiforge devin probe [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## diff

### `diff`

Diff OpenAPI contracts.

**Syntax**

```text
apiforge diff
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `diff contract`

Classify bounded breaking changes between two contracts.

**Syntax**

```text
apiforge diff contract <baseline> <candidate> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `baseline` | yes | — | Baseline OpenAPI document. |
| `candidate` | yes | — | Candidate OpenAPI document. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## discover

### `discover`

Statically inventory FastAPI routes without executing code.

**Syntax**

```text
apiforge discover <project> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `project` | yes | — | FastAPI project root. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## dispatch

### `dispatch`

Run deterministic playbook steps; pending steps name their missing inputs.

**Syntax**

```text
apiforge dispatch
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `dispatch run`

Run a coordinator's playbook; pending steps name their missing inputs.

**Syntax**

```text
apiforge dispatch run <coordinator> <case> [project] [contract] [baseline] [candidate] [input_path] [findings] [rule_id] [tool] [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `coordinator` | yes | — | Coordinator name. |
| `case` | yes | — | Case directory. |
| `project` | no | — | — |
| `contract` | no | — | — |
| `baseline` | no | — | — |
| `candidate` | no | — | — |
| `input_path` | no | — | Dump/report/template path for model verbs. |
| `findings` | no | — | — |
| `rule_id` | no | — | — |
| `tool` | no | — | Tool selection for verbs that need one (perf scenario). |
| `now` | no | — | ISO8601 — the only clock. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## distribution

### `distribution`

Inspect the installed package, paths and hostless capabilities.

**Syntax**

```text
apiforge distribution
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `distribution doctor`

**Syntax**

```text
apiforge distribution doctor [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `distribution init`

**Syntax**

```text
apiforge distribution init [root] [workspace] [name] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `workspace` | no | — | — |
| `name` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `distribution inspect`

**Syntax**

```text
apiforge distribution inspect [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `distribution status`

**Syntax**

```text
apiforge distribution status [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## doctor

### `doctor`

Inspect runtime state, or the local installation when no task is supplied.

**Syntax**

```text
apiforge doctor [task_id] [root] [economy] [agentic] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | no | — | TaskSpec id, or omit for installation doctor. |
| `root` | no | — | — |
| `economy` | no | — | Economy diagnostics instead. |
| `agentic` | no | — | Cross-plane agentic health report. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## economy

### `economy`

Measured cost per call — bytes recorded, tokens unresolved without a transcript.

**Syntax**

```text
apiforge economy
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy budget-check`

Check a proposed spend without appending it.

**Syntax**

```text
apiforge economy budget-check <plan_id> <task_id> <phase> <role> <tool> <spend_id> <cost> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `plan_id` | yes | — | — |
| `task_id` | yes | — | — |
| `phase` | yes | — | — |
| `role` | yes | — | — |
| `tool` | yes | — | — |
| `spend_id` | yes | — | — |
| `cost` | yes | — | CostVector JSON or JSON file. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy budget-plan`

Register an immutable hierarchical budget plan.

**Syntax**

```text
apiforge economy budget-plan <plan> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `plan` | yes | — | JSON declaration with task_id, limits and created_at. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy budget-spend`

Admit and append one measured spend receipt.

**Syntax**

```text
apiforge economy budget-spend <plan_id> <spend_id> <task_id> <phase> <role> <tool> <cost> <observed_at> [provenance] [evidence] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `plan_id` | yes | — | — |
| `spend_id` | yes | — | — |
| `task_id` | yes | — | — |
| `phase` | yes | — | — |
| `role` | yes | — | — |
| `tool` | yes | — | — |
| `cost` | yes | — | CostVector JSON or JSON file. |
| `observed_at` | yes | — | — |
| `provenance` | no | — | — |
| `evidence` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy cost`

Price an accounting under the declared catalog; gaps stay named.

**Syntax**

```text
apiforge economy cost <provider> <model> <accounting> [at] [pricing] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `provider` | yes | — | — |
| `model` | yes | — | — |
| `accounting` | yes | — | TokenAccounting JSON or file. |
| `at` | no | — | — |
| `pricing` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy doctor`

What in this setup makes runs pay more than needed, with the unlock for each.

**Syntax**

```text
apiforge economy doctor [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy explain`

Why each ref of a run was spent, from recorded provenance rules only.

**Syntax**

```text
apiforge economy explain <run_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | run_id printed by `context capsule`. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy ledger`

Per-basis token rollup for a run — observed and estimated never mix.

**Syntax**

```text
apiforge economy ledger <run_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy phase-budget`

Profile envelope split across SDD phases; protected phases are never cut.

**Syntax**

```text
apiforge economy phase-budget [profile] [usage] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `profile` | no | — | — |
| `usage` | no | — | Per-phase usage JSON. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy pricing`

List the declared pricing catalog — prices are never hardcoded.

**Syntax**

```text
apiforge economy pricing [pricing] [limit] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `pricing` | no | — | — |
| `limit` | no | — | Bound carried entries; count stays the real total. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy providers`

Declared provider capabilities and deterministic capabilities.

**Syntax**

```text
apiforge economy providers [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy reconcile`

§22 estimated vs observed for a run, with calibration error per axis.

**Syntax**

```text
apiforge economy reconcile <run_id> <estimate> [observed_cost] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `estimate` | yes | — | Estimate JSON/yaml or file: tokens/cost/tool_calls/elapsed_ms. |
| `observed_cost` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy record-usage`

Append usage rows for a run; the file is append-only.

**Syntax**

```text
apiforge economy record-usage <run_id> [task_id] [agent] [transcript] [estimate] [method] <recorded_at> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `task_id` | no | — | — |
| `agent` | no | — | — |
| `transcript` | no | — | Host transcript JSONL; derives observed rows. |
| `estimate` | no | — | Declared token estimate; derives an estimated row. |
| `method` | no | — | — |
| `recorded_at` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy report`

Aggregate recorded call sizes; detail_level_effect shows what summary saves.

**Syntax**

```text
apiforge economy report [root] [transcript] [estimate] [cost_basis] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Directory whose .apiforge/economy.jsonl to aggregate. |
| `transcript` | no | — | Host transcript JSONL; unlocks counted tokens. |
| `estimate` | no | — | Add a labeled chars/4 estimate (never counted). |
| `cost_basis` | no | — | YAML model->rates; unlocks dollar cost. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy roi`

Per extra capability: calls, facts and unresolved added, outcome changed vs primary.

**Syntax**

```text
apiforge economy roi [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy stats`

Bytes attributed per run and source; tokens stay unresolved without a transcript.

**Syntax**

```text
apiforge economy stats [root] [run_id] [transcript] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `run_id` | no | — | — |
| `transcript` | no | — | Host transcript JSONL; unlocks observed tokens. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy tier`

Cheapest tier the evidence proves sufficient (T0-T3), with the reason.

**Syntax**

```text
apiforge economy tier <capability> [risk] [family] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `capability` | yes | — | — |
| `risk` | no | — | — |
| `family` | no | — | — |
| `root` | no | — | Where scorecards live. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## evals

### `evals`

Declarative local eval matrix, goldens and holdout metadata.

**Syntax**

```text
apiforge evals
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals agent-governor`

§23-§27 governor primitives vs declared corpus expectations.

**Syntax**

```text
apiforge evals agent-governor [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals agent-routing`

Deterministic proxy-router eval: top-1/top-3, per family, protected-role misroutes.

**Syntax**

```text
apiforge evals agent-routing [root] [cases] [baseline] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Repository root. |
| `cases` | no | — | Golden cases JSON. |
| `baseline` | no | — | Previous agent-routing report; top-1 may not regress. |
| `out` | no | — | Write the report JSON here. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals agentic-quality`

Recorded specialist verdicts vs ground truth under each profile (no model calls).

**Syntax**

```text
apiforge evals agentic-quality [corpus] [responses_dir] [min_accuracy] [baseline] [allow_cross_corpus_baseline] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `responses_dir` | no | — | Recorded outputs: <case_id>.json capability -> payload. |
| `min_accuracy` | no | — | Absolute accuracy floor every profile must reach. |
| `baseline` | no | — | Previous agentic-quality report; no profile may regress. |
| `allow_cross_corpus_baseline` | no | — | Compare with a baseline of another benchmark (recorded as cross_corpus). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals agentops`

§53–§57: seeded ledgers -> inspect/compare/waste verdicts.

**Syntax**

```text
apiforge evals agentops [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals cache`

Warm/mutate/rebuild: all-hit on unchanged, precise invalidation, zero stale reuse.

**Syntax**

```text
apiforge evals cache [corpus] [repo_root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals context-quality`

Fixture capsule + recorded uses vs declared metrics and sufficiency gates.

**Syntax**

```text
apiforge evals context-quality [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals control-plane`

§28-§32 lifecycle: shadow never governs, promotion gates, fallback.

**Syntax**

```text
apiforge evals control-plane [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals economy`

Capsule bytes and evidence recall vs the recorded baseline; exit 1 when a gate fails.

**Syntax**

```text
apiforge evals economy [corpus] [repo_root] [record] [min_reduction] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `record` | no | — | Measure and persist the no-gateway baseline only. |
| `min_reduction` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals economy-extras`

Verification plans, retrieval, evidence refs, doctor, tiers, prefixes and locality gates.

**Syntax**

```text
apiforge evals economy-extras [corpus] [repo_root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals economy-freshness`

Freshness watch, live gating, escalation, phase budget and resume pinning gates.

**Syntax**

```text
apiforge evals economy-freshness [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals economy-hardening`

Path containment, class-pool budget, tokens, phase and delta gates on production code.

**Syntax**

```text
apiforge evals economy-hardening [corpus] [repo_root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals economy-matrix`

Canonical tasks x economy/balanced/deep with quality, evidence, cost, context, latency apart.

**Syntax**

```text
apiforge evals economy-matrix [corpus] [repo_root] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `out` | no | — | Write the EconomyMatrix/v1 report. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals economy-routing`

Profiles vs pre-economy plans with the risk floor as invariant; exit 1 on gate failure.

**Syntax**

```text
apiforge evals economy-routing [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals forge-protocol`

§46–§48: submit/attach/inspect/result/evidence/handoff/health lifecycle.

**Syntax**

```text
apiforge evals forge-protocol [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals frontier`

§23: quality x cost x latency frontier across profiles.

**Syntax**

```text
apiforge evals frontier <report> [latencies] [costs] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `report` | yes | — | agentic-quality report JSON |
| `latencies` | no | — | optional yaml {latency_ms: {profile: ms}} |
| `costs` | no | — | optional yaml {cost: {profile: usd}} |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals gate`

Ship only without quality, safety, holdout or mutation regression; exit 1 on reject.

**Syntax**

```text
apiforge evals gate <baseline> <candidate> [max_quality_regression] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `baseline` | yes | — | EconomyMatrix/v1 before the change. |
| `candidate` | yes | — | EconomyMatrix/v1 after the change. |
| `max_quality_regression` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals graph-quality`

Per-rule x language precision/recall of graph rules over the golden corpus.

**Syntax**

```text
apiforge evals graph-quality [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals knowledge-drift`

§29 drift verdicts over declared pack+receipt cases.

**Syntax**

```text
apiforge evals knowledge-drift [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals list`

List declarative eval cases without executing agents.

**Syntax**

```text
apiforge evals list [path] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals live`

§23: deterministic tier observed; provider tier deferred_external.

**Syntax**

```text
apiforge evals live [layer] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `layer` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals memory-evals`

§24: the eight memory axes against the real governed store.

**Syntax**

```text
apiforge evals memory-evals [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals model-routing`

§33-§35 router constraints, scorecard floors and promotion evidence.

**Syntax**

```text
apiforge evals model-routing [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals replay`

Re-plan stored decisions under the current policy; exit 1 if a required role is removed.

**Syntax**

```text
apiforge evals replay [root] [corpus] [profile] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Replay stored runs under a root. |
| `corpus` | no | — | Replay stored run bundles. |
| `profile` | no | — | Re-plan under this profile. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals retrieval`

§38: lexical/graph/semantic/hybrid on recall, precision, latency, cost.

**Syntax**

```text
apiforge evals retrieval [corpus] [root] [graph_dir] [cost_rate] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `root` | no | — | Knowledge packs directory. |
| `graph_dir` | no | — | Hashed graph directory for the graph strategy. |
| `cost_rate` | no | — | Declared cost per token. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals security-adversarial`

§25: synthesized attacks against the platform's own defenses.

**Syntax**

```text
apiforge evals security-adversarial [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals selective-agentics`

Lazy expertise, per-role bytes, referee packets, shadow share and agent audit gates.

**Syntax**

```text
apiforge evals selective-agentics [corpus] [repo_root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals telemetry-otlp`

§50-§52: ledger spans -> OTLP export -> structural acceptance.

**Syntax**

```text
apiforge evals telemetry-otlp [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals token-economics`

Usage rows + pricing + estimate vs ledger/cost/calibration expectations.

**Syntax**

```text
apiforge evals token-economics [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals tool-economy`

Compact output, gateway surface, discover/call reach and slicer recall gates.

**Syntax**

```text
apiforge evals tool-economy [corpus] [repo_root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `repo_root` | no | — | Where fixture paths resolve. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals tool-surface`

§40–§43: audit findings, disclosure routing, paging, benchmark honesty.

**Syntax**

```text
apiforge evals tool-surface [corpus] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals trace-grading`

§23: recorded traces graded against the declared rubric.

**Syntax**

```text
apiforge evals trace-grading [corpus] [rubric] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `corpus` | no | — | — |
| `rubric` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals validate`

Validate closed eval vocabulary and mutation/holdout requirements.

**Syntax**

```text
apiforge evals validate [path] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## evidence

### `evidence`

Release evidence receipts.

**Syntax**

```text
apiforge evidence
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evidence emit`

Emit a receipt binding artifact paths to their sha256 contents.

**Syntax**

```text
apiforge evidence emit <case> <out> [now] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | yes | — | Persisted case directory. |
| `out` | yes | — | Receipt output path. |
| `now` | no | — | Explicit timestamp; the only clock source. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evidence gate`

Cheapest evidence mode for a question; live_read_only only for runtime questions.

**Syntax**

```text
apiforge evidence gate <question> [mode] [offline] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `question` | yes | — | — |
| `mode` | no | — | Requested evidence mode. |
| `offline` | no | — | No live access in this run. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evidence resolve`

One evidence node with one-hop neighbors as further evidence:// refs.

**Syntax**

```text
apiforge evidence resolve <ref> [root] [case_dir] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `ref` | yes | — | evidence://{operation|fact|finding|rule}/<id> |
| `root` | no | — | — |
| `case_dir` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evidence verify`

Re-hash every artifact a receipt lists.

**Syntax**

```text
apiforge evidence verify <receipt> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `receipt` | yes | — | Receipt JSON file. |
| `root` | no | — | Artifact base dir; defaults to receipt.case. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## evolve

### `evolve`

Execute a bounded, evidence-backed API evolution run.

**Syntax**

```text
apiforge evolve <task_id> [root] [policy] [now] [debate] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | TaskSpec id to execute. |
| `root` | no | — | — |
| `policy` | no | — | — |
| `now` | no | — | — |
| `debate` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## experience

### `experience`

Canonical execution, governance and evidence projections.

**Syntax**

```text
apiforge experience
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `experience doctor`

**Syntax**

```text
apiforge experience doctor <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `experience review`

**Syntax**

```text
apiforge experience review <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `experience status`

**Syntax**

```text
apiforge experience status <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## field

### `field`

Pre-registered field validation: evidence-joined run records and gap report.

**Syntax**

```text
apiforge field
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `field annotate`

Record human fields with closed enums.

**Syntax**

```text
apiforge field annotate <task> [phase] [completed] [exit_reason] [manual_context] [human_intervention] [false_positives] [false_negatives] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task` | yes | — | — |
| `phase` | no | — | — |
| `completed` | no | — | — |
| `exit_reason` | no | — | — |
| `manual_context` | no | — | — |
| `human_intervention` | no | — | — |
| `false_positives` | no | — | — |
| `false_negatives` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `field export`

Write anonymized verified tasks into evals/corpus/field.

**Syntax**

```text
apiforge field export [root] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `out` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `field record`

Join ledger, summary and checkpoint of linked runs into a field-run/v1 record.

**Syntax**

```text
apiforge field record <task> <run> [phase] <started> <ended> <executor> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task` | yes | — | Task id pre-registered in docs/field/corpus.yaml. |
| `run` | yes | — | Linked runtime run_id (repeatable). |
| `phase` | no | — | baseline | ab_on |
| `started` | yes | — | RFC3339 wall-clock task start. |
| `ended` | yes | — | RFC3339 wall-clock task end. |
| `executor` | yes | — | Who executed the task: human:sha256:<64 hex> or agent:<roster-name>. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `field report`

Counts, Wilson 95% CI, theme qualification and H1 verdict from verified runs.

**Syntax**

```text
apiforge field report [root] [ab] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `ab` | no | — | Include baseline vs ab_on deltas. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `field verify`

Blind verifier verdict; never echoes the human labels.

**Syntax**

```text
apiforge field verify <task> <verdict> <verifier> [phase] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task` | yes | — | — |
| `verdict` | yes | — | agree | disagree | unresolved |
| `verifier` | yes | — | Independent verifier: human:sha256:<64 hex> or agent:<roster-name>. |
| `phase` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## forge

### `forge`

Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health.

**Syntax**

```text
apiforge forge
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge attach`

§47 link a forge task to its governed TaskSpec execution unit.

**Syntax**

```text
apiforge forge attach <task_id> <governed_task> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `governed_task` | yes | — | TaskSpec id to link (must exist). |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge capabilities`

§46 discover: public capability descriptors other engines can call.

**Syntax**

```text
apiforge forge capabilities [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge evidence`

§47 retrieve evidence: content-addressed artifact bundle.

**Syntax**

```text
apiforge forge evidence <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge handoff`

§47/§48 handoff: portable bundle — delivery stays a human step.

**Syntax**

```text
apiforge forge handoff <task_id> <to_engine> [context_ref] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `to_engine` | yes | — | Declared peer engine (rules/forge_protocol.yaml). |
| `context_ref` | no | — | ctx:// ref to carry (repeatable). |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge health`

§47 health: engine, protocol version and declared task counts.

**Syntax**

```text
apiforge forge health [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge inspect`

§47 inspect: live wire projection of forge + governed state.

**Syntax**

```text
apiforge forge inspect <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge result`

§47 retrieve result: governed OutcomeBrief mapped, gaps named.

**Syntax**

```text
apiforge forge result <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge submit`

§47 submit: validate capability + risk gate, persist the request.

**Syntax**

```text
apiforge forge submit <task_id> <capability> <intent> [risk] [inputs] [requested_by] [origin_engine] [acknowledge_risk] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | lowercase, digits, hyphens. |
| `capability` | yes | — | Public capability_id. |
| `intent` | yes | — | What the task must achieve. |
| `risk` | no | — | CapabilityRisk literal. |
| `inputs` | no | — | JSON object with declared task inputs. |
| `requested_by` | no | — | — |
| `origin_engine` | no | — | — |
| `acknowledge_risk` | no | — | Required for gated risk classes. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## governance

### `governance`

Fail-closed agentic decision gates.

**Syntax**

```text
apiforge governance
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governance decision-check`

Evaluate and record a proposal; never infer approval from model text.

**Syntax**

```text
apiforge governance decision-check <request> [approval] [policy] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `request` | yes | — | DecisionRequest JSON file. |
| `approval` | no | — | ApprovalGate JSON file. |
| `policy` | no | — | AgenticPolicy JSON file. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## governor

### `governor`

Agent Governor decisions: ceilings, gain, stop, recovery and loop checks.

**Syntax**

```text
apiforge governor
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governor decide`

§23: profile ceilings adjusted by risk, security and budget.

**Syntax**

```text
apiforge governor decide <inputs> [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `inputs` | yes | — | GovernorInputs JSON or file. |
| `policy` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governor gain`

§24: pre-action expected information gain over declared signals.

**Syntax**

```text
apiforge governor gain <action> <signals> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `action` | yes | — | spawn_agent|call_reviewer|start_debate|expand_context|expensive_retrieval |
| `signals` | yes | — | JSON map of §24 signals. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governor loop-check`

§27: block a strategy that repeats inside the trailing window.

**Syntax**

```text
apiforge governor loop-check <fingerprints> [window] [max_repeats] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `fingerprints` | yes | — | JSON list of strategy fingerprints. |
| `window` | no | — | — |
| `max_repeats` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governor recover`

§26: governed recovery for a classified failure.

**Syntax**

```text
apiforge governor recover <failure_class> [attempt] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `failure_class` | yes | — | — |
| `attempt` | no | — | — |
| `policy` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governor stop`

§25: explicit STOP — continue only on gain > threshold or requirement.

**Syntax**

```text
apiforge governor stop <action> <signals> [mandatory] [threshold] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `action` | yes | — | — |
| `signals` | yes | — | — |
| `mandatory` | no | — | — |
| `threshold` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## graph

### `graph`

Native provenance graph — canonical JSONL store, closed-vocabulary queries.

**Syntax**

```text
apiforge graph
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph build`

Populate nodes.jsonl/edges.jsonl from case artifacts — deterministic bytes.

**Syntax**

```text
apiforge graph build <case> <out> [tasks_root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | yes | — | Case directory with case.json. |
| `out` | yes | — | Graph output directory. |
| `tasks_root` | no | — | Root holding .apiforge/tasks for task nodes. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph coverage`

Structural gaps: unverified findings, unimplemented ops, unreferenced facts.

**Syntax**

```text
apiforge graph coverage <graph> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph export`

jsonl copy, Neptune Gremlin CSV or RDF N-Triples, plus export.json digests.

**Syntax**

```text
apiforge graph export <graph> <out> [fmt] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory. |
| `out` | yes | — | Export directory. |
| `fmt` | no | — | jsonl|neptune (Gremlin CSV)|rdf (N-Triples). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph impact`

Reverse traversal: everything that transitively depends on the node.

**Syntax**

```text
apiforge graph impact <graph> <node> [max_depth] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory. |
| `node` | yes | — | Node id whose dependents to list. |
| `max_depth` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph query`

Filter nodes/edges by closed vocabulary — no free text.

**Syntax**

```text
apiforge graph query <graph> [kind] [edge_kind] [prop] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory (nodes.jsonl). |
| `kind` | no | — | Filter nodes by kind. |
| `edge_kind` | no | — | Filter edges by kind. |
| `prop` | no | — | Node prop filter `k=v` (repeatable). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph trace`

Shortest directed path between two nodes; absent path is named.

**Syntax**

```text
apiforge graph trace <graph> <from_id> <to_id> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory. |
| `from_id` | yes | — | Source node id. |
| `to_id` | yes | — | Target node id. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph ui`

Open the local Graph Studio explorer for this graph.

**Syntax**

```text
apiforge graph ui <graph> [no_browser] [port]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory (nodes.jsonl). |
| `no_browser` | no | — | Serve without opening a browser (SSH/remote). |
| `port` | no | — | Port to bind (default ephemeral). |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph view`

Emit the ForgeGraphView/v1 document (Graph Studio contract).

**Syntax**

```text
apiforge graph view <graph>
```

| argument/flag | required | default | description |
|---|---|---|---|
| `graph` | yes | — | Graph directory (nodes.jsonl). |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## grpc

### `grpc`

Offline-first gRPC contract control plane.

**Syntax**

```text
apiforge grpc
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc analyze`

Build the canonical gRPC IR without invoking external toolchains.

**Syntax**

```text
apiforge grpc analyze <source> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | .proto or descriptor source. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc benchmark`

Evaluate RPS/TPS evidence without claiming capacity from invalid runs.

**Syntax**

```text
apiforge grpc benchmark <run> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run` | yes | — | JSON performance run. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc capabilities`

Show optional local gRPC toolchain capabilities.

**Syntax**

```text
apiforge grpc capabilities [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc codegen`

Generate deterministic local artifacts or report missing toolchains.

**Syntax**

```text
apiforge grpc codegen <source> [language] [output_dir] [tool] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | — |
| `language` | no | — | — |
| `output_dir` | no | — | — |
| `tool` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc diff`

Classify protobuf evolution using deterministic compatibility rules.

**Syntax**

```text
apiforge grpc diff <baseline> <candidate> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `baseline` | yes | — | — |
| `candidate` | yes | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc discover`

Discover a gRPC contract and expose its canonical IR.

**Syntax**

```text
apiforge grpc discover <source> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | .proto or descriptor source. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc gateway`

Project the contract to local gateway artifacts.

**Syntax**

```text
apiforge grpc gateway <source> [gateway] [output_dir] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | — |
| `gateway` | no | — | — |
| `output_dir` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc test`

Run the offline contract test and independent verification gates.

**Syntax**

```text
apiforge grpc test <source> [baseline] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | — |
| `baseline` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc verify`

Run independent local verification over a gRPC contract.

**Syntax**

```text
apiforge grpc verify <source> [baseline] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | — |
| `baseline` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## index

### `index`

TokenSave: content-hash cache + local indexes over extractor output.

**Syntax**

```text
apiforge index
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `index build`

Write the 12 index kinds under .apiforge/index/ (manifest lists all).

**Syntax**

```text
apiforge index build <project> [root] [framework] [findings] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `project` | yes | — | Project root to index. |
| `root` | no | — | Root holding .apiforge/. |
| `framework` | no | — | fastapi|spring|go|auto. |
| `findings` | no | — | Case findings.json feeding the derived findings index. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `index status`

Name added/changed/removed source files against the built index.

**Syntax**

```text
apiforge index status <project> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `project` | yes | — | Project root to compare. |
| `root` | no | — | Root holding .apiforge/. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## init

### `init`

Create only a minimal local project or workspace manifest.

**Syntax**

```text
apiforge init [root] [workspace] [name] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `workspace` | no | — | — |
| `name` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## inspect

### `inspect`

Inspect installed assets and bounded project/workspace discovery.

**Syntax**

```text
apiforge inspect [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## install

### `install`

Install API Forge assets into a project, workspace or the user home; manage the lifecycle (status, doctor, repair, update, uninstall).

**Syntax**

```text
apiforge install [scope] [host] [profile] [root] [yes] [dry_run] [components] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `scope` | no | — | project|workspace|user. |
| `host` | no | — | claude|devin|codex|copilot|all. |
| `profile` | no | — | minimal|recommended|full. |
| `root` | no | — | Target root (default: VCS root or cwd). |
| `yes` | no | — | Explicit approval; without it only --dry-run is allowed. |
| `dry_run` | no | — | Plan only — writes nothing. |
| `components` | no | — | Optional components csv: skills,agents,mcp,tui,graph-studio. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `install doctor`

Deep installation health: ledger, drift, mcp config, handshake.

**Syntax**

```text
apiforge install doctor [scope] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `scope` | no | — | project|workspace|user. |
| `root` | no | — | Target root (default: VCS root or cwd). |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `install repair`

Rewrite managed assets that went missing or drifted.

**Syntax**

```text
apiforge install repair [scope] [root] [dry_run] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `scope` | no | — | project|workspace|user. |
| `root` | no | — | Target root (default: VCS root or cwd). |
| `dry_run` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `install status`

Ledger + drift + health document of the installation.

**Syntax**

```text
apiforge install status [scope] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `scope` | no | — | project|workspace|user. |
| `root` | no | — | Target root (default: VCS root or cwd). |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `install uninstall`

Remove only what the ledger declares as managed.

**Syntax**

```text
apiforge install uninstall [scope] [root] [purge] [dry_run] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `scope` | no | — | project|workspace|user. |
| `root` | no | — | Target root (default: VCS root or cwd). |
| `purge` | no | — | Also delete the state dir .apiforge/install. |
| `dry_run` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `install update`

Upgrade the bootstrap-installed runtime.

**Syntax**

```text
apiforge install update [to] [repo] [dry_run] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `to` | no | — | Pinned target version (never 'latest'). |
| `repo` | no | — | Checkout to install/upgrade from. |
| `dry_run` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `install verify`

Real JSON-RPC handshake: initialize + tools/list on the MCP server.

**Syntax**

```text
apiforge install verify [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## integration

### `integration`

Read-only external evidence adapters and freshness receipts.

**Syntax**

```text
apiforge integration
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `integration github-issues`

Read GitHub issues through a GET-only adapter and emit a receipt.

**Syntax**

```text
apiforge integration github-issues <repository> [state] [api_base] [max_age] [out] [token_env] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `repository` | yes | — | — |
| `state` | no | — | — |
| `api_base` | no | — | — |
| `max_age` | no | — | — |
| `out` | no | — | Optional JSON evidence path. |
| `token_env` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `integration health`

Read a remote HTTP health endpoint and emit a freshness receipt.

**Syntax**

```text
apiforge integration health <url> [max_age] [out] [token_env] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `url` | yes | — | — |
| `max_age` | no | — | — |
| `out` | no | — | Optional JSON evidence path. |
| `token_env` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `integration json`

Read a generic external JSON endpoint (Jira, Linear or similar).

**Syntax**

```text
apiforge integration json <url> [max_age] [out] [token_env] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `url` | yes | — | — |
| `max_age` | no | — | — |
| `out` | no | — | Optional JSON evidence path. |
| `token_env` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `integration verify-receipt`

Verify external receipt correspondence and declared freshness.

**Syntax**

```text
apiforge integration verify-receipt <receipt> <now> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `receipt` | yes | — | — |
| `now` | yes | — | Explicit ISO-8601 verification time. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## judge

### `judge`

Judge contract/code divergence, or catalog checks over report facts.

**Syntax**

```text
apiforge judge [contract] [project] [facts] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `contract` | no | — | OpenAPI 3.1 document. |
| `project` | no | — | FastAPI project root. |
| `facts` | no | — | facts.json emitted by a `model *` verb. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## knowledge

### `knowledge`

Domain packs — source authority, runtime matrices, declared evals.

**Syntax**

```text
apiforge knowledge
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge adaptive`

§36: L0→L4 ladder; escalates only while the level is insufficient.

**Syntax**

```text
apiforge knowledge adaptive <query> [max_level] [semantic] [root] [graph_dir] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `query` | yes | — | — |
| `max_level` | no | — | L0..L4 ceiling. |
| `semantic` | no | — | Declare the local adapter. |
| `root` | no | — | Directory of knowledge packs. |
| `graph_dir` | no | — | Graph JSONL directory. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge check`

Validate every pack; exit 4 when any problem is named.

**Syntax**

```text
apiforge knowledge check [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Directory of knowledge packs. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge drift`

§29 drift verdict across one or more read-only source receipts.

**Syntax**

```text
apiforge knowledge drift <domain> [receipts] [root] <now> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `domain` | yes | — | Pack directory name. |
| `receipts` | no | — | Read-only observation JSON; repeatable. |
| `root` | no | — | — |
| `now` | yes | — | Explicit ISO8601 clock. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge freshness`

Verify pack freshness from a local read-only source receipt.

**Syntax**

```text
apiforge knowledge freshness <domain> [receipt] [root] <now> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `domain` | yes | — | Pack directory name. |
| `receipt` | no | — | Read-only observation JSON. |
| `root` | no | — | — |
| `now` | yes | — | Explicit ISO8601 clock. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge impact`

§29 source -> pack -> rule -> skill -> eval relation graph.

**Syntax**

```text
apiforge knowledge impact [root] [skills] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `skills` | no | — | Skill manifests directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge list`

List every pack with its areas, rules and verification date.

**Syntax**

```text
apiforge knowledge list [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | Directory of knowledge packs. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge rewrite`

§39: rewrite only when deterministic retrieval failed + gates allow.

**Syntax**

```text
apiforge knowledge rewrite <query> [deterministic_hits] [profile] [budget] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `query` | yes | — | — |
| `deterministic_hits` | no | — | — |
| `profile` | no | — | — |
| `budget` | no | — | budget_remaining JSON. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge search`

Deterministic expansion, ranked passages with signals, progressive tiers.

**Syntax**

```text
apiforge knowledge search <query> [tier] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `query` | yes | — | — |
| `tier` | no | — | 1 = top 3, 2 = top 5, 3 = up to 20. |
| `root` | no | — | Directory of knowledge packs. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge select`

Only the packs a declared trigger names; no trigger means no packs.

**Syntax**

```text
apiforge knowledge select <intent> [capability] [framework] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `intent` | yes | — | What the task is about. |
| `capability` | no | — | — |
| `framework` | no | — | Observed framework. |
| `root` | no | — | Directory of knowledge packs. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge show`

Print one pack: summary, source authority, matrix, declared evals.

**Syntax**

```text
apiforge knowledge show <domain> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `domain` | yes | — | Pack directory name, e.g. rest-design. |
| `root` | no | — | Directory of knowledge packs. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge watch`

Packs whose upstream fingerprint, version or expiry says refresh_needed (never fetches).

**Syntax**

```text
apiforge knowledge watch <manifest> <now> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `manifest` | yes | — | Local upstream fingerprint JSON. |
| `now` | yes | — | Explicit ISO8601 clock. |
| `root` | no | — | Directory of knowledge packs. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## lab

### `lab`

Opt-in experimental scenario catalog (§28).

**Syntax**

```text
apiforge lab
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `lab scenarios`

§28 experimental scenario catalog with honest coverage states.

**Syntax**

```text
apiforge lab scenarios [catalog] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `catalog` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## mcp

### `mcp`

MCP surface projections and their measured cost.

**Syntax**

```text
apiforge mcp
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `mcp audit`

§40 audit: oversized schemas/outputs, weak descriptions, unbounded lists.

**Syntax**

```text
apiforge mcp audit [surface] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `surface` | no | — | full|compact. |
| `policy` | no | — | rules/tool_surface.yaml override. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `mcp benchmark`

§43 measured response bytes + labeled token estimate per sampled tool.

**Syntax**

```text
apiforge mcp benchmark [repeats] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `repeats` | no | — | Invocations per sampled tool. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `mcp disclose`

§41 task -> capability router -> active tool set (advisory).

**Syntax**

```text
apiforge mcp disclose <task> [task_class] [surface] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task` | yes | — | Task text to route to a tool set. |
| `task_class` | no | — | Declared class override. |
| `surface` | no | — | full|compact. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `mcp surface`

Name, description and schema bytes of every tool on a surface.

**Syntax**

```text
apiforge mcp surface [surface] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `surface` | no | — | full|compact. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## memory

### `memory`

Governed append-only agent memory.

**Syntax**

```text
apiforge memory
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory invalidate`

**Syntax**

```text
apiforge memory invalidate <memory_id> <reason> <by> <now> [evidence] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `memory_id` | yes | — | — |
| `reason` | yes | — | — |
| `by` | yes | — | — |
| `now` | yes | — | — |
| `evidence` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory persist`

**Syntax**

```text
apiforge memory persist <candidate_id> [policy] <now> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `candidate_id` | yes | — | — |
| `policy` | no | — | — |
| `now` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory propose`

**Syntax**

```text
apiforge memory propose <scope> <origin> <payload> <proposed_by> <reason> <created_at> [observed_at] [expires_at] [trust_level] [provenance] [evidence] [environment] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `scope` | yes | — | — |
| `origin` | yes | — | — |
| `payload` | yes | — | JSON value or JSON file. |
| `proposed_by` | yes | — | — |
| `reason` | yes | — | — |
| `created_at` | yes | — | — |
| `observed_at` | no | — | — |
| `expires_at` | no | — | — |
| `trust_level` | no | — | — |
| `provenance` | no | — | — |
| `evidence` | no | — | — |
| `environment` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory quarantine-list`

List pending and released quarantine rows.

**Syntax**

```text
apiforge memory quarantine-list [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory quarantine-resolve`

Human review boundary: release a quarantined candidate.

**Syntax**

```text
apiforge memory quarantine-resolve <candidate_id> <verdict> <resolved_by> [policy] [minimum_trust] <now> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `candidate_id` | yes | — | — |
| `verdict` | yes | — | persist or reject |
| `resolved_by` | yes | — | — |
| `policy` | no | — | — |
| `minimum_trust` | no | — | explicit human floor for the release |
| `now` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory rank`

§15 ranked retrieval: per-record score decomposition, deterministic.

**Syntax**

```text
apiforge memory rank [term] [scope] [environment] [minimum_trust] [now] [include_invalidated] [max_results] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `term` | no | — | — |
| `scope` | no | — | — |
| `environment` | no | — | — |
| `minimum_trust` | no | — | — |
| `now` | no | — | — |
| `include_invalidated` | no | — | — |
| `max_results` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory search`

**Syntax**

```text
apiforge memory search [term] [scope] [environment] [minimum_trust] [now] [include_invalidated] [max_results] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `term` | no | — | — |
| `scope` | no | — | — |
| `environment` | no | — | — |
| `minimum_trust` | no | — | — |
| `now` | no | — | — |
| `include_invalidated` | no | — | — |
| `max_results` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## migration

### `migration`

Offline-first runtime migration analysis and verification.

**Syntax**

```text
apiforge migration
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `migration analyze`

Discover runtime migration impact without changing the project.

**Syntax**

```text
apiforge migration analyze <project> <ecosystem> <source> <target> [matrix] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `project` | yes | — | Project root to inspect. |
| `ecosystem` | yes | — | java, python or go. |
| `source` | yes | — | — |
| `target` | yes | — | — |
| `matrix` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `migration matrix`

Project an observed compatibility matrix; missing cells remain unresolved.

**Syntax**

```text
apiforge migration matrix <ecosystem> [receipt] [matrix] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `ecosystem` | yes | — | — |
| `receipt` | no | — | Runtime receipt JSON; repeatable. |
| `matrix` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `migration plan`

Build a closed migration TaskSpec and dependency DAG.

**Syntax**

```text
apiforge migration plan <project> <ecosystem> <source> <target> [matrix] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `project` | yes | — | Project root to inspect. |
| `ecosystem` | yes | — | — |
| `source` | yes | — | — |
| `target` | yes | — | — |
| `matrix` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `migration verify`

Apply conservative status gates to a migration report.

**Syntax**

```text
apiforge migration verify <report> [evidence_ok] [verification_ok] [contract_breaking] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `report` | yes | — | MigrationReport JSON. |
| `evidence_ok` | no | — | — |
| `verification_ok` | no | — | — |
| `contract_breaking` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## model

### `model`

Build the canonical API-IR.

**Syntax**

```text
apiforge model
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model alb`

**Syntax**

```text
apiforge model alb <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model api-gateway`

Read an API Gateway dump into facts — offline, no credentials.

**Syntax**

```text
apiforge model api-gateway <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from collect api-gateway. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model asyncapi`

**Syntax**

```text
apiforge model asyncapi <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | AsyncAPI 2.x/3.x document. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model build`

Compose the API-IR and print it.

**Syntax**

```text
apiforge model build <contract> <project> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `contract` | yes | — | OpenAPI 3.1 document. |
| `project` | yes | — | FastAPI project root. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model cloudwatch`

**Syntax**

```text
apiforge model cloudwatch <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model cognito`

**Syntax**

```text
apiforge model cognito <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model coverage`

**Syntax**

```text
apiforge model coverage <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | coverage.py JSON report. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model docdb`

**Syntax**

```text
apiforge model docdb <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model dynamodb`

**Syntax**

```text
apiforge model dynamodb <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model dynamodb-access`

**Syntax**

```text
apiforge model dynamodb-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model ec2`

**Syntax**

```text
apiforge model ec2 <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model ecs`

**Syntax**

```text
apiforge model ecs <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model eks`

**Syntax**

```text
apiforge model eks <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model elasticache`

**Syntax**

```text
apiforge model elasticache <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model elasticache-access`

**Syntax**

```text
apiforge model elasticache-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model eventbridge`

**Syntax**

```text
apiforge model eventbridge <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model eventbridge-access`

**Syntax**

```text
apiforge model eventbridge-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | AWS EventBridge |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model gatling`

**Syntax**

```text
apiforge model gatling <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Gatling global_stats.json or report dir. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model gitleaks`

**Syntax**

```text
apiforge model gitleaks <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | gitleaks report JSON. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model graph-access`

Graph call sites (Gremlin/openCypher/SPARQL) + GraphAccessIR and domain sketch.

**Syntax**

```text
apiforge model graph-access <path> [vendor] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan. |
| `vendor` | no | — | neptune|neo4j (default: both). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model graph-explain`

Parse a Neptune/Neo4j plan dump into GraphPlanIR + data.graph.plan facts.

**Syntax**

```text
apiforge model graph-explain <path> [fmt] [synthetic] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | One explain/profile dump file. |
| `fmt` | no | — | Plan format (auto-detected). |
| `synthetic` | no | — | Mark the plan as synthetic. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model graphql`

**Syntax**

```text
apiforge model graphql <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | GraphQL SDL schema file. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model hey`

**Syntax**

```text
apiforge model hey <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | hey -o csv export. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model iam-role`

**Syntax**

```text
apiforge model iam-role <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model jfr`

**Syntax**

```text
apiforge model jfr <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | jfr print --json output. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model jmeter`

**Syntax**

```text
apiforge model jmeter <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | JMeter JTL CSV. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model k6`

**Syntax**

```text
apiforge model k6 <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | k6 --summary-export JSON. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model kafka-access`

**Syntax**

```text
apiforge model kafka-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for Kafka producer/consumer access. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model kinesis-access`

**Syntax**

```text
apiforge model kinesis-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | AWS Kinesis |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model kms`

**Syntax**

```text
apiforge model kms <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model lambda`

Read a Lambda dump into facts — offline, no credentials.

**Syntax**

```text
apiforge model lambda <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from collect lambda. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model locust`

**Syntax**

```text
apiforge model locust <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Locust --csv stats export. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model mongo`

**Syntax**

```text
apiforge model mongo <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model msk`

**Syntax**

```text
apiforge model msk <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model msk-access`

**Syntax**

```text
apiforge model msk-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for Kafka access declared for Amazon MSK. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model mysql-access`

**Syntax**

```text
apiforge model mysql-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model nats-access`

**Syntax**

```text
apiforge model nats-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for NATS access. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model neo4j-access`

**Syntax**

```text
apiforge model neo4j-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model neptune`

**Syntax**

```text
apiforge model neptune <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model neptune-access`

**Syntax**

```text
apiforge model neptune-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model opensearch-access`

**Syntax**

```text
apiforge model opensearch-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | OpenSearch/Elasticsearch |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model otel`

OTel export -> perf.otel.* facts + a PerformanceRun — offline.

**Syntax**

```text
apiforge model otel <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | OTLP/JSON trace export from an OTel collector. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model pact`

**Syntax**

```text
apiforge model pact <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Pact contract JSON file. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model postgres-access`

**Syntax**

```text
apiforge model postgres-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model pprof`

**Syntax**

```text
apiforge model pprof <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | go tool pprof -top text. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model proto`

Extract gRPC services/messages from .proto — no protoc, offline.

**Syntax**

```text
apiforge model proto <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Directory of *.proto files. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model pulsar-access`

**Syntax**

```text
apiforge model pulsar-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for Apache Pulsar access. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model pyroscope`

**Syntax**

```text
apiforge model pyroscope <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Pyroscope flamebearer JSON. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model pytest-benchmark`

**Syntax**

```text
apiforge model pytest-benchmark <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | pytest-benchmark --benchmark-json. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model rabbitmq-access`

**Syntax**

```text
apiforge model rabbitmq-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for RabbitMQ access. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model rds-access`

**Syntax**

```text
apiforge model rds-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model redis`

Static extraction of Redis/Valkey call sites + DataAccessIR — offline.

**Syntax**

```text
apiforge model redis <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for Redis/Valkey calls. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model redshift-access`

**Syntax**

```text
apiforge model redshift-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Amazon Redshift |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model resilience`

Static resilience scan (timeouts, retries, pools, breaker/shutdown/
idempotency declarations) — heuristic, blind spots named.

**Syntax**

```text
apiforge model resilience <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Project directory to scan for resilience signals. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model s3`

**Syntax**

```text
apiforge model s3 <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model sam`

Extract AWS::Serverless::* resources — intrinsics become named diagnostics.

**Syntax**

```text
apiforge model sam <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | SAM template.yaml. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model schemathesis`

**Syntax**

```text
apiforge model schemathesis <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Schemathesis JSON report. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model secrets`

**Syntax**

```text
apiforge model secrets <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model semgrep`

**Syntax**

```text
apiforge model semgrep <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Semgrep --json output. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model sns`

**Syntax**

```text
apiforge model sns <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model sns-access`

**Syntax**

```text
apiforge model sns-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | AWS SNS |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model sqs`

**Syntax**

```text
apiforge model sqs <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model sqs-access`

**Syntax**

```text
apiforge model sqs-access <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | AWS SQS |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model stepfunctions`

**Syntax**

```text
apiforge model stepfunctions <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model terraform`

Extract API Gateway + Lambda resources from HCL — offline, no terraform.

**Syntax**

```text
apiforge model terraform <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Directory of *.tf files. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model trivy`

**Syntax**

```text
apiforge model trivy <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | trivy --format json output. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model vegeta`

**Syntax**

```text
apiforge model vegeta <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | vegeta report -type=json. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model vpc-endpoints`

**Syntax**

```text
apiforge model vpc-endpoints <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model waf`

**Syntax**

```text
apiforge model waf <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model wrk`

**Syntax**

```text
apiforge model wrk <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | wrk stdout summary text. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model xray`

**Syntax**

```text
apiforge model xray <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | Dump directory from `collect`. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model zap`

**Syntax**

```text
apiforge model zap <path> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `path` | yes | — | OWASP ZAP JSON report. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## next-step

### `next-step`

Recommend the specialist agent for the dominant finding area.

**Syntax**

```text
apiforge next-step <findings> <phase> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `findings` | yes | — | findings.json produced by analyze or judge. |
| `phase` | yes | — | Canonical SDD phase. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## observability

### `observability`

Offline-first OTel, Datadog and Dynatrace control plane.

**Syntax**

```text
apiforge observability
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability capabilities`

Show provider capabilities without credentials.

**Syntax**

```text
apiforge observability capabilities [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability credential-check`

Validate credential metadata without reading environment or secret stores.

**Syntax**

```text
apiforge observability credential-check <provider> <reference> [source] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `provider` | yes | — | — |
| `reference` | yes | — | Secret reference name; never a secret value. |
| `source` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability health`

Correlate telemetry and SLO evidence into an incident-ready health view.

**Syntax**

```text
apiforge observability health <source> <service> [slo] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | OTel-compatible JSON fixture. |
| `service` | yes | — | — |
| `slo` | no | — | SLO JSON definition. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability ingest`

Normalize a fixture and compute signals without external access.

**Syntax**

```text
apiforge observability ingest <source> [service] [slo] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `source` | yes | — | OTel-compatible JSON fixture. |
| `service` | no | — | — |
| `slo` | no | — | SLO JSON definition. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability instrument`

Recommend OTel instrumentation for Java, Go or Python.

**Syntax**

```text
apiforge observability instrument <language> [framework] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `language` | yes | — | — |
| `framework` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability read-plan`

Create a vendor read plan without credentials or network access.

**Syntax**

```text
apiforge observability read-plan <provider> <service> <start> <end> [environment] [signal] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `provider` | yes | — | otel, datadog, dynatrace or cloudwatch. |
| `service` | yes | — | — |
| `start` | yes | — | ISO-8601 start. |
| `end` | yes | — | ISO-8601 end. |
| `environment` | no | — | — |
| `signal` | no | — | traces, metrics, logs or events. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## perf

### `perf`

Compose over measured runs — compare, never interpolate.

**Syntax**

```text
apiforge perf
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf chaos`

List the declared controlled failure-injection scenarios (CHAOS-001..013).

Each scenario names the fault, the expected signal, the blast-radius
guard and the evidence a run must produce — injection itself is never
executed by API Forge.

**Syntax**

```text
apiforge perf chaos [limit] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `limit` | no | — | Bound carried scenarios. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf compare`

compare_runs / detect_regression over two PerformanceRun payloads.

**Syntax**

```text
apiforge perf compare <baseline> <candidate> [threshold_pct] [min_samples] [repeat_baseline] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `baseline` | yes | — | PerformanceRun JSON (or `model otel` payload). |
| `candidate` | yes | — | PerformanceRun JSON (or `model otel` payload). |
| `threshold_pct` | no | — | Regression threshold — declared, never assumed. |
| `min_samples` | no | — | Minimum span count per operation to be judged. |
| `repeat_baseline` | no | — | Dir of repeated baseline runs — measures the noise floor. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf memory`

Append-only PerformanceRun memory — local store.

**Syntax**

```text
apiforge perf memory
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf memory add`

Append a run to .apiforge/perf/runs.jsonl — payload hash recorded.

**Syntax**

```text
apiforge perf memory add <run> [root] [recorded_at] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run` | yes | — | PerformanceRun JSON to persist. |
| `root` | no | — | Workspace root. |
| `recorded_at` | no | — | Explicit timestamp; the only clock source. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf memory search`

search_performance_memory — filters declared fields, never infers.

**Syntax**

```text
apiforge perf memory search [subject] [tool] [since] [root] [limit] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `subject` | no | — | — |
| `tool` | no | — | — |
| `since` | no | — | ISO-8601 lower bound on recorded_at. |
| `root` | no | — | Workspace root. |
| `limit` | no | — | Bound carried runs; count stays the real total. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf plan`

Create a declarative load plan; generation never executes a tool.

**Syntax**

```text
apiforge perf plan <subject> <endpoint> <target_tps> [test_kind] [duration_s] [max_p99_ms] [max_error_rate] [generator] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `subject` | yes | — | — |
| `endpoint` | yes | — | — |
| `target_tps` | yes | — | — |
| `test_kind` | no | — | — |
| `duration_s` | no | — | — |
| `max_p99_ms` | no | — | — |
| `max_error_rate` | no | — | — |
| `generator` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf scenario`

Generate the tool's script for a declared scenario — never executes it.

**Syntax**

```text
apiforge perf scenario <tool> <scenario> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `tool` | yes | — | k6 | jmeter | locust. |
| `scenario` | yes | — | Declared scenario JSON (endpoints, rps, duration). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf suggest`

suggest_fix — emits an ActionPlan; never applies it.

**Syntax**

```text
apiforge perf suggest [case] [findings] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case` | no | — | Case dir — reads findings.json inside it. |
| `findings` | no | — | Findings JSON (list or {findings: []}). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf verdict`

passed / failed / inconclusive over a run — conditions named, never guessed.

**Syntax**

```text
apiforge perf verdict <run> [repeat_baseline] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run` | yes | — | PerformanceRun JSON (or `model otel` payload). |
| `repeat_baseline` | no | — | Dir of repeated baseline runs — deltas inside the measured noise floor make the verdict inconclusive. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## plan

### `plan`

Planning verbs — compose over facts other verbs already extracted.

**Syntax**

```text
apiforge plan
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `plan architecture`

Architecture Decision Engine — rank AWS primitives per role.

Eliminates on declared hard constraints, scores survivors on the
profile, and emits chosen + rejected-with-reason + change conditions.

**Syntax**

```text
apiforge plan architecture <profile> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `profile` | yes | — | WorkloadProfile JSON — every field declared. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `plan strangler`

Per-route strangler cut plan over two code inventories.

**Syntax**

```text
apiforge plan strangler <baseline> <candidate> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `baseline` | yes | — | facts.json from the legacy surface. |
| `candidate` | yes | — | facts.json from the new implementation. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## platform

### `platform`

Run allowlisted local runtime probes for platform verticals.

**Syntax**

```text
apiforge platform
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `platform verify-runtime`

Execute committed probes and emit local runtime evidence.

**Syntax**

```text
apiforge platform verify-runtime [root] [vertical] [now] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `vertical` | no | — | — |
| `now` | no | — | Explicit ISO-8601 observation time. |
| `out` | no | — | Optional runtime receipt path. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## playbook

### `playbook`

Render the declared executor decomposition for a coordinator.

The floor on every platform — works without dispatch.

**Syntax**

```text
apiforge playbook <coordinator> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `coordinator` | yes | — | Coordinator profile name. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## policy

### `policy`

Evaluate actions against the policy catalog.

**Syntax**

```text
apiforge policy
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `policy check`

Decide whether an action is allowed, gated or denied.

**Syntax**

```text
apiforge policy check <verb> [action_class] [args] [target] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `verb` | yes | — | Action verb, e.g. fs.delete. |
| `action_class` | no | — | Declared autonomy class. |
| `args` | no | — | Positional arguments. |
| `target` | no | — | Action target. |
| `policy` | no | — | Policy YAML; defaults to the packaged catalog. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## report

### `report`

Release evidence bundle — sign binds hashes; verify names what diverged.

**Syntax**

```text
apiforge report
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `report build`

Compose the release evidence bundle for a case.

**Syntax**

```text
apiforge report build <case_dir> [receipt] [now] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `case_dir` | yes | — | Persisted case directory. |
| `receipt` | no | — | evidence receipt JSON to pin into the bundle. |
| `now` | no | — | Explicit ISO8601 (only clock). |
| `out` | no | — | Write report.json here. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `report keygen`

Generate an Ed25519 keypair — proves key possession, never identity.

**Syntax**

```text
apiforge report keygen <name> [keys_dir] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `name` | yes | — | Key name (writes <name>.pem). |
| `keys_dir` | no | — | Directory holding PEM keys. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `report sign`

Append the signature block binding body/evidence/catalog hashes.

**Syntax**

```text
apiforge report sign <report> [key] [out] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `report` | yes | — | report.json to sign. |
| `key` | no | — | Ed25519 private PEM — adds cryptographic binding. |
| `out` | no | — | Write signed report here. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `report verify`

Name which part diverged: signature_version|body|evidence|catalog|signature_crypto.

**Syntax**

```text
apiforge report verify <report> [receipt] [pubkey] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `report` | yes | — | signed report.json. |
| `receipt` | no | — | receipt file to re-hash for the evidence check. |
| `pubkey` | no | — | Ed25519 public PEM to verify signature_b64. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## resume

### `resume`

Resume only persisted, eligible work from the latest control run.

**Syntax**

```text
apiforge resume <task_id> [root] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | TaskSpec id to resume. |
| `root` | no | — | — |
| `policy` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## review

### `review`

Render the canonical Outcome Brief for a runtime run.

**Syntax**

```text
apiforge review <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | TaskSpec id to review. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## route

### `route`

Model routing: candidates, scorecards and lifecycle promotion.

**Syntax**

```text
apiforge route
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `route model`

§33: rank declared model candidates; quality history is a constraint.

**Syntax**

```text
apiforge route model <inputs> [scorecards] [task_class] [shadow_root] [legacy_selected] [policy] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `inputs` | yes | — | ModelRouteInputs JSON or file. |
| `scorecards` | no | — | ModelEvaluation JSONL or scorecards JSON file. |
| `task_class` | no | — | — |
| `shadow_root` | no | — | Record candidate vs legacy in Decision Plane shadow mode. |
| `legacy_selected` | no | — | — |
| `policy` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `route promote`

§35: lifecycle promotion gated on scorecard evidence, not benchmarks.

**Syntax**

```text
apiforge route promote [route] <evidence> [approval] [evaluations] [task_class] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `route` | no | — | — |
| `evidence` | yes | — | PromotionEvidence JSON. |
| `approval` | no | — | — |
| `evaluations` | no | — | ModelEvaluation JSONL proving real traffic |
| `task_class` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `route scorecard`

§34: fold evaluation rows into scorecards per provider/model/class.

**Syntax**

```text
apiforge route scorecard <evaluations> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `evaluations` | yes | — | ModelEvaluation JSONL. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## rules

### `rules`

Read the rule catalog — the knowledge base every finding cites.

**Syntax**

```text
apiforge rules
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `rules list`

List rule ids, titles and severities by area.

**Syntax**

```text
apiforge rules list [area] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `area` | no | — | Filter by catalog area. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `rules lookup`

Print one rule's full guidance.

**Syntax**

```text
apiforge rules lookup <rule_id> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `rule_id` | yes | — | Rule id, e.g. AF-SEC-001. |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## run

### `run`

Execute allowlisted scanner binaries, then read their reports.

**Syntax**

```text
apiforge run
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `run list`

The tool registry — declared metadata plus *measured* install status.

**Syntax**

```text
apiforge run list [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `run tool`

Execute a scanner binary (fixed argv, no shell) and read its report.

**Syntax**

```text
apiforge run tool <tool> <target> <out> [config] [timeout] [dry_run] [approve] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `tool` | yes | — | Allowlisted tool: semgrep|trivy|gitleaks|k6. |
| `target` | yes | — | Path the tool scans. |
| `out` | yes | — | Report file the tool writes. |
| `config` | no | — | Tool config (semgrep requires a local rules path). |
| `timeout` | no | — | Seconds before the run is refused. |
| `dry_run` | no | — | Print argv; execute nothing. |
| `approve` | no | — | Approval reference required when a load script targets a remote or unresolvable URL (policy gate `sensitive`). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## runtime

### `runtime`

Bounded agentic execution over sealed TaskSpecs; local and CI safe.

**Syntax**

```text
apiforge runtime
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime approve`

Record a local human approval artifact for a runtime run.

**Syntax**

```text
apiforge runtime approve <task_id> <run_id> <approver> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `run_id` | yes | — | — |
| `approver` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime checkpoint`

Budget a run already spent, as a resume will continue it.

**Syntax**

```text
apiforge runtime checkpoint <task_id> <run_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `run_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime control-cancel`

Cancel a control-plane run and persist the actor.

**Syntax**

```text
apiforge runtime control-cancel <run_id> <actor> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `actor` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime control-complete`

Complete a running step with a content-hashed result.

**Syntax**

```text
apiforge runtime control-complete <run_id> <step_id> [result_json] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `step_id` | yes | — | — |
| `result_json` | no | — | JSON result payload. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime control-create`

Create a persistent control-plane run without executing work.

**Syntax**

```text
apiforge runtime control-create <task_id> <step> [root] [max_parallel] [max_calls] [max_retries] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `step` | yes | — | Step or step=dependency1,dependency2; repeatable. |
| `root` | no | — | — |
| `max_parallel` | no | — | — |
| `max_calls` | no | — | — |
| `max_retries` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime control-plan`

Show ready steps and dynamic parallel width.

**Syntax**

```text
apiforge runtime control-plan <run_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime control-review`

Close a completed plan through an independent review verdict.

**Syntax**

```text
apiforge runtime control-review <run_id> <reviewer> [verdict] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `reviewer` | yes | — | — |
| `verdict` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime control-start`

Claim one ready step and consume one bounded call.

**Syntax**

```text
apiforge runtime control-start <run_id> <step_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `run_id` | yes | — | — |
| `step_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime debate`

Request a debate room before the runtime makes a final decision.

**Syntax**

```text
apiforge runtime debate <task_id> [root] [policy] [profile] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `policy` | no | — | — |
| `profile` | no | — | Economy profile: economy|balanced|deep (risk may escalate). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime resume`

Resume by replaying the TaskSpec through the bounded supervisor.

**Syntax**

```text
apiforge runtime resume <task_id> [root] [policy] [profile] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `policy` | no | — | — |
| `profile` | no | — | Economy profile: economy|balanced|deep (risk may escalate). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime run`

Execute a sealed TaskSpec with the deterministic fake adapter.

**Syntax**

```text
apiforge runtime run <task_id> [root] [policy] [now] [debate] [profile] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | TaskSpec id to execute. |
| `root` | no | — | Project root. |
| `policy` | no | — | — |
| `now` | no | — | Deterministic timestamp for replay. |
| `debate` | no | — | Request a debate room. |
| `profile` | no | — | Economy profile: economy|balanced|deep (risk may escalate). |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime semantic-checkpoint`

**Syntax**

```text
apiforge runtime semantic-checkpoint <state_file> <task_id> <run_id> <now> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `state_file` | yes | — | JSON object matching SemanticCheckpoint fields. |
| `task_id` | yes | — | — |
| `run_id` | yes | — | — |
| `now` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime status`

Show the newest persisted runtime run.

**Syntax**

```text
apiforge runtime status <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime telemetry-collector-check`

§52 POST the payload to a real collector and count accepted spans.

**Syntax**

```text
apiforge runtime telemetry-collector-check <endpoint> [otlp] [output_file] [timeout_s] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `endpoint` | yes | — | OTLP/HTTP base URL. |
| `otlp` | no | — | Payload file; defaults to the local ledger. |
| `output_file` | no | — | — |
| `timeout_s` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime telemetry-export`

§50 export local spans as one OTLP ExportTraceServiceRequest body.

**Syntax**

```text
apiforge runtime telemetry-export [out] [service_name] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `out` | no | — | Write OTLP JSON to this file. |
| `service_name` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime telemetry-ids`

§51 emit the standardized correlation id set (+ W3C traceparent).

**Syntax**

```text
apiforge runtime telemetry-ids [task_id] [run_id] [trace_id] [span_id] [agent_id] [model_call_id] [tool_call_id] [decision_id] [memory_id] [context_id] [issue_trace] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | no | — | — |
| `run_id` | no | — | — |
| `trace_id` | no | — | — |
| `span_id` | no | — | — |
| `agent_id` | no | — | — |
| `model_call_id` | no | — | — |
| `tool_call_id` | no | — | — |
| `decision_id` | no | — | — |
| `memory_id` | no | — | — |
| `context_id` | no | — | — |
| `issue_trace` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime telemetry-query`

Query local agent/tool spans without contacting an exporter.

**Syntax**

```text
apiforge runtime telemetry-query [task_id] [run_id] [trace_id] [operation] [status] [max_results] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | no | — | — |
| `run_id` | no | — | — |
| `trace_id` | no | — | — |
| `operation` | no | — | — |
| `status` | no | — | — |
| `max_results` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime telemetry-span`

Append one sanitized local agent/tool span.

**Syntax**

```text
apiforge runtime telemetry-span <trace_id> <task_id> <run_id> <operation> <started_at> [agent_name] [tool_name] [agent_id] [model_call_id] [tool_call_id] [decision_id] [memory_id] [context_id] [parent_span_id] [ended_at] [status] [status_message] [attributes] [event] [link] [evidence] [unresolved] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `trace_id` | yes | — | — |
| `task_id` | yes | — | — |
| `run_id` | yes | — | — |
| `operation` | yes | — | — |
| `started_at` | yes | — | — |
| `agent_name` | no | — | — |
| `tool_name` | no | — | — |
| `agent_id` | no | — | — |
| `model_call_id` | no | — | — |
| `tool_call_id` | no | — | — |
| `decision_id` | no | — | — |
| `memory_id` | no | — | — |
| `context_id` | no | — | — |
| `parent_span_id` | no | — | — |
| `ended_at` | no | — | — |
| `status` | no | — | — |
| `status_message` | no | — | — |
| `attributes` | no | — | JSON object or JSON file. |
| `event` | no | — | — |
| `link` | no | — | — |
| `evidence` | no | — | — |
| `unresolved` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime telemetry-validate`

§52 deterministic structural acceptance of an OTLP payload.

**Syntax**

```text
apiforge runtime telemetry-validate <otlp> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `otlp` | yes | — | OTLP/JSON payload file. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## sandbox

### `sandbox`

Copy-based sandbox evaluation.

**Syntax**

```text
apiforge sandbox
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sandbox apply`

Apply a diff to copies of the tree and report the finding delta.

**Syntax**

```text
apiforge sandbox apply <root> <diff> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | yes | — | Project root to copy. |
| `diff` | yes | — | Unified diff file. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sandbox clean`

Remove .apiforge/sandbox and report removed ids.

**Syntax**

```text
apiforge sandbox clean <root> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | yes | — | Project root. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## sdd

### `sdd`

Spec-driven development artifacts and gates.

**Syntax**

```text
apiforge sdd
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd check`

Validate the SDD hash cascade and phase metadata.

**Syntax**

```text
apiforge sdd check <root> [feature] [strict] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | yes | — | SDD artifacts root. |
| `feature` | no | — | Single feature. |
| `strict` | no | — | Gaps refuse. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd classify`

Classify change risk deterministically and name the minimum SDD profile.

**Syntax**

```text
apiforge sdd classify [description] [path] [baseline] [candidate] [protocol] [repositories] [write] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `description` | no | — | Change description. |
| `path` | no | — | Touched path (repeatable). |
| `baseline` | no | — | Baseline contract. |
| `candidate` | no | — | Candidate contract. |
| `protocol` | no | — | openapi or grpc. |
| `repositories` | no | — | Repos touched. |
| `write` | no | — | Feature dir: record risk_class in intent.md frontmatter. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd evidence`

Write evidence/<kind>.json derived from a real artifact — no overrides.

**Syntax**

```text
apiforge sdd evidence <root> <feature> <kind> <source> <now> [state_dir] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | yes | — | SDD artifacts root. |
| `feature` | yes | — | — |
| `kind` | yes | — | Gate evidence kind. |
| `source` | yes | — | Artifact the evidence derives from. |
| `now` | yes | — | Explicit ISO8601 timestamp. |
| `state_dir` | no | — | Feature state dir (defaults to .apiforge/sdd/<F>). |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd set-phase`

Transition a phase; under --strict, gates require evidence or override.

**Syntax**

```text
apiforge sdd set-phase <root> <feature> <phase> <status> [strict] [override_gate] [override_reason] [override_actor] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | yes | — | SDD artifacts root. |
| `feature` | yes | — | — |
| `phase` | yes | — | — |
| `status` | yes | — | — |
| `strict` | no | — | — |
| `override_gate` | no | — | — |
| `override_reason` | no | — | — |
| `override_actor` | no | — | — |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd stamp`

Write the upstream sha256 into an artifact's frontmatter.

**Syntax**

```text
apiforge sdd stamp <artifact> <upstream> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `artifact` | yes | — | Phase artifact. |
| `upstream` | yes | — | Upstream artifact. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd status`

Summarize per-feature phase status.

**Syntax**

```text
apiforge sdd status <root> [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | yes | — | SDD artifacts root. |
| `detail_level` | no | — | Payload level. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## slice

### `slice`

Failures and signatures instead of whole logs; the full log stays behind ctx://.

**Syntax**

```text
apiforge slice
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `slice log`

Deduplicated failure signatures with frames, preceding context and environment.

**Syntax**

```text
apiforge slice log <input_path> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `input_path` | yes | — | CI or build log. |
| `root` | no | — | Where the full log is stored. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `slice tests`

Counts plus every failing test with file:line and assertion.

**Syntax**

```text
apiforge slice tests <input_path> [fmt] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `input_path` | yes | — | pytest output or JUnit XML. |
| `fmt` | no | — | auto|pytest|junit. |
| `root` | no | — | Where the full log is stored. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## status

### `status`

Show TaskSpec status, or project/workspace status when no task is supplied.

**Syntax**

```text
apiforge status [task_id] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | no | — | TaskSpec id, or omit for project status. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## task

### `task`

Sealed, budgeted units of agentic work (TaskSpec).

**Syntax**

```text
apiforge task
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task accept`

Accept a supervised run; the acceptor must differ from the executor.

**Syntax**

```text
apiforge task accept <task_id> <by> [evidence] [notes] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `by` | yes | — | Acceptor — never the executor. |
| `evidence` | no | — | — |
| `notes` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task compile`

Compile a local API intention into a verified TaskSpec draft.

**Syntax**

```text
apiforge task compile <task_id> <outcome> <contract> <project> <case> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `outcome` | yes | — | — |
| `contract` | yes | — | — |
| `project` | yes | — | — |
| `case` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task create`

Create a task in draft; sealed only after review.

**Syntax**

```text
apiforge task create <task_id> <outcome> [spec_file] [input_] [writable] [strategy] [risk] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | Task id (lowercase, digits, hyphens). |
| `outcome` | yes | — | The single outcome. |
| `spec_file` | no | — | YAML/JSON TaskSpec to load instead of flags. |
| `input_` | no | — | field=path-or-value (project, contract, findings…) |
| `writable` | no | — | Writable path glob. |
| `strategy` | no | — | Recipe name. |
| `risk` | no | — | Action class. |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task holdout`

Run deterministic local mutations and report whether proofs detect them.

**Syntax**

```text
apiforge task holdout <project> <contract> <manifest> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `project` | yes | — | — |
| `contract` | yes | — | — |
| `manifest` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task plan`

Bind a sealed TaskSpec to a closed persisted TaskPlan.

**Syntax**

```text
apiforge task plan <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task reject`

Reject a supervised run back to reviewable state.

**Syntax**

```text
apiforge task reject <task_id> <by> <reason> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `by` | yes | — | — |
| `reason` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task review`

Mark reviewed — any --set change bumps the revision, voiding seals.

**Syntax**

```text
apiforge task review <task_id> <by> [set_] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `by` | yes | — | Reviewer identity. |
| `set_` | no | — | scalar field=value changes |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task run`

Run the recipe within budgets; ends awaiting supervision or named stop.

**Syntax**

```text
apiforge task run <task_id> <by> [now] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `by` | yes | — | Executor identity. |
| `now` | no | — | ISO8601 (only clock). |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task seal`

Seal the current revision — key possession, never identity.

**Syntax**

```text
apiforge task seal <task_id> <key> <by> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `key` | yes | — | Ed25519 private PEM. |
| `by` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task status`

Task spec plus its append-only history.

**Syntax**

```text
apiforge task status <task_id> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task verify`

Run independent proof checks and persist a VerificationRecord.

**Syntax**

```text
apiforge task verify <task_id> <project> <contract> [manifest] [run_id] [by] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | — |
| `project` | yes | — | — |
| `contract` | yes | — | — |
| `manifest` | no | — | — |
| `run_id` | no | — | — |
| `by` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | Payload level: summary|normal|full. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## tui

### `tui`

Execution-first terminal UX with a Rich/JSON fallback.

**Syntax**

```text
apiforge tui <task_id> [root] [fallback]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `task_id` | yes | — | TaskSpec id to inspect or execute. |
| `root` | no | — | Project root. |
| `fallback` | no | — | Force headless projection. |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## verify

### `verify`

Targeted verification plans (never executes).

**Syntax**

```text
apiforge verify
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `verify escalate`

Next verification step: static -> test -> stop; runtime read-only only if inconclusive.

**Syntax**

```text
apiforge verify escalate [static] [test] [test_slice] [runtime] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `static` | no | — | missing|likely|clear|inconclusive |
| `test` | no | — | missing|passed|failed|inconclusive |
| `test_slice` | no | — | TestSlice/v1 JSON. |
| `runtime` | no | — | missing|confirmed|clear|inconclusive |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `verify plan`

Ladder level for the risk plus the impacted tests and the commands to run them.

**Syntax**

```text
apiforge verify plan [changed] [risk] [breaking] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `changed` | no | — | Changed file (repeatable). |
| `risk` | no | — | micro|low|medium|high (sdd classify). |
| `breaking` | no | — | Contract verdict is breaking. |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

## workspace

### `workspace`

Register independent repositories in a local virtual workspace.

**Syntax**

```text
apiforge workspace
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace add`

**Syntax**

```text
apiforge workspace add <repository> [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `repository` | yes | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace discover`

**Syntax**

```text
apiforge workspace discover [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace graph`

Workspace graph; declared relations only unless --infer is passed.

**Syntax**

```text
apiforge workspace graph [root] [infer] [run_id] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `infer` | no | — | Add static cross-repo inferred relations (opt-in, audited). |
| `run_id` | no | — | Attribute inference to a run; field records detect it. |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace init`

**Syntax**

```text
apiforge workspace init [root] [name] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `name` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace locality`

Target repo first, direct neighbors next, transitive only on request.

**Syntax**

```text
apiforge workspace locality <target> [transitive] [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `target` | yes | — | Repository name or id. |
| `transitive` | no | — | — |
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace status`

**Syntax**

```text
apiforge workspace status [root] [detail_level]
```

| argument/flag | required | default | description |
|---|---|---|---|
| `root` | no | — | — |
| `detail_level` | no | — | — |

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->
