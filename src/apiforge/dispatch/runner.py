"""Deterministic playbook dispatch.

Each playbook step names a verb; a closed table maps dispatchable verbs to
the same service functions the CLI calls. A step runs when every input the
verb needs is present in the dispatch context — otherwise it stays
``pending`` with the missing inputs named, or ``refused`` when the verb is
deliberately not dispatchable (``collect *`` touches AWS; mutating verbs
stay CLI-gated). Ran steps record the sha256 of their canonical output —
the dispatch record is evidence, not a transcript of vibes.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apiforge.core.ids import stable_id


class DispatchError(ValueError):
    """A refused dispatch; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class DispatchContext:
    """Inputs a dispatch run may draw on — everything absent stays absent."""

    case: Path
    project: Path | None = None
    contract: Path | None = None
    baseline: Path | None = None
    candidate: Path | None = None
    input_path: Path | None = None  # dump/report/template input for model verbs
    findings: Path | None = None
    rule_id: str | None = None
    now: str | None = None
    operation_id: str | None = None  # build endpoint target
    tool: str | None = None  # perf scenario generator selection


def _canon_sha(payload: object) -> str:
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(text.encode()).hexdigest()


def _inventory_payload(inventory: Any) -> dict[str, object]:
    return {
        "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
        "facts": [f.model_dump(mode="json") for f in inventory.facts],
        "framework": inventory.framework,
        "input_hashes": dict(inventory.input_hashes),
    }


def _need(ctx: DispatchContext, *fields: str) -> list[str]:
    return [f for f in fields if getattr(ctx, f) is None]


