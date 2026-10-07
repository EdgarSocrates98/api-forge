# API Forge AWS Slice 2 Plan — Lambda / Terraform / SAM

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans task-by-task.

**Goal:** Extend the AWS boundary: `collect lambda` at the edge, `model lambda`, `model terraform`, `model sam` offline. Same contract as slice 1 — only `collect` touches AWS; everything downstream reads dumps/files offline.

**Key constraint discovered during design:** SAM templates are saturated with intrinsic tags (`!Ref`, `!Sub`, `!GetAtt`) that the strict YAML loader refuses. A SAM-specific `SafeLoader` subclass maps unknown tags to `{"tag": <name>, "value": <scalar>}` **data** — never objects — and any property whose value is a tag is emitted `unresolved`, never resolved by inference.

## Task 1: `collect lambda` + `model lambda`

- `collect lambda --function-name X --out dump/ [--now]` → `function.json` (GetFunction Configuration only — `Code.Location` dropped: it is a pre-signed URL, never persisted), `manifest.json`. boto3 stays confined.
- `model lambda --path dump/` → facts `aws.lambda.function`: runtime, memory_mb, timeout_s, handler, package_type, layers count, **env var names only** (values never read), tracing_mode, reserved_concurrency.
- Diagnostics `AF-LAM-DUMP-MISSING` / `AF-LAM-DUMP-INVALID` (source optional on missing, as slice 1).

## Task 2: `model terraform`

- `python-hcl2>=4,<8` core dep (pure parser, like tree-sitter).
- `model terraform --path dir/` → per `*.tf`: `tf.apigateway.method` (http_method, authorization, api_key_required, integration timeout/type), `tf.apigateway.rest_api`, `tf.apigateway.stage`, `tf.lambda.function` (runtime, memory_size, timeout, reserved_concurrent_executions, env var names), `tf.lambda.permission` (principal, source_arn presence).
- Values containing `${` interpolation → `AF-TF-UNRESOLVED` (named, not inferred); parse failure → `AF-TF-PARSE`.

## Task 3: `model sam`

- `model sam --path template.yaml` → `AWS::Serverless::Function` → `sam.function` (runtime, memory, timeout, Api events with path+method), `AWS::Serverless::Api` → `sam.api` (stage_name, auth presence, cors).
- Tag-bearing values → `AF-SAM-UNRESOLVED`; non-mapping template / missing Resources → `AF-SAM-INVALID`.

## Task 4: gate + docs

- Parity rows `AF-LAM`/`AF-TF`/`AF-SAM`; hcl2 import confined to `adapters/terraform/`; threat row; README rows; labs/fixtures for all three.

## Final acceptance

- `model terraform` on a fixture with `aws_api_gateway_method{authorization=NONE}` emits the fact; interpolation → `AF-TF-UNRESOLVED`
- `model sam` on a template with `!Ref` emits `sam.function` + `AF-SAM-UNRESOLVED` for the tagged prop
- `collect lambda` without boto3 → `AF-COLLECT-AWS` with unlock
- pytest/ruff/mypy/`check_release.py` green
