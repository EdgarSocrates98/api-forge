# `apiforge` command reference

Generated from the real CLI parser by `doc_inventory.py` + `doc_reference.py`. Do not hand-edit generated sections — write between `keep:start`/`keep:end` markers. `por que`/`quando` lines come from the curated `command-rationale.json` — edit rationale there, never here. Status vocabulary: `available` unless marked otherwise.

Rationale coverage: **67/67** first-level groups curated in `command-rationale.json`.

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

**para que:** Host-neutral Caveman/RTK protocols, workflows and adapters.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

**Syntax**

```text
apiforge agentops
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agentops activation-plan`

**para que:** Build a host activation plan; no host configuration is mutated.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** §55 deterministic a/b over quality/tokens/cost/latency/context/evidence/tools/agents.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** List closed command filters used by the RTK adapter.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** List host adapters for Claude, GPT/Codex, Devin and Copilot.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** §53–§54 sectioned report for one run; sections never drop silently.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Inspect repository-native Caveman/Cavekit assets and RTK configuration.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Resolve a capability intersection from local host declarations.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Audit host discovery and capability parity without invoking a host.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Declared economical projection for a host, with measured surface bytes.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Stable prompt prefix (hashed) and the run-specific suffix.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Render ordered ledger/span/token events with missing-order evidence.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Inspect one Tool Adapter contract.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** List typed Tool Adapters and their safety/evidence metadata.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** §56–§57 waste detector; every finding labeled observed/estimated/hypothesis.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Render one workflow plan; execution remains governed by TaskSpec.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** List deterministic Caveman-inspired API workflows.

- **por que:** protocolos host-neutral Caveman/RTK, workflows e adapters
- **quando usar:** operações do runtime agêntico que cruzam hosts

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

**para que:** Publish coordinator profiles to host-native mirrors.

- **por que:** publica perfis de coordenadores para mirrors nativos dos hosts
- **quando usar:** sincronizar/inspecionar o roster de agentes — mirror nunca é editado à mão

**Syntax**