def _verb_discover(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.application.analyze import _EXTRACTORS, _detect_framework

    assert ctx.project is not None
    inventory = _EXTRACTORS[_detect_framework(ctx.project)](ctx.project)
    return _inventory_payload(inventory)


def _verb_analyze(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.application.analyze import analyze_project

    assert ctx.contract is not None and ctx.project is not None
    result = analyze_project(
        contract=ctx.contract,
        project=ctx.project,
        baseline=ctx.baseline,
        out_dir=ctx.case,
        framework="auto",
    )
    return {
        "case_id": result.manifest.case_id,
        "operations": len(result.model.operations),
        "findings": len(result.findings),
        "diagnostics": len(result.diagnostics),
    }


def _verb_model_build(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.adapters.fastapi.extractor import extract_fastapi
    from apiforge.api_ir.builder import build_api_model
    from apiforge.openapi.loader import load_openapi

    assert ctx.contract is not None and ctx.project is not None
    model = build_api_model(load_openapi(ctx.contract), extract_fastapi(ctx.project))
    return model.model_dump(mode="json")


def _verb_judge(ctx: DispatchContext) -> list[dict[str, Any]]:
    from apiforge.adapters.fastapi.extractor import extract_fastapi
    from apiforge.api_ir.builder import build_api_model
    from apiforge.openapi.loader import load_openapi
    from apiforge.rules.judge import judge_api_model

    assert ctx.contract is not None and ctx.project is not None
    model = build_api_model(load_openapi(ctx.contract), extract_fastapi(ctx.project))
    return [f.model_dump(mode="json") for f in judge_api_model(model)]


def _verb_diff_contract(ctx: DispatchContext) -> list[dict[str, Any]]:
    from apiforge.openapi.diff import diff_contracts
    from apiforge.openapi.loader import load_openapi

    assert ctx.baseline is not None and ctx.candidate is not None
    return [
        c.model_dump(mode="json")
        for c in diff_contracts(
            load_openapi(ctx.baseline), load_openapi(ctx.candidate)
        )
    ]


def _verb_rules_list(ctx: DispatchContext, area: str | None = None) -> dict[str, object]:
    from apiforge.rules.catalog import load_catalog

    catalog = load_catalog()
    items = [
        meta.model_dump(mode="json") | {"id": rid}
        for rid, meta in sorted(catalog.items())
        if area is None or meta.area == area
    ]
    return {"count": len(items), "rules": items}


def _verb_rules_lookup(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.rules.catalog import load_catalog

    assert ctx.rule_id is not None
    meta = load_catalog().get(ctx.rule_id.upper())
    if meta is None:
        raise DispatchError("AF-RULE-NOT-FOUND", f"no rule {ctx.rule_id!r}")
    return meta.model_dump(mode="json") | {"id": ctx.rule_id.upper()}


def _verb_next_step(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.application.next_step import next_step
    from apiforge.core.models import Finding

    assert ctx.findings is not None
    doc = json.loads(ctx.findings.read_text(encoding="utf-8"))
    payload = doc if isinstance(doc, list) else doc.get("findings", [])
    parsed = tuple(Finding.model_validate(f) for f in payload)
    step = next_step(parsed, "verify")
    return step.model_dump(mode="json")


def _verb_evidence_emit(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.evidence.build import emit_receipt

    receipt = emit_receipt(ctx.case, now=ctx.now)
    return receipt.model_dump(mode="json")


def _verb_context_funnel(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.application.funnel import measure_funnel

    return measure_funnel(ctx.case)


def _verb_economy(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.economy.ledger import report

    return report(ctx.case.parent)


def _model_verb(importer: str) -> Callable[[DispatchContext], dict[str, object]]:
    module_name, func_name = importer.rsplit(".", 1)

    def run(ctx: DispatchContext) -> dict[str, object]:
        import importlib

        extract = getattr(importlib.import_module(module_name), func_name)
        assert ctx.input_path is not None
        return _inventory_payload(extract(ctx.input_path))

    return run


def _verb_plan_strangler(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.core.models import Fact
    from apiforge.plan.strangler import strangler_plan

    def facts_of(path: Path) -> list[Fact]:
        doc = json.loads(path.read_text(encoding="utf-8"))
        payload = doc.get("facts", doc) if isinstance(doc, dict) else doc
        return [Fact.model_validate(f) for f in payload]

    assert ctx.baseline is not None and ctx.candidate is not None
    return strangler_plan(facts_of(ctx.baseline), facts_of(ctx.candidate))


def _verb_report_build(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.report.bundle import build_report

    return build_report(ctx.case, receipt_path=None, now=ctx.now)


def _verb_perf_compare(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.contracts.stubs import PerformanceRun
    from apiforge.perf.compare import compare_runs

    def load_run(path: Path) -> PerformanceRun:
        doc = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(doc, dict) and isinstance(doc.get("performance_run"), dict):
            doc = doc["performance_run"]
        return PerformanceRun.model_validate(doc)

    assert ctx.baseline is not None and ctx.candidate is not None
    return compare_runs(load_run(ctx.baseline), load_run(ctx.candidate)).model_dump(
        mode="json"
    )


def _verb_perf_verdict(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.contracts.stubs import PerformanceRun
    from apiforge.perf.verdict import verdict

    assert ctx.input_path is not None
    doc = json.loads(ctx.input_path.read_text(encoding="utf-8"))
    if isinstance(doc, dict) and isinstance(doc.get("performance_run"), dict):
        doc = doc["performance_run"]
    return verdict(PerformanceRun.model_validate(doc)).model_dump(mode="json")


def _verb_perf_scenario(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.perf.scenario import generate_scenario

    assert ctx.input_path is not None and ctx.tool is not None
    spec = json.loads(ctx.input_path.read_text(encoding="utf-8"))
    return dict(generate_scenario(ctx.tool, spec))


def _verb_perf_chaos(_ctx: DispatchContext) -> dict[str, object]:
    from apiforge.perf.chaos import list_scenarios

    return {"scenarios": list_scenarios()}


def _verb_plan_architecture(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.contracts.stubs import WorkloadProfile
    from apiforge.plan.architecture import recommend

    assert ctx.input_path is not None
    doc = json.loads(ctx.input_path.read_text(encoding="utf-8"))
    if isinstance(doc, dict) and isinstance(doc.get("workload_profile"), dict):
        doc = doc["workload_profile"]
    return dict(recommend(WorkloadProfile.model_validate(doc)))


# verb prefix -> (required ctx fields, runner). `collect *` is absent on
# purpose: dispatch never touches AWS.
_VERBS: tuple[tuple[str, tuple[str, ...], Callable[..., Any]], ...] = (
    ("discover", ("project",), _verb_discover),
    ("analyze", ("contract", "project"), _verb_analyze),
    ("model build", ("contract", "project"), _verb_model_build),
    ("judge", ("contract", "project"), _verb_judge),
    ("diff contract", ("baseline", "candidate"), _verb_diff_contract),
    ("rules list", (), _verb_rules_list),
    ("rules lookup", ("rule_id",), _verb_rules_lookup),
    ("next-step", ("findings",), _verb_next_step),
    ("evidence emit", ("now",), _verb_evidence_emit),
    ("context funnel", (), _verb_context_funnel),
    ("economy report", (), _verb_economy),
    ("plan strangler", ("baseline", "candidate"), _verb_plan_strangler),
    ("report build", ("now",), _verb_report_build),
    (
        "model api-gateway",
        ("input_path",),
        _model_verb("apiforge.adapters.apigateway.extract.extract_apigateway"),
    ),
    ("model lambda", ("input_path",), _model_verb("apiforge.adapters.lambda_.extract.extract_lambda")),
    ("model terraform", ("input_path",), _model_verb("apiforge.adapters.terraform.extract.extract_terraform")),
    ("model sam", ("input_path",), _model_verb("apiforge.adapters.sam.extract.extract_sam")),
    ("model asyncapi", ("input_path",), _model_verb("apiforge.adapters.asyncapi.extract.extract_asyncapi")),
    ("model graphql", ("input_path",), _model_verb("apiforge.adapters.graphql_.extract.extract_graphql")),
    ("model proto", ("input_path",), _model_verb("apiforge.adapters.protobuf.extract.extract_protobuf")),
    ("model redis", ("input_path",), _model_verb("apiforge.adapters.redis_.extract.extract_redis")),
    ("model elasticache-access", ("input_path",), _model_verb("apiforge.adapters.redis_.extract.extract_elasticache")),
    ("model mongo", ("input_path",), _model_verb("apiforge.adapters.dbaccess.extract_mongo")),
    ("model dynamodb-access", ("input_path",), _model_verb("apiforge.adapters.dbaccess.extract_dynamo_access")),
    ("model neptune-access", ("input_path",), _model_verb("apiforge.adapters.dbaccess.extract_neptune_access")),
    ("model otel", ("input_path",), _model_verb("apiforge.adapters.otel.extract.extract_otel")),
    ("model resilience", ("input_path",), _model_verb("apiforge.adapters.resilience.extract_resilience")),
    ("model sqs", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_sqs")),
    ("model sns", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_sns")),
    ("model eventbridge", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_eventbridge")),
    ("model iam-role", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_iam_role")),
    ("model cognito", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_cognito")),
    ("model waf", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_waf")),
    ("model dynamodb", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_dynamodb")),
    ("model docdb", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_docdb")),
    ("model neptune", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_neptune")),
    ("model stepfunctions", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_stepfunctions")),
    ("model cloudwatch", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_cloudwatch")),
    ("model xray", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_xray")),
    ("model kms", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_kms")),
    ("model secrets", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_secrets")),
    ("model vpc-endpoints", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_vpc_endpoints")),
    ("model s3", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_s3")),
    ("model alb", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_alb")),
    ("model ecs", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_ecs")),
    ("model eks", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_eks")),
    ("model ec2", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_ec2")),
    ("model msk", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_msk")),
    ("model elasticache", ("input_path",), _model_verb("apiforge.adapters.awsdumps.extract_elasticache")),
    ("perf compare", ("baseline", "candidate"), _verb_perf_compare),
    ("perf verdict", ("input_path",), _verb_perf_verdict),
    ("perf scenario", ("input_path", "tool"), _verb_perf_scenario),
    ("perf chaos", (), _verb_perf_chaos),
    ("plan architecture", ("input_path",), _verb_plan_architecture),
)


def _verb_build_endpoint(ctx: DispatchContext) -> dict[str, object]:
    from apiforge.build.service import build_endpoint
    from apiforge.policy.loader import load_policy

    assert ctx.contract is not None and ctx.project is not None
    assert ctx.operation_id is not None
    return build_endpoint(
        ctx.contract,
        ctx.project,
        ctx.operation_id,
        policy=load_policy(),
        promote=None,  # promotion is a human act, never a task step
    )


# Mutation verbs write into the task's sandbox copy only — never the main
# tree, never a promotion. They refuse under plain dispatch; the task runner
# is the only caller allowed to lift the gate, and only after the policy
# engine allows the action (declared class local_reversible).
_MUTATION_VERBS: dict[str, tuple[tuple[str, ...], Callable[..., Any]]] = {
    "build endpoint": (
        ("contract", "project", "operation_id"),
        _verb_build_endpoint,
    ),
}


def is_mutation_verb(verb: str) -> bool:
    head = verb.strip()
    return any(head == p or head.startswith(p + " ") for p in _MUTATION_VERBS)

_MODEL_REPORTS = {
    "pact": "apiforge.adapters.testreports.extract_pact",
    "schemathesis": "apiforge.adapters.testreports.extract_schemathesis",
    "k6": "apiforge.adapters.testreports.extract_k6",
    "coverage": "apiforge.adapters.testreports.extract_coverage",
    "zap": "apiforge.adapters.secreports.extract_zap",
    "semgrep": "apiforge.adapters.secreports.extract_semgrep",
    "trivy": "apiforge.adapters.secreports.extract_trivy",
    "gitleaks": "apiforge.adapters.secreports.extract_gitleaks",
    "jfr": "apiforge.adapters.perfprofiles.extract_jfr",
    "pprof": "apiforge.adapters.perfprofiles.extract_pprof",
    "pyroscope": "apiforge.adapters.perfprofiles.extract_pyroscope",
}

_VERBS = _VERBS + tuple(
    (f"model {name}", ("input_path",), _model_verb(path))
    for name, path in _MODEL_REPORTS.items()
)


def _match_verb(verb: str) -> tuple[tuple[str, ...], Callable[..., Any], str | None]:
    """Resolve a playbook verb string to (needs, runner, extra)."""
    head = verb.strip()
    extra: str | None = None
    for prefix, (needs, runner) in _MUTATION_VERBS.items():
        if head == prefix or head.startswith(prefix + " "):
            return needs, runner, "__mutation__"
    for prefix, needs, runner in _VERBS:
        if head == prefix or head.startswith(prefix + " "):
            extra = head[len(prefix):].strip() or None
            return needs, runner, extra
    if head.startswith("collect "):
        return (), lambda *a: None, "__collect__"
    return (), lambda *a: None, "__unknown__"


def required_fields(verb: str) -> tuple[str, ...]:
    """Ctx fields a verb needs bound — derived from the dispatch tables,
    so recipes never duplicate the requirement list."""
    needs, _, extra = _match_verb(verb)
    if extra in ("__unknown__", "__collect__"):
        return ()
    return needs


def dispatch_step(
    verb: str, ctx: DispatchContext, *, allow_mutation: bool = False
) -> dict[str, object]:
    """Execute one verb against the context — the unit tasks and playbooks share.

    Returns a status entry: ``ran`` (with ``output_sha256``), ``pending``
    (missing inputs named), ``refused`` (``collect *``, or a mutation verb
    without ``allow_mutation``), or ``error``.
    """
    needs, runner, extra = _match_verb(verb)
    entry: dict[str, object] = {"verb": verb}
    if extra == "__collect__":
        entry["status"] = "refused"
        entry["reason"] = "collect touches AWS — run outside dispatch"
    elif extra == "__unknown__":
        entry["status"] = "pending"
        entry["missing"] = ["dispatchable-verb"]
    elif extra == "__mutation__" and not allow_mutation:
        entry["status"] = "refused"
        entry["reason"] = (
            "AF-TASK-MUTATION-GATED: mutation verbs run only inside a task, "
            "after the policy engine allows them"
        )
    else:
        missing = _need(ctx, *needs)
        if missing:
            entry["status"] = "pending"
            entry["missing"] = missing
        else:
            try:
                if extra and verb.startswith("rules list"):
                    output = runner(ctx, extra.removeprefix("--area "))
                else:
                    output = runner(ctx)
                entry["status"] = "ran"
                entry["output_sha256"] = _canon_sha(output)
            except Exception as exc:  # noqa: BLE001 - a step failure is data
                entry["status"] = "error"
                entry["error"] = str(exc).split("\n")[0]
    return entry


def run_playbook(coordinator: str, ctx: DispatchContext) -> dict[str, object]:
    """Execute a coordinator's playbook; the record lands under case/dispatch."""
    from apiforge.rules.catalog import load_playbooks

    steps = load_playbooks().get(coordinator)
    if steps is None:
        raise DispatchError(
            "AF-DISPATCH-NO-PLAYBOOK",
            f"no playbook for {coordinator!r}; known: {sorted(load_playbooks())}",
        )
    record_steps: list[dict[str, object]] = []
    for order, step in enumerate(steps, 1):
        verb = str(step.get("verb", ""))
        entry: dict[str, object] = {
            "order": order,
            "executor": step.get("executor"),
            "purpose": step.get("purpose", ""),
        }
        entry.update(dispatch_step(verb, ctx))
        record_steps.append(entry)

    ran = sum(1 for s in record_steps if s["status"] == "ran")
    record = {
        "coordinator": coordinator,
        "ran": ran,
        "pending": sum(1 for s in record_steps if s["status"] == "pending"),
        "refused": sum(1 for s in record_steps if s["status"] == "refused"),
        "errors": sum(1 for s in record_steps if s["status"] == "error"),
        "steps": record_steps,
    }
    record_id = stable_id("dispatch", record)
    out = ctx.case / "dispatch" / f"{record_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record | {"record": str(out)}