```text
apiforge agents
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `agents audit`

**para que:** Anti-agentic-theater gate: unique capability/expertise/validator/tool/decision role.

- **por que:** publica perfis de coordenadores para mirrors nativos dos hosts
- **quando usar:** sincronizar/inspecionar o roster de agentes — mirror nunca é editado à mão

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

**para que:** Report render drift for all three hosts — the release gate fails on the same check.

- **por que:** publica perfis de coordenadores para mirrors nativos dos hosts
- **quando usar:** sincronizar/inspecionar o roster de agentes — mirror nunca é editado à mão

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

**para que:** Agent contract lint: sections, word budget, English, description, access, owned tools.

- **por que:** publica perfis de coordenadores para mirrors nativos dos hosts
- **quando usar:** sincronizar/inspecionar o roster de agentes — mirror nunca é editado à mão

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

**para que:** Every agent name in rules/code/tests/evals is a coordinator or an active alias.

- **por que:** publica perfis de coordenadores para mirrors nativos dos hosts
- **quando usar:** sincronizar/inspecionar o roster de agentes — mirror nunca é editado à mão

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

**para que:** Render `.agents/agents/`, `.claude/agents/` and `.codex/agents/` from `agents/*.md`.

- **por que:** publica perfis de coordenadores para mirrors nativos dos hosts
- **quando usar:** sincronizar/inspecionar o roster de agentes — mirror nunca é editado à mão

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

**para que:** Run the full deterministic slice and persist a case.

- **por que:** roda a fatia determinística completa e persiste um case
- **quando usar:** primeira passada num projeto antes de judge/next-step

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

**para que:** Autonomy modes (observe->continuous) and runbooks on the policy engine.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

**Syntax**

```text
apiforge autonomy
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `autonomy heal`

**para que:** Self-healing pipeline: detect->explain->propose->authorize->execute->
verify->compare->accept|rollback. Every transition is policy-decided and
ledgered; rollback restores the snapshot of --writable-path files.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

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

**para que:** Read the append-only autonomy ledger.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

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

**para que:** Evaluate one action under the current mode; execute only on allow.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

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

**para que:** Run a runbook under the current mode — halting is mode-defined.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

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

**para que:** Change the autonomy mode — itself a policy-gated action.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

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

**para que:** Current mode, who set it, and the ledger size.

- **por que:** modos de autonomia (observe→continuous) e runbooks no policy engine
- **quando usar:** entender/subir o nível de autonomia com política explícita

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

**para que:** Structured append-only shared state.

- **por que:** estado compartilhado estruturado, append-only
- **quando usar:** ver o que os agentes já publicaram no case

**Syntax**

```text
apiforge blackboard
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `blackboard append`

- **por que:** estado compartilhado estruturado, append-only
- **quando usar:** ver o que os agentes já publicaram no case

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

- **por que:** estado compartilhado estruturado, append-only
- **quando usar:** ver o que os agentes já publicaram no case

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

**para que:** Outcome Briefs — DONE is refused while mandatory gaps exist.

- **por que:** Outcome Briefs — DONE é recusado enquanto houver gaps obrigatórios
- **quando usar:** fechar uma execução com evidência completa e gaps nomeados

**Syntax**

```text
apiforge brief
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `brief show`

**para que:** Render the Outcome Brief for a task — DONE is refused, not advised.

- **por que:** Outcome Briefs — DONE é recusado enquanto houver gaps obrigatórios
- **quando usar:** fechar uma execução com evidência completa e gaps nomeados

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

**para que:** Generate code skeletons — evaluated in the sandbox, promoted via worktree only.

- **por que:** gera esqueletos de código — avaliados em sandbox, promovidos só via worktree
- **quando usar:** scaffolding governado de código novo

**Syntax**

```text
apiforge build
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `build endpoint`

**para que:** Synthesize a Spring endpoint skeleton; main tree is never touched.

- **por que:** gera esqueletos de código — avaliados em sandbox, promovidos só via worktree
- **quando usar:** scaffolding governado de código novo

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

**para que:** Advisory layered cache — reuse only fresh evidence, invalidate by dependency.

- **por que:** cache em camadas, advisory — reusa só evidência fresca, invalida por dependência
- **quando usar:** inspecionar/limpar evidência cacheada

**Syntax**

```text
apiforge cache
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `cache invalidate`

**para que:** Drop only the capsule selections whose dependencies intersect the change set.

- **por que:** cache em camadas, advisory — reusa só evidência fresca, invalida por dependência
- **quando usar:** inspecionar/limpar evidência cacheada

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

**para que:** Entries, bytes, expired and corrupt counts per layer and tier, plus policies.

- **por que:** cache em camadas, advisory — reusa só evidência fresca, invalida por dependência
- **quando usar:** inspecionar/limpar evidência cacheada

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

**para que:** Inspect the evidence-backed public capability matrix.

- **por que:** matriz pública de capabilities com evidência por trás
- **quando usar:** perguntar o que a forja declara atender

**Syntax**

```text
apiforge capabilities
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `capabilities list`

**para que:** List public capabilities and their explicit support boundaries.

- **por que:** matriz pública de capabilities com evidência por trás
- **quando usar:** perguntar o que a forja declara atender

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

**para que:** Verify documentation, limitations and evidence requirements.

- **por que:** matriz pública de capabilities com evidência por trás
- **quando usar:** perguntar o que a forja declara atender

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

**para que:** Govern API, Git and CI/CD changes with read-only evidence.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

**Syntax**

```text
apiforge change-control
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `change-control collect`

**para que:** Collect GitHub context with a GET-only adapter into a replay bundle.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

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

**para que:** Publish the canonical result to JUnit, Markdown, SARIF and HTML.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

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

**para que:** Run analyze -> next-step -> graph -> evidence -> brief from a bundle.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

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

**para que:** Serve a local or authenticated TLS read-only UI and IDE bridge.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

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

**para que:** Export a canonical IDE/UI projection without changing its semantics.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

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

**para que:** Verify that a change-control result still references existing artifacts.

- **por que:** governa mudanças de API, Git e CI/CD com evidência read-only
- **quando usar:** revisar uma mudança antes de propor — mutação fica no host

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

**para que:** Collect AWS artifacts into offline dumps (the only family that touches AWS).

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

**Syntax**

```text
apiforge collect
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `collect alb`

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch one REST API's configuration into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch the user pool and its app clients into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch the bus, its rules and their targets into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch one role, its attached policies and inline policy documents.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch one Lambda function's configuration into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Read-only explain/profile over the neptunedata allowlist; receipt in manifest.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch one topic's attributes and subscriptions into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch one queue's attribute set into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch one WebACL's configuration into an offline dump.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Fetch X-Ray sampling rules and encryption config.

- **por que:** coleta artefatos AWS em dumps offline — única família que toca AWS
- **quando usar:** trazer evidência de runtime para análise offline

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

**para que:** Measured context accounting — the funnel, in bytes per stage.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

**Syntax**

```text
apiforge context
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `context capsule`

**para que:** Minimal sufficient evidence for one operation as ctx:// refs under a byte budget.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** Compact a command artifact while preserving critical evidence.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** What changed, which operations it impacts and which capsules to build — delta first.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** Return one ctx object after verifying its sha256.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** Measure what each case stage keeps — bytes, never claims.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** Expired/corrupt cache entries, orphan cache objects and unreferenced ctx objects.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** Measured context quality + minimum-sufficient decision for one capsule.

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

- **por que:** contabilidade de contexto medida — o funil, em bytes por estágio
- **quando usar:** montar contexto econômico para um agente/host

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

**para que:** List and inspect the canonical versioned contracts.

- **por que:** lista e inspeciona os contratos versionados canônicos
- **quando usar:** conferir o contrato antes de depender dele

**Syntax**

```text
apiforge contract
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `contract list`

**para que:** List the registered canonical contracts.

- **por que:** lista e inspeciona os contratos versionados canônicos
- **quando usar:** conferir o contrato antes de depender dele

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

**para que:** Emit the JSON schema of a canonical contract.

- **por que:** lista e inspeciona os contratos versionados canônicos
- **quando usar:** conferir o contrato antes de depender dele

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

**para que:** Unify contract impact analysis and build an offline API Digital Twin.

- **por que:** unifica análise de impacto de contrato e constrói o Digital Twin de API offline
- **quando usar:** avaliar impacto de mudança de contrato de ponta a ponta

**Syntax**

```text
apiforge contract-intel
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `contract-intel impact`

**para que:** Classify compatibility and expose affected contract references.

- **por que:** unifica análise de impacto de contrato e constrói o Digital Twin de API offline
- **quando usar:** avaliar impacto de mudança de contrato de ponta a ponta

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

**para que:** Create a no-network Digital Twin plan and optionally simulate a scenario.

- **por que:** unifica análise de impacto de contrato e constrói o Digital Twin de API offline
- **quando usar:** avaliar impacto de mudança de contrato de ponta a ponta

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

**para que:** Decision Control Plane lifecycle: shadow, assisted, active and fallback.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

**Syntax**

```text
apiforge control
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `control demote`

**para que:** §32: step a route back one stage — the safe direction is always open.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

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

**para que:** §29-§32: who governs this evaluation under the route's mode.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

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

**para que:** §30-§31: one lifecycle step; ACTIVE requires the five requirements.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

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

**para que:** §28: every declared route with its effective lifecycle mode.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

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

**para que:** §29: recorded parallel-run observations for a route.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

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

**para que:** §32: map declared signals to the closed trigger vocabulary.

- **por que:** ciclo de vida do Decision Control Plane: shadow, assisted, active, fallback
- **quando usar:** operar o plano de decisão governado

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

**para que:** Record specialist disagreement — positions cite fact_ids, a referee closes.

- **por que:** registra desacordo de especialistas — posições citam fact_ids, referee fecha
- **quando usar:** quando especialistas divergem sobre o caso

**Syntax**

```text
apiforge debate
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `debate close`

**para que:** Close as resolved (--decision) or unresolved (no --decision).

- **por que:** registra desacordo de especialistas — posições citam fact_ids, referee fecha
- **quando usar:** quando especialistas divergem sobre o caso

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

**para que:** Open a debate over a question with named sides.

- **por que:** registra desacordo de especialistas — posições citam fact_ids, referee fecha
- **quando usar:** quando especialistas divergem sobre o caso

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

**para que:** Referee input: shared capsule id + one position delta per side + disagreements.

- **por que:** registra desacordo de especialistas — posições citam fact_ids, referee fecha
- **quando usar:** quando especialistas divergem sobre o caso

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

**para que:** Append a position — every position must cite fact_id evidence.

- **por que:** registra desacordo de especialistas — posições citam fact_ids, referee fecha
- **quando usar:** quando especialistas divergem sobre o caso

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

**para que:** Generate and inspect offline-first payloads for Devin Desktop, CLI and Cloud.

- **por que:** payloads offline-first para Devin Desktop, CLI e Cloud
- **quando usar:** transportar a forja para hosts Devin

**Syntax**

```text
apiforge devin
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `devin capabilities`

**para que:** Report Devin capability declarations plus local CLI observation.

- **por que:** payloads offline-first para Devin Desktop, CLI e Cloud
- **quando usar:** transportar a forja para hosts Devin

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

**para que:** Create a Devin payload; this command never starts Devin or mutates Git.

- **por que:** payloads offline-first para Devin Desktop, CLI e Cloud
- **quando usar:** transportar a forja para hosts Devin

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

**para que:** Observe whether a local Devin CLI executable is available on PATH.

- **por que:** payloads offline-first para Devin Desktop, CLI e Cloud
- **quando usar:** transportar a forja para hosts Devin

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

**para que:** Diff OpenAPI contracts.

- **por que:** diff semântico de contratos OpenAPI
- **quando usar:** comparar duas versões de contrato com mudanças tipadas

**Syntax**

```text
apiforge diff
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `diff contract`

**para que:** Classify bounded breaking changes between two contracts.

- **por que:** diff semântico de contratos OpenAPI
- **quando usar:** comparar duas versões de contrato com mudanças tipadas

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

**para que:** Statically inventory FastAPI routes without executing code.

- **por que:** inventaria rotas FastAPI estaticamente, sem executar código
- **quando usar:** primeiro mapa de uma API desconhecida

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

**para que:** Run deterministic playbook steps; pending steps name their missing inputs.

- **por que:** executa passos de playbook determinísticos; pendentes nomeiam inputs faltantes
- **quando usar:** rodar um fluxo declarado passo a passo

**Syntax**

```text
apiforge dispatch
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `dispatch run`

**para que:** Run a coordinator's playbook; pending steps name their missing inputs.

- **por que:** executa passos de playbook determinísticos; pendentes nomeiam inputs faltantes
- **quando usar:** rodar um fluxo declarado passo a passo

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

**para que:** Inspect the installed package, paths and hostless capabilities.

- **por que:** inspeciona o pacote instalado, paths e capabilities hostless
- **quando usar:** verificar a distribuição instalada

**Syntax**

```text
apiforge distribution
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `distribution doctor`

- **por que:** inspeciona o pacote instalado, paths e capabilities hostless
- **quando usar:** verificar a distribuição instalada

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

- **por que:** inspeciona o pacote instalado, paths e capabilities hostless
- **quando usar:** verificar a distribuição instalada

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

- **por que:** inspeciona o pacote instalado, paths e capabilities hostless
- **quando usar:** verificar a distribuição instalada

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

- **por que:** inspeciona o pacote instalado, paths e capabilities hostless
- **quando usar:** verificar a distribuição instalada

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

**para que:** Inspect runtime state, or the local installation when no task is supplied.

- **por que:** inspeciona estado de runtime, ou a instalação local sem task
- **quando usar:** primeira linha de diagnóstico: ambiente, instalação, imports

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

**para que:** Measured cost per call — bytes recorded, tokens unresolved without a transcript.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

**Syntax**

```text
apiforge economy
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `economy budget-check`

**para que:** Check a proposed spend without appending it.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Register an immutable hierarchical budget plan.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Admit and append one measured spend receipt.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Price an accounting under the declared catalog; gaps stay named.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** What in this setup makes runs pay more than needed, with the unlock for each.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Why each ref of a run was spent, from recorded provenance rules only.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Per-basis token rollup for a run — observed and estimated never mix.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Profile envelope split across SDD phases; protected phases are never cut.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** List the declared pricing catalog — prices are never hardcoded.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Declared provider capabilities and deterministic capabilities.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** §22 estimated vs observed for a run, with calibration error per axis.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Append usage rows for a run; the file is append-only.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Aggregate recorded call sizes; detail_level_effect shows what summary saves.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Per extra capability: calls, facts and unresolved added, outcome changed vs primary.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Bytes attributed per run and source; tokens stay unresolved without a transcript.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Cheapest tier the evidence proves sufficient (T0-T3), with the reason.

- **por que:** custo medido por chamada — bytes gravados, tokens só com transcript
- **quando usar:** quantificar custo real de contexto antes de otimizar

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

**para que:** Declarative local eval matrix, goldens and holdout metadata.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

**Syntax**

```text
apiforge evals
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evals agent-governor`

**para que:** §23-§27 governor primitives vs declared corpus expectations.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Deterministic proxy-router eval: top-1/top-3, per family, protected-role misroutes.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Recorded specialist verdicts vs ground truth under each profile (no model calls).

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §53–§57: seeded ledgers -> inspect/compare/waste verdicts.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Warm/mutate/rebuild: all-hit on unchanged, precise invalidation, zero stale reuse.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Fixture capsule + recorded uses vs declared metrics and sufficiency gates.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §28-§32 lifecycle: shadow never governs, promotion gates, fallback.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Capsule bytes and evidence recall vs the recorded baseline; exit 1 when a gate fails.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Verification plans, retrieval, evidence refs, doctor, tiers, prefixes and locality gates.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Freshness watch, live gating, escalation, phase budget and resume pinning gates.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Path containment, class-pool budget, tokens, phase and delta gates on production code.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Canonical tasks x economy/balanced/deep with quality, evidence, cost, context, latency apart.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Profiles vs pre-economy plans with the risk floor as invariant; exit 1 on gate failure.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §46–§48: submit/attach/inspect/result/evidence/handoff/health lifecycle.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §23: quality x cost x latency frontier across profiles.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Ship only without quality, safety, holdout or mutation regression; exit 1 on reject.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Per-rule x language precision/recall of graph rules over the golden corpus.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §29 drift verdicts over declared pack+receipt cases.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** List declarative eval cases without executing agents.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §23: deterministic tier observed; provider tier deferred_external.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §24: the eight memory axes against the real governed store.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §33-§35 router constraints, scorecard floors and promotion evidence.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Re-plan stored decisions under the current policy; exit 1 if a required role is removed.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §38: lexical/graph/semantic/hybrid on recall, precision, latency, cost.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §25: synthesized attacks against the platform's own defenses.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Lazy expertise, per-role bytes, referee packets, shadow share and agent audit gates.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §50-§52: ledger spans -> OTLP export -> structural acceptance.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Usage rows + pricing + estimate vs ledger/cost/calibration expectations.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Compact output, gateway surface, discover/call reach and slicer recall gates.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §40–§43: audit findings, disclosure routing, paging, benchmark honesty.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** §23: recorded traces graded against the declared rubric.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Validate closed eval vocabulary and mutation/holdout requirements.

- **por que:** matriz de avaliação declarativa local, goldens e holdout
- **quando usar:** validar qualidade determinística antes de release

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

**para que:** Release evidence receipts.

- **por que:** recibos de evidência de release
- **quando usar:** produzir/verificar a cadeia de evidência de uma entrega

**Syntax**

```text
apiforge evidence
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `evidence emit`

**para que:** Emit a receipt binding artifact paths to their sha256 contents.

- **por que:** recibos de evidência de release
- **quando usar:** produzir/verificar a cadeia de evidência de uma entrega

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

**para que:** Cheapest evidence mode for a question; live_read_only only for runtime questions.

- **por que:** recibos de evidência de release
- **quando usar:** produzir/verificar a cadeia de evidência de uma entrega

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

**para que:** One evidence node with one-hop neighbors as further evidence:// refs.

- **por que:** recibos de evidência de release
- **quando usar:** produzir/verificar a cadeia de evidência de uma entrega

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

**para que:** Re-hash every artifact a receipt lists.

- **por que:** recibos de evidência de release
- **quando usar:** produzir/verificar a cadeia de evidência de uma entrega

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

**para que:** Execute a bounded, evidence-backed API evolution run.

- **por que:** executa um run de evolução de API bounded e com evidência
- **quando usar:** evolução governada de API com limites declarados

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

**para que:** Canonical execution, governance and evidence projections.

- **por que:** projeções canônicas de execução, governança e evidência
- **quando usar:** consultar a visão de experiência canônica

**Syntax**

```text
apiforge experience
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `experience doctor`

- **por que:** projeções canônicas de execução, governança e evidência
- **quando usar:** consultar a visão de experiência canônica

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

- **por que:** projeções canônicas de execução, governança e evidência
- **quando usar:** consultar a visão de experiência canônica

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

- **por que:** projeções canônicas de execução, governança e evidência
- **quando usar:** consultar a visão de experiência canônica

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

**para que:** Pre-registered field validation: evidence-joined run records and gap report.

- **por que:** validação de campo pré-registrada: run records com evidência juntada e gap report
- **quando usar:** validar em campo contra casos pré-registrados

**Syntax**

```text
apiforge field
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `field annotate`

**para que:** Record human fields with closed enums.

- **por que:** validação de campo pré-registrada: run records com evidência juntada e gap report
- **quando usar:** validar em campo contra casos pré-registrados

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

**para que:** Write anonymized verified tasks into evals/corpus/field.

- **por que:** validação de campo pré-registrada: run records com evidência juntada e gap report
- **quando usar:** validar em campo contra casos pré-registrados

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

**para que:** Join ledger, summary and checkpoint of linked runs into a field-run/v1 record.

- **por que:** validação de campo pré-registrada: run records com evidência juntada e gap report
- **quando usar:** validar em campo contra casos pré-registrados

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

**para que:** Counts, Wilson 95% CI, theme qualification and H1 verdict from verified runs.

- **por que:** validação de campo pré-registrada: run records com evidência juntada e gap report
- **quando usar:** validar em campo contra casos pré-registrados

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

**para que:** Blind verifier verdict; never echoes the human labels.

- **por que:** validação de campo pré-registrada: run records com evidência juntada e gap report
- **quando usar:** validar em campo contra casos pré-registrados

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

**para que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

**Syntax**

```text
apiforge forge
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `forge attach`

**para que:** §47 link a forge task to its governed TaskSpec execution unit.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §46 discover: public capability descriptors other engines can call.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §47 retrieve evidence: content-addressed artifact bundle.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §47/§48 handoff: portable bundle — delivery stays a human step.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §47 health: engine, protocol version and declared task counts.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §47 inspect: live wire projection of forge + governed state.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §47 retrieve result: governed OutcomeBrief mapped, gaps named.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** §47 submit: validate capability + risk gate, persist the request.

- **por que:** Forge Protocol: capabilities, task submit/inspect/result/evidence, handoff, health
- **quando usar:** interoperar com o control plane The Forge

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

**para que:** Fail-closed agentic decision gates.

- **por que:** gates de decisão agêntica fail-closed
- **quando usar:** verificar política antes de uma ação governada

**Syntax**

```text
apiforge governance
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governance decision-check`

**para que:** Evaluate and record a proposal; never infer approval from model text.

- **por que:** gates de decisão agêntica fail-closed
- **quando usar:** verificar política antes de uma ação governada

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

**para que:** Agent Governor decisions: ceilings, gain, stop, recovery and loop checks.

- **por que:** decisões do Agent Governor: tetos, ganho, stop, recovery, loop checks
- **quando usar:** inspecionar limites e decisões do governador

**Syntax**

```text
apiforge governor
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `governor decide`

**para que:** §23: profile ceilings adjusted by risk, security and budget.

- **por que:** decisões do Agent Governor: tetos, ganho, stop, recovery, loop checks
- **quando usar:** inspecionar limites e decisões do governador

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

**para que:** §24: pre-action expected information gain over declared signals.

- **por que:** decisões do Agent Governor: tetos, ganho, stop, recovery, loop checks
- **quando usar:** inspecionar limites e decisões do governador

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

**para que:** §27: block a strategy that repeats inside the trailing window.

- **por que:** decisões do Agent Governor: tetos, ganho, stop, recovery, loop checks
- **quando usar:** inspecionar limites e decisões do governador

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

**para que:** §26: governed recovery for a classified failure.

- **por que:** decisões do Agent Governor: tetos, ganho, stop, recovery, loop checks
- **quando usar:** inspecionar limites e decisões do governador

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

**para que:** §25: explicit STOP — continue only on gain > threshold or requirement.

- **por que:** decisões do Agent Governor: tetos, ganho, stop, recovery, loop checks
- **quando usar:** inspecionar limites e decisões do governador

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

**para que:** Native provenance graph — canonical JSONL store, closed-vocabulary queries.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

**Syntax**

```text
apiforge graph
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `graph build`

**para que:** Populate nodes.jsonl/edges.jsonl from case artifacts — deterministic bytes.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Structural gaps: unverified findings, unimplemented ops, unreferenced facts.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** jsonl copy, Neptune Gremlin CSV or RDF N-Triples, plus export.json digests.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Reverse traversal: everything that transitively depends on the node.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Filter nodes/edges by closed vocabulary — no free text.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Shortest directed path between two nodes; absent path is named.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Open the local Graph Studio explorer for this graph.

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Emit the ForgeGraphView/v1 document (Graph Studio contract).

- **por que:** grafo de proveniência nativo — store JSONL canônico, queries de vocabulário fechado
- **quando usar:** perguntas de dependência, impacto ou proveniência

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

**para que:** Offline-first gRPC contract control plane.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

**Syntax**

```text
apiforge grpc
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `grpc analyze`

**para que:** Build the canonical gRPC IR without invoking external toolchains.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Evaluate RPS/TPS evidence without claiming capacity from invalid runs.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Show optional local gRPC toolchain capabilities.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Generate deterministic local artifacts or report missing toolchains.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Classify protobuf evolution using deterministic compatibility rules.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Discover a gRPC contract and expose its canonical IR.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Project the contract to local gateway artifacts.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Run the offline contract test and independent verification gates.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** Run independent local verification over a gRPC contract.

- **por que:** control plane de contratos gRPC offline-first
- **quando usar:** trabalhar contratos gRPC sem executar serviços

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

**para que:** TokenSave: content-hash cache + local indexes over extractor output.

- **por que:** TokenSave: cache por content-hash + índices locais sobre saída de extratores
- **quando usar:** recuperação econômica por níveis L0-L6

**Syntax**

```text
apiforge index
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `index build`

**para que:** Write the 12 index kinds under .apiforge/index/ (manifest lists all).

- **por que:** TokenSave: cache por content-hash + índices locais sobre saída de extratores
- **quando usar:** recuperação econômica por níveis L0-L6

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

**para que:** Name added/changed/removed source files against the built index.

- **por que:** TokenSave: cache por content-hash + índices locais sobre saída de extratores
- **quando usar:** recuperação econômica por níveis L0-L6

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

**para que:** Create only a minimal local project or workspace manifest.

- **por que:** cria só um manifesto mínimo de projeto/workspace
- **quando usar:** primeiro passo num diretório novo

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

**para que:** Inspect installed assets and bounded project/workspace discovery.

- **por que:** inspeciona assets instalados e descoberta bounded de projeto/workspace
- **quando usar:** perguntar sobre artefatos instalados antes de ler arquivo

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

**para que:** Install API Forge assets into a project, workspace or the user home; manage the lifecycle (status, doctor, repair, update, uninstall).

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Deep installation health: ledger, drift, mcp config, handshake.

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Rewrite managed assets that went missing or drifted.

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Ledger + drift + health document of the installation.

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Remove only what the ledger declares as managed.

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Upgrade the bootstrap-installed runtime.

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Real JSON-RPC handshake: initialize + tools/list on the MCP server.

- **por que:** instala assets API Forge em projeto, workspace ou home; gerencia o ciclo de vida
- **quando usar:** ativar a forja num escopo governado

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

**para que:** Read-only external evidence adapters and freshness receipts.

- **por que:** adapters de evidência externa read-only e recibos de frescor
- **quando usar:** consultar fontes externas sem mutação

**Syntax**

```text
apiforge integration
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `integration github-issues`

**para que:** Read GitHub issues through a GET-only adapter and emit a receipt.

- **por que:** adapters de evidência externa read-only e recibos de frescor
- **quando usar:** consultar fontes externas sem mutação

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

**para que:** Read a remote HTTP health endpoint and emit a freshness receipt.

- **por que:** adapters de evidência externa read-only e recibos de frescor
- **quando usar:** consultar fontes externas sem mutação

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

**para que:** Read a generic external JSON endpoint (Jira, Linear or similar).

- **por que:** adapters de evidência externa read-only e recibos de frescor
- **quando usar:** consultar fontes externas sem mutação

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

**para que:** Verify external receipt correspondence and declared freshness.

- **por que:** adapters de evidência externa read-only e recibos de frescor
- **quando usar:** consultar fontes externas sem mutação

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

**para que:** Judge contract/code divergence, or catalog checks over report facts.

- **por que:** julga divergência contrato/código, ou checks de catálogo sobre facts
- **quando usar:** depois do analyze: facts viram findings com rule_id

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

**para que:** Domain packs — source authority, runtime matrices, declared evals.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

**Syntax**

```text
apiforge knowledge
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `knowledge adaptive`

**para que:** §36: L0→L4 ladder; escalates only while the level is insufficient.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Validate every pack; exit 4 when any problem is named.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** §29 drift verdict across one or more read-only source receipts.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Verify pack freshness from a local read-only source receipt.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** §29 source -> pack -> rule -> skill -> eval relation graph.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** List every pack with its areas, rules and verification date.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** §39: rewrite only when deterministic retrieval failed + gates allow.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Deterministic expansion, ranked passages with signals, progressive tiers.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Only the packs a declared trigger names; no trigger means no packs.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Print one pack: summary, source authority, matrix, declared evals.

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Packs whose upstream fingerprint, version or expiry says refresh_needed (never fetches).

- **por que:** domain packs — autoridade de fonte, matrizes de runtime, evals declarados
- **quando usar:** consultar a fonte canônica de conhecimento de domínio

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

**para que:** Opt-in experimental scenario catalog (§28).

- **por que:** catálogo de cenários experimentais opt-in (§28)
- **quando usar:** cenários reproduzíveis sem tocar o real

**Syntax**

```text
apiforge lab
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `lab scenarios`

**para que:** §28 experimental scenario catalog with honest coverage states.

- **por que:** catálogo de cenários experimentais opt-in (§28)
- **quando usar:** cenários reproduzíveis sem tocar o real

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

**para que:** MCP surface projections and their measured cost.

- **por que:** projeções de superfície MCP e seu custo medido
- **quando usar:** servir a forja via MCP ou auditar o custo da superfície

**Syntax**

```text
apiforge mcp
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `mcp audit`

**para que:** §40 audit: oversized schemas/outputs, weak descriptions, unbounded lists.

- **por que:** projeções de superfície MCP e seu custo medido
- **quando usar:** servir a forja via MCP ou auditar o custo da superfície

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

**para que:** §43 measured response bytes + labeled token estimate per sampled tool.

- **por que:** projeções de superfície MCP e seu custo medido
- **quando usar:** servir a forja via MCP ou auditar o custo da superfície

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

**para que:** §41 task -> capability router -> active tool set (advisory).

- **por que:** projeções de superfície MCP e seu custo medido
- **quando usar:** servir a forja via MCP ou auditar o custo da superfície

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

**para que:** Name, description and schema bytes of every tool on a surface.

- **por que:** projeções de superfície MCP e seu custo medido
- **quando usar:** servir a forja via MCP ou auditar o custo da superfície

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

**para que:** Governed append-only agent memory.

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

**Syntax**

```text
apiforge memory
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `memory invalidate`

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

**para que:** List pending and released quarantine rows.

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

**para que:** Human review boundary: release a quarantined candidate.

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

**para que:** §15 ranked retrieval: per-record score decomposition, deterministic.

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

- **por que:** memória de agente append-only governada
- **quando usar:** persistir contexto entre sessões com governo

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

**para que:** Offline-first runtime migration analysis and verification.

- **por que:** análise e verificação de migração de runtime offline-first
- **quando usar:** avaliar migração de runtime/framework com evidência

**Syntax**

```text
apiforge migration
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `migration analyze`

**para que:** Discover runtime migration impact without changing the project.

- **por que:** análise e verificação de migração de runtime offline-first
- **quando usar:** avaliar migração de runtime/framework com evidência

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

**para que:** Project an observed compatibility matrix; missing cells remain unresolved.

- **por que:** análise e verificação de migração de runtime offline-first
- **quando usar:** avaliar migração de runtime/framework com evidência

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

**para que:** Build a closed migration TaskSpec and dependency DAG.

- **por que:** análise e verificação de migração de runtime offline-first
- **quando usar:** avaliar migração de runtime/framework com evidência

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

**para que:** Apply conservative status gates to a migration report.

- **por que:** análise e verificação de migração de runtime offline-first
- **quando usar:** avaliar migração de runtime/framework com evidência

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

**para que:** Build the canonical API-IR.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

**Syntax**

```text
apiforge model
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `model alb`

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Read an API Gateway dump into facts — offline, no credentials.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Compose the API-IR and print it.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Graph call sites (Gremlin/openCypher/SPARQL) + GraphAccessIR and domain sketch.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Parse a Neptune/Neo4j plan dump into GraphPlanIR + data.graph.plan facts.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Read a Lambda dump into facts — offline, no credentials.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** OTel export -> perf.otel.* facts + a PerformanceRun — offline.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Extract gRPC services/messages from .proto — no protoc, offline.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Static extraction of Redis/Valkey call sites + DataAccessIR — offline.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Static resilience scan (timeouts, retries, pools, breaker/shutdown/
idempotency declarations) — heuristic, blind spots named.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Extract AWS::Serverless::* resources — intrinsics become named diagnostics.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Extract API Gateway + Lambda resources from HCL — offline, no terraform.

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

- **por que:** constrói o API-IR canônico
- **quando usar:** materializar a representação intermediária da API

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

**para que:** Recommend the specialist agent for the dominant finding area.

- **por que:** recomenda o agente especialista para a área dominante dos findings
- **quando usar:** depois de um case com findings: quem atende agora

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

**para que:** Offline-first OTel, Datadog and Dynatrace control plane.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

**Syntax**

```text
apiforge observability
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `observability capabilities`

**para que:** Show provider capabilities without credentials.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

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

**para que:** Validate credential metadata without reading environment or secret stores.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

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

**para que:** Correlate telemetry and SLO evidence into an incident-ready health view.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

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

**para que:** Normalize a fixture and compute signals without external access.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

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

**para que:** Recommend OTel instrumentation for Java, Go or Python.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

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

**para que:** Create a vendor read plan without credentials or network access.

- **por que:** control plane OTel, Datadog e Dynatrace offline-first
- **quando usar:** trabalhar telemetria/observabilidade com evidência exportada

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

**para que:** Compose over measured runs — compare, never interpolate.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

**Syntax**

```text
apiforge perf
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf chaos`

**para que:** List the declared controlled failure-injection scenarios (CHAOS-001..013).

Each scenario names the fault, the expected signal, the blast-radius
guard and the evidence a run must produce — injection itself is never
executed by API Forge.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** compare_runs / detect_regression over two PerformanceRun payloads.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** Append-only PerformanceRun memory — local store.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

**Syntax**

```text
apiforge perf memory
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `perf memory add`

**para que:** Append a run to .apiforge/perf/runs.jsonl — payload hash recorded.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** search_performance_memory — filters declared fields, never infers.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** Create a declarative load plan; generation never executes a tool.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** Generate the tool's script for a declared scenario — never executes it.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** suggest_fix — emits an ActionPlan; never applies it.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** passed / failed / inconclusive over a run — conditions named, never guessed.

- **por que:** compõe sobre runs medidos — compara, nunca interpola
- **quando usar:** comparar performance entre execuções medidas

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

**para que:** Planning verbs — compose over facts other verbs already extracted.

- **por que:** verbos de planejamento — compõem sobre facts já extraídos
- **quando usar:** revisar passos antes de executar trabalho composto

**Syntax**

```text
apiforge plan
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `plan architecture`

**para que:** Architecture Decision Engine — rank AWS primitives per role.

Eliminates on declared hard constraints, scores survivors on the
profile, and emits chosen + rejected-with-reason + change conditions.

- **por que:** verbos de planejamento — compõem sobre facts já extraídos
- **quando usar:** revisar passos antes de executar trabalho composto

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

**para que:** Per-route strangler cut plan over two code inventories.

- **por que:** verbos de planejamento — compõem sobre facts já extraídos
- **quando usar:** revisar passos antes de executar trabalho composto

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

**para que:** Run allowlisted local runtime probes for platform verticals.

- **por que:** probes de runtime locais allowlisted para verticais de plataforma
- **quando usar:** prova de runtime opt-in e allowlisted — prova fixtures, não produção

**Syntax**

```text
apiforge platform
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `platform verify-runtime`

**para que:** Execute committed probes and emit local runtime evidence.

- **por que:** probes de runtime locais allowlisted para verticais de plataforma
- **quando usar:** prova de runtime opt-in e allowlisted — prova fixtures, não produção

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

**para que:** Render the declared executor decomposition for a coordinator.

The floor on every platform — works without dispatch.

- **por que:** renderiza a decomposição de executor declarada para um coordenador
- **quando usar:** ver como um coordenador decompõe o trabalho

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

**para que:** Evaluate actions against the policy catalog.

- **por que:** avalia ações contra o catálogo de políticas
- **quando usar:** checar veredito de política antes de agir

**Syntax**

```text
apiforge policy
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `policy check`

**para que:** Decide whether an action is allowed, gated or denied.

- **por que:** avalia ações contra o catálogo de políticas
- **quando usar:** checar veredito de política antes de agir

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

**para que:** Release evidence bundle — sign binds hashes; verify names what diverged.

- **por que:** bundle de evidência de release — sign amarra hashes; verify nomeia o que divergiu
- **quando usar:** provar que o relatório corresponde à evidência

**Syntax**

```text
apiforge report
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `report build`

**para que:** Compose the release evidence bundle for a case.

- **por que:** bundle de evidência de release — sign amarra hashes; verify nomeia o que divergiu
- **quando usar:** provar que o relatório corresponde à evidência

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

**para que:** Generate an Ed25519 keypair — proves key possession, never identity.

- **por que:** bundle de evidência de release — sign amarra hashes; verify nomeia o que divergiu
- **quando usar:** provar que o relatório corresponde à evidência

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

**para que:** Append the signature block binding body/evidence/catalog hashes.

- **por que:** bundle de evidência de release — sign amarra hashes; verify nomeia o que divergiu
- **quando usar:** provar que o relatório corresponde à evidência

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

**para que:** Name which part diverged: signature_version|body|evidence|catalog|signature_crypto.

- **por que:** bundle de evidência de release — sign amarra hashes; verify nomeia o que divergiu
- **quando usar:** provar que o relatório corresponde à evidência

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

**para que:** Resume only persisted, eligible work from the latest control run.

- **por que:** retoma só trabalho persistido e elegível do último control run
- **quando usar:** uma execução falhou no meio — continuar do ponto válido

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

**para que:** Render the canonical Outcome Brief for a runtime run.

- **por que:** renderiza o Outcome Brief canônico de um runtime run
- **quando usar:** revisar o resultado de uma execução com gaps nomeados

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

**para que:** Model routing: candidates, scorecards and lifecycle promotion.

- **por que:** roteamento de modelo: candidatos, scorecards e promoção de ciclo de vida
- **quando usar:** decidir rota de modelo com scorecard, não chute

**Syntax**

```text
apiforge route
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `route model`

**para que:** §33: rank declared model candidates; quality history is a constraint.

- **por que:** roteamento de modelo: candidatos, scorecards e promoção de ciclo de vida
- **quando usar:** decidir rota de modelo com scorecard, não chute

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

**para que:** §35: lifecycle promotion gated on scorecard evidence, not benchmarks.

- **por que:** roteamento de modelo: candidatos, scorecards e promoção de ciclo de vida
- **quando usar:** decidir rota de modelo com scorecard, não chute

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

**para que:** §34: fold evaluation rows into scorecards per provider/model/class.

- **por que:** roteamento de modelo: candidatos, scorecards e promoção de ciclo de vida
- **quando usar:** decidir rota de modelo com scorecard, não chute

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

**para que:** Read the rule catalog — the knowledge base every finding cites.

- **por que:** lê o catálogo de regras — a base que todo finding cita
- **quando usar:** inspecionar regras disponíveis e metadados

**Syntax**

```text
apiforge rules
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `rules list`

**para que:** List rule ids, titles and severities by area.

- **por que:** lê o catálogo de regras — a base que todo finding cita
- **quando usar:** inspecionar regras disponíveis e metadados

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

**para que:** Print one rule's full guidance.

- **por que:** lê o catálogo de regras — a base que todo finding cita
- **quando usar:** inspecionar regras disponíveis e metadados

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

**para que:** Execute allowlisted scanner binaries, then read their reports.

- **por que:** executa binários de scanner allowlisted e lê seus relatórios
- **quando usar:** rodar ferramentas externas permitidas e capturar saída

**Syntax**

```text
apiforge run
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `run list`

**para que:** The tool registry — declared metadata plus *measured* install status.

- **por que:** executa binários de scanner allowlisted e lê seus relatórios
- **quando usar:** rodar ferramentas externas permitidas e capturar saída

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

**para que:** Execute a scanner binary (fixed argv, no shell) and read its report.

- **por que:** executa binários de scanner allowlisted e lê seus relatórios
- **quando usar:** rodar ferramentas externas permitidas e capturar saída

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

**para que:** Bounded agentic execution over sealed TaskSpecs; local and CI safe.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

**Syntax**

```text
apiforge runtime
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `runtime approve`

**para que:** Record a local human approval artifact for a runtime run.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Budget a run already spent, as a resume will continue it.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Cancel a control-plane run and persist the actor.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Complete a running step with a content-hashed result.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Create a persistent control-plane run without executing work.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Show ready steps and dynamic parallel width.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Close a completed plan through an independent review verdict.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Claim one ready step and consume one bounded call.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Request a debate room before the runtime makes a final decision.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Resume by replaying the TaskSpec through the bounded supervisor.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Execute a sealed TaskSpec with the deterministic fake adapter.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Show the newest persisted runtime run.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** §52 POST the payload to a real collector and count accepted spans.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** §50 export local spans as one OTLP ExportTraceServiceRequest body.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** §51 emit the standardized correlation id set (+ W3C traceparent).

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Query local agent/tool spans without contacting an exporter.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Append one sanitized local agent/tool span.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** §52 deterministic structural acceptance of an OTLP payload.

- **por que:** execução agêntica bounded sobre TaskSpecs selados; seguro local e CI
- **quando usar:** executar trabalho agêntico com orçamento e selo

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

**para que:** Copy-based sandbox evaluation.

- **por que:** avaliação em sandbox por cópia
- **quando usar:** testar uma mudança sem tocar a árvore original

**Syntax**

```text
apiforge sandbox
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sandbox apply`

**para que:** Apply a diff to copies of the tree and report the finding delta.

- **por que:** avaliação em sandbox por cópia
- **quando usar:** testar uma mudança sem tocar a árvore original

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

**para que:** Remove .apiforge/sandbox and report removed ids.

- **por que:** avaliação em sandbox por cópia
- **quando usar:** testar uma mudança sem tocar a árvore original

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

**para que:** Spec-driven development artifacts and gates.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

**Syntax**

```text
apiforge sdd
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `sdd check`

**para que:** Validate the SDD hash cascade and phase metadata.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

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

**para que:** Classify change risk deterministically and name the minimum SDD profile.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

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

**para que:** Write evidence/<kind>.json derived from a real artifact — no overrides.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

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

**para que:** Transition a phase; under --strict, gates require evidence or override.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

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

**para que:** Write the upstream sha256 into an artifact's frontmatter.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

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

**para que:** Summarize per-feature phase status.

- **por que:** artefatos e gates de spec-driven development
- **quando usar:** trabalho não-trivial: discover→intent→contract→architecture→plan→build→verify→secure→benchmark→ship

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

**para que:** Failures and signatures instead of whole logs; the full log stays behind ctx://.

- **por que:** falhas e assinaturas em vez de logs inteiros; o log fica atrás de ctx://
- **quando usar:** inspecionar falhas sem pagar o log completo em contexto

**Syntax**

```text
apiforge slice
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `slice log`

**para que:** Deduplicated failure signatures with frames, preceding context and environment.

- **por que:** falhas e assinaturas em vez de logs inteiros; o log fica atrás de ctx://
- **quando usar:** inspecionar falhas sem pagar o log completo em contexto

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

**para que:** Counts plus every failing test with file:line and assertion.

- **por que:** falhas e assinaturas em vez de logs inteiros; o log fica atrás de ctx://
- **quando usar:** inspecionar falhas sem pagar o log completo em contexto

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

**para que:** Show TaskSpec status, or project/workspace status when no task is supplied.

- **por que:** status de TaskSpec, ou de projeto/workspace sem task
- **quando usar:** visão rápida do estado atual

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

**para que:** Sealed, budgeted units of agentic work (TaskSpec).

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

**Syntax**

```text
apiforge task
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `task accept`

**para que:** Accept a supervised run; the acceptor must differ from the executor.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Compile a local API intention into a verified TaskSpec draft.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Create a task in draft; sealed only after review.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Run deterministic local mutations and report whether proofs detect them.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Bind a sealed TaskSpec to a closed persisted TaskPlan.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Reject a supervised run back to reviewable state.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Mark reviewed — any --set change bumps the revision, voiding seals.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Run the recipe within budgets; ends awaiting supervision or named stop.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Seal the current revision — key possession, never identity.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Task spec plus its append-only history.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Run independent proof checks and persist a VerificationRecord.

- **por que:** unidades seladas e orçadas de trabalho agêntico (TaskSpec)
- **quando usar:** submeter/inspecionar trabalho governado

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

**para que:** Execution-first terminal UX with a Rich/JSON fallback.

- **por que:** UX de terminal execution-first com fallback Rich/JSON
- **quando usar:** operar a forja interativamente no terminal

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

**para que:** Targeted verification plans (never executes).

- **por que:** planos de verificação direcionados — nunca executa
- **quando usar:** planejar verificação antes de executar

**Syntax**

```text
apiforge verify
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `verify escalate`

**para que:** Next verification step: static -> test -> stop; runtime read-only only if inconclusive.

- **por que:** planos de verificação direcionados — nunca executa
- **quando usar:** planejar verificação antes de executar

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

**para que:** Ladder level for the risk plus the impacted tests and the commands to run them.

- **por que:** planos de verificação direcionados — nunca executa
- **quando usar:** planejar verificação antes de executar

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

**para que:** Register independent repositories in a local virtual workspace.

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

**Syntax**

```text
apiforge workspace
```

<!-- keep:start -->
_free notes — errors, examples, next steps (hand-written, preserved)_
<!-- keep:end -->

### `workspace add`

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

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

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

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

**para que:** Workspace graph; declared relations only unless --infer is passed.

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

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

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

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

**para que:** Target repo first, direct neighbors next, transitive only on request.

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

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

- **por que:** registra repositórios independentes num workspace virtual local
- **quando usar:** operar multi-repo num escopo declarado

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
