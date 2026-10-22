"""Classified eval catalog + thin adapters for the §7.2 conceptual ops
(install-2.0 cycle 5, lf-0038).

§7.1 classifies the existing eval surface — every suite below already exists
as a native ``apiforge evals <suite>`` / ``apiforge task <verb>`` verb; this
catalog is *declared metadata* over them, not a second engine:

- ``catalog()``/``describe()`` are agent-facing: ids, kinds, environments,
  declared inputs and hash-pinned baselines/holdouts. Case payloads and
  expected answers are never returned (§7.3) — ``describe`` reports sealed
  paths as sha256 + count.
- ``run_suite()`` dispatches to the native runner of one declared suite; a
  suite that declares inputs refuses to run until every ``--set name=value``
  is filled — missing inputs are a named refusal, never a silent skip.
- ``environment`` marks *simulated* (deterministic fixture/corpus evidence)
  vs *deferred-external* (provider/live tiers a human must gate) — a
  simulated result is evidence, never real-environment proof.
- ``result()`` reads a persisted eval report file back for hosts; the
  ``verification.*`` ops stay on the native ``verify plan`` / ``verify
  escalate`` / ``task verify`` verbs — they already implement §7.4
  (select → plan → execute authorized → evidence → explicit verdicts).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

from apiforge.contracts.base import ContractError
from apiforge.evals.paths import resolve_evals_path

EvalKind = Literal["developer", "runtime-decision", "output-verification", "host-conformance"]

SIMULATED: Final = "simulated"
DEFERRED_EXTERNAL: Final = "deferred-external"


@dataclass(frozen=True, kw_only=True)
class EvalSuite:
    """One declared eval suite. ``inputs`` are the named ``--set name=value``
    keys ``evals run`` requires before dispatching to the native runner."""

    id: str
    kind: EvalKind
    description: str
    argv: tuple[str, ...]
    corpus: str | None = None
    environment: str = SIMULATED
    inputs: tuple[str, ...] = ()
    sealed: tuple[str, ...] = ()


SUITES: tuple[EvalSuite, ...] = (
    # --- developer: offline corpus gates over apiforge internals -----------
    EvalSuite(
        id="validate",
        kind="developer",
        description="closed declarative case vocabulary + mutation/holdout requirements",
        argv=("evals", "validate"),
        corpus="evals/cases/platform.yaml",
    ),
    EvalSuite(
        id="economy",
        kind="developer",
        description="deterministic economy replay vs the recorded baseline gate",
        argv=("evals", "economy"),
        corpus="evals/corpus/economy",
        sealed=("evals/corpus/economy/baseline.json",),
    ),
    EvalSuite(
        id="economy-matrix",
        kind="developer",
        description="case × profile economy matrix — source of evals gate reports",
        argv=("evals", "economy-matrix"),
        corpus="evals/corpus/economy-matrix",
    ),
    EvalSuite(
        id="economy-extras",
        kind="developer",
        description="economy edge-case corpus (budget floors, preserved safety)",
        argv=("evals", "economy-extras"),
        corpus="evals/corpus/economy-extras",
    ),
    EvalSuite(
        id="economy-hardening",
        kind="developer",
        description="economy certification corpus — hardening cases",
        argv=("evals", "economy-hardening"),
        corpus="evals/corpus/economy-hardening",
    ),
    EvalSuite(
        id="economy-freshness",
        kind="developer",
        description="freshness watch, live gating, escalation, resume pinning",
        argv=("evals", "economy-freshness"),
        corpus="evals/corpus/economy-freshness",
    ),
    EvalSuite(
        id="cache",
        kind="developer",
        description="cache hits/misses and reuse accounting on the cache corpus",
        argv=("evals", "cache"),
        corpus="evals/corpus/economy-cache",
    ),
    EvalSuite(
        id="selective-agentics",
        kind="developer",
        description="selective agentic activation — when the loop may engage",
        argv=("evals", "selective-agentics"),
        corpus="evals/corpus/selective-agentics",
    ),
    EvalSuite(
        id="tool-economy",
        kind="developer",
        description="tool-call economy accounting vs declared expectations",
        argv=("evals", "tool-economy"),
        corpus="evals/corpus/tool-economy",
    ),
    EvalSuite(
        id="memory-evals",
        kind="developer",
        description="memory/case-persistence corpus verdicts",
        argv=("evals", "memory-evals"),
        corpus="evals/corpus/memory-evals",
    ),
    EvalSuite(
        id="token-economics",
        kind="developer",
        description="usage rows + pricing + estimate vs ledger/cost/calibration",
        argv=("evals", "token-economics"),
        corpus="evals/corpus/token-economics",
    ),
    EvalSuite(
        id="knowledge-drift",
        kind="developer",
        description="declared pack + receipt drift verdicts",
        argv=("evals", "knowledge-drift"),
        corpus="evals/corpus/knowledge-drift",
    ),
    EvalSuite(
        id="agentops",
        kind="developer",
        description="seeded ledgers → inspect/compare/waste verdicts",
        argv=("evals", "agentops"),
        corpus="evals/corpus/agentops",
    ),
    # --- runtime-decision: judge the runtime/control-plane's own decisions --
    EvalSuite(
        id="economy-routing",
        kind="runtime-decision",
        description="economy routing decisions vs declared corpus expectations",
        argv=("evals", "economy-routing"),
        corpus="evals/corpus/economy-routing",
    ),
    EvalSuite(
        id="model-routing",
        kind="runtime-decision",
        description="router constraints, scorecard floors, promotion evidence",
        argv=("evals", "model-routing"),
        corpus="evals/corpus/model-routing",
    ),
    EvalSuite(
        id="retrieval",
        kind="runtime-decision",
        description="lexical/graph/semantic/hybrid retrieval on recall, precision, cost",
        argv=("evals", "retrieval"),
        corpus="evals/corpus/retrieval",
    ),
    EvalSuite(
        id="control-plane",
        kind="runtime-decision",
        description="lifecycle: shadow never governs, promotion gates, fallback",
        argv=("evals", "control-plane"),
        corpus="evals/corpus/control-plane",
    ),
    EvalSuite(
        id="agent-governor",
        kind="runtime-decision",
        description="governor primitives vs declared corpus expectations",
        argv=("evals", "agent-governor"),
        corpus="evals/corpus/agent-governor",
    ),
    EvalSuite(
        id="security-adversarial",
        kind="runtime-decision",
        description="adversarial inputs against the declared guardrail surface",
        argv=("evals", "security-adversarial"),
        corpus="evals/corpus/security-adversarial",
    ),
    EvalSuite(
        id="replay",
        kind="runtime-decision",
        description="re-decide stored runs under the current policy; removals refuse",
        argv=("evals", "replay"),
    ),
    EvalSuite(
        id="gate",
        kind="runtime-decision",
        description="ship only without quality/safety/holdout/mutation regression",
        argv=("evals", "gate", "--baseline", "{baseline}", "--candidate", "{candidate}"),
        inputs=("baseline", "candidate"),
    ),
    EvalSuite(
        id="task-holdout",
        kind="runtime-decision",
        description="deterministic local mutations — expected detections stay sealed",
        argv=(
            "task",
            "holdout",
            "--project",
            "{project}",
            "--contract",
            "{contract}",
            "--manifest",
            "{manifest}",
        ),
        inputs=("project", "contract", "manifest"),
    ),
    EvalSuite(
        id="task-verify",
        kind="runtime-decision",
        description="independent proof checks → persisted VerificationRecord",
        argv=(
            "task",
            "verify",
            "{task}",
            "--project",
            "{project}",
            "--contract",
            "{contract}",
            "--manifest",
            "{manifest}",
        ),
        inputs=("task", "project", "contract"),  # --manifest is optional upstream
    ),
    # --- output-verification: grade produced artifacts -----------------------
    EvalSuite(
        id="agentic-quality",
        kind="output-verification",
        description="absolute floor per profile + non-regression vs baseline",
        argv=("evals", "agentic-quality"),
        corpus="evals/corpus/agentic-quality",
    ),
    EvalSuite(
        id="context-quality",
        kind="output-verification",
        description="context pack quality vs declared corpus",
        argv=("evals", "context-quality"),
        corpus="evals/corpus/context-quality",
    ),
    EvalSuite(
        id="graph-quality",
        kind="output-verification",
        description="graph/search output quality gates",
        argv=("evals", "graph-quality"),
        corpus="evals/corpus/graph-quality",
    ),
    EvalSuite(
        id="trace-grading",
        kind="output-verification",
        description="grade recorded traces against the declared rubric",
        argv=("evals", "trace-grading"),
        corpus="evals/corpus/trace-grading",
    ),
    EvalSuite(
        id="frontier",
        kind="output-verification",
        description="quality × cost × latency frontier across profiles",
        argv=("evals", "frontier", "--report", "{report}"),
        inputs=("report",),
    ),
    # --- host-conformance: the host/provider surface conforms ---------------
    EvalSuite(
        id="tool-surface",
        kind="host-conformance",
        description="declared tool surface vs the sealed audit baseline",
        argv=("evals", "tool-surface"),
        corpus="evals/corpus/tool-surface",
        sealed=("evals/corpus/tool-surface/audit-baseline.yaml",),
    ),
    EvalSuite(
        id="forge-protocol",
        kind="host-conformance",
        description="Forge protocol conformance of the declared surface",
        argv=("evals", "forge-protocol"),
        corpus="evals/corpus/forge-protocol",
    ),
    EvalSuite(
        id="agent-routing",
        kind="host-conformance",
        description="coordinator → case routing vs corpus incl. sealed holdout",
        argv=("evals", "agent-routing"),
        corpus="evals/corpus/agent-routing",
        sealed=("evals/corpus/agent-routing/holdout.json",),
    ),
    EvalSuite(
        id="telemetry-otlp",
        kind="host-conformance",
        description="OTLP export produces conforming spans",
        argv=("evals", "telemetry-otlp"),
        corpus="evals/corpus/telemetry-otlp",
    ),
    EvalSuite(
        id="live",
        kind="host-conformance",
        description=(
            "deterministic tier observed locally; provider tier is "
            "deferred-external — never fabricated as real-environment proof"
        ),
        argv=("evals", "live"),
        corpus="src/apiforge/rules/live_evals.yaml",
        environment=DEFERRED_EXTERNAL,
    ),
)


def _suite(suite_id: str) -> EvalSuite:
    for suite in SUITES:
        if suite.id == suite_id:
            return suite
    raise ContractError(
        "AF-EVALS-SUITE-UNKNOWN",
        f"unknown eval suite {suite_id!r} — declared: {', '.join(s.id for s in SUITES)}",
    )


# ---------------------------------------------------------------------------
# §7.1 — classified inventory (agent-facing: metadata only, never answers)
# ---------------------------------------------------------------------------


def catalog() -> list[dict[str, Any]]:
    """Every declared suite with its §7.1 kind. Metadata only — no case
    content, no expected answers, no holdout payloads."""
    return [
        {
            "id": s.id,
            "kind": s.kind,
            "description": s.description,
            "environment": s.environment,
            "inputs": list(s.inputs),
            "command": ["apiforge", *s.argv],
        }
        for s in SUITES
    ]


def manifest_suites() -> list[dict[str, Any]]:
    """``forge/context/v1`` ``eval_suites`` entries (id + kind + command)."""
    return [{"id": s.id, "kind": s.kind, "command": ["apiforge", *s.argv]} for s in SUITES]


def _file_digest(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return {
        "path": str(path),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }


def describe(suite_id: str, *, root: Path | None = None) -> dict[str, Any]:
    """One suite's metadata. Sealed baselines/holdouts surface as path +
    sha256 + count — contents are never returned (§7.3)."""
    suite = _suite(suite_id)
    base = root or Path.cwd()
    entries = [
        d
        for d in (
            _file_digest(base / rel if not Path(rel).is_absolute() else Path(rel))
            for rel in suite.sealed
        )
        if d is not None
    ]
    corpus_path = resolve_evals_path(suite.corpus) if suite.corpus else None
    doc: dict[str, Any] = {
        "id": suite.id,
        "kind": suite.kind,
        "description": suite.description,
        "environment": suite.environment,
        "command": ["apiforge", *suite.argv],
        "inputs": [{"name": name, "required": True} for name in suite.inputs],
        "corpus": str(corpus_path) if corpus_path is not None else None,
        "proof_note": (
            "deferred-external: provider/live tiers require a human-gated run — "
            "never fabricate a result"
            if suite.environment == DEFERRED_EXTERNAL
            else "simulated evidence — deterministic local proof, not a "
            "real-environment attestation"
        ),
        "sealed": {
            "count": len(suite.sealed),
            "resolved": entries,
            "content": "sealed — expected answers/baselines never inlined into agent-facing output",
        },
    }
    return doc


# ---------------------------------------------------------------------------
# §7.2 — evals.run / evals.result adapters over the native runners
# ---------------------------------------------------------------------------


def _runner_validate(o: dict[str, str]) -> dict[str, Any]:
    from apiforge.evals.suite import load_cases

    cases = load_cases(Path(o.get("path", "evals/cases/platform.yaml")))
    ids = [case.case_id for case in cases]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    invalid = [
        case.case_id for case in cases if not case.required_evidence or case.mutation == "none"
    ]
    ok = not duplicates and not invalid
    return {
        "ok": ok,
        "passed": ok,
        "cases": len(cases),
        "duplicate_ids": duplicates,
        "invalid_cases": invalid,
    }


def _runner_economy(o: dict[str, str]) -> Any:
    from apiforge.evals.economy import run_economy

    return run_economy(
        resolve_evals_path(o.get("corpus", "evals/corpus/economy")),
        Path(o.get("root", ".")),
    )


def _runner_economy_matrix(o: dict[str, str]) -> Any:
    from apiforge.evals.matrix import run_matrix

    return run_matrix(
        resolve_evals_path(o.get("corpus", "evals/corpus/economy-matrix")),
        Path(o.get("root", ".")),
    )


def _runner_gate(o: dict[str, str]) -> Any:
    from apiforge.evals.gate import gate_files

    return gate_files(Path(o["baseline"]), Path(o["candidate"]))


def _runner_frontier(o: dict[str, str]) -> Any:
    from apiforge.evals.frontier import run_frontier

    return run_frontier(
        Path(o["report"]),
        latencies=Path(o["latencies"]) if "latencies" in o else None,
        costs=Path(o["costs"]) if "costs" in o else None,
    )


def _runner_agent_routing(o: dict[str, str]) -> Any:
    from apiforge.evals.agent_routing import run

    return run(
        Path(o.get("root", ".")),
        cases_path=Path(o["cases"]) if "cases" in o else None,
    )


def _runner_replay(o: dict[str, str]) -> Any:
    from apiforge.evals.replay import replay

    return replay(
        root=Path(o["root"]) if "root" in o else None,
        corpus=Path(o["corpus"]) if "corpus" in o else None,
        profile=o.get("profile"),
    )


def _runner_live(o: dict[str, str]) -> Any:
    from apiforge.evals.live_evals import run_live_evals

    return run_live_evals(Path(o.get("layer", "src/apiforge/rules/live_evals.yaml")))


def _runner_task_holdout(o: dict[str, str]) -> dict[str, Any]:
    from apiforge.verification.holdout import run_holdouts

    root = Path(o.get("root", "."))
    records = run_holdouts(root, Path(o["project"]), Path(o["contract"]), Path(o["manifest"]))
    return {"holdouts": [r.model_dump(mode="json") for r in records]}


def _runner_task_verify(o: dict[str, str]) -> Any:
    from apiforge.taskspec.planner import plan_task
    from apiforge.verification.holdout import run_holdouts
    from apiforge.verification.service import verify_task

    root = Path(o.get("root", "."))
    task_id = o["task"]
    plan_path = root / ".apiforge" / "tasks" / task_id / "plan.json"
    if not plan_path.is_file():
        plan_task(root, task_id)
    holdout = (
        run_holdouts(root, Path(o["project"]), Path(o["contract"]), Path(o["manifest"]))
        if "manifest" in o
        else ()
    )
    return verify_task(
        root,
        task_id,
        project=Path(o["project"]),
        contract=Path(o["contract"]),
        run_id=o.get("run_id", "evals-run"),
        holdout=holdout,
    )


def _corpus_runner(module: str, func: str, default_corpus: str) -> Callable[[dict[str, str]], Any]:
    def run(o: dict[str, str]) -> Any:
        import importlib

        runner = getattr(importlib.import_module(module), func)
        return runner(resolve_evals_path(o.get("corpus", default_corpus)))

    return run


def _corpus_root_runner(
    module: str, func: str, default_corpus: str
) -> Callable[[dict[str, str]], Any]:
    def run(o: dict[str, str]) -> Any:
        import importlib

        runner = getattr(importlib.import_module(module), func)
        return runner(resolve_evals_path(o.get("corpus", default_corpus)), Path(o.get("root", ".")))

    return run


_RUNNERS: dict[str, Any] = {
    "validate": _runner_validate,
    "economy": _runner_economy,
    "economy-matrix": _runner_economy_matrix,
    "economy-extras": _corpus_root_runner(
        "apiforge.evals.extras", "run_extras", "evals/corpus/economy-extras"
    ),
    "economy-hardening": _corpus_root_runner(
        "apiforge.evals.hardening", "run_hardening", "evals/corpus/economy-hardening"
    ),
    "economy-freshness": _corpus_runner(
        "apiforge.evals.freshness_resume",
        "run_freshness_resume",
        "evals/corpus/economy-freshness",
    ),
    "cache": _corpus_root_runner(
        "apiforge.evals.cache", "run_cache_eval", "evals/corpus/economy-cache"
    ),
    "selective-agentics": _corpus_root_runner(
        "apiforge.evals.selective",
        "run_selective_eval",
        "evals/corpus/selective-agentics",
    ),
    "tool-economy": _corpus_root_runner(
        "apiforge.evals.tool_economy",
        "run_tool_economy",
        "evals/corpus/tool-economy",
    ),
    "memory-evals": _corpus_runner(
        "apiforge.evals.memory_evals", "run_memory_evals", "evals/corpus/memory-evals"
    ),
    "token-economics": _corpus_runner(
        "apiforge.evals.token_economics",
        "run_token_economics",
        "evals/corpus/token-economics",
    ),
    "knowledge-drift": _corpus_runner(
        "apiforge.evals.knowledge_drift",
        "run_knowledge_drift",
        "evals/corpus/knowledge-drift",
    ),
    "agentops": _corpus_runner("apiforge.evals.agentops", "run_agentops", "evals/corpus/agentops"),
    "economy-routing": _corpus_runner(
        "apiforge.evals.economy_routing",
        "run_economy_routing",
        "evals/corpus/economy-routing",
    ),
    "model-routing": _corpus_runner(
        "apiforge.evals.model_routing",
        "run_model_routing",
        "evals/corpus/model-routing",
    ),
    "retrieval": _corpus_runner(
        "apiforge.evals.retrieval", "run_retrieval", "evals/corpus/retrieval"
    ),
    "control-plane": _corpus_runner(
        "apiforge.evals.control_plane",
        "run_control_plane",
        "evals/corpus/control-plane",
    ),
    "agent-governor": _corpus_runner(
        "apiforge.evals.agent_governor",
        "run_agent_governor",
        "evals/corpus/agent-governor",
    ),
    "security-adversarial": _corpus_runner(
        "apiforge.evals.security_adversarial",
        "run_security_adversarial",
        "evals/corpus/security-adversarial",
    ),
    "replay": _runner_replay,
    "gate": _runner_gate,
    "task-holdout": _runner_task_holdout,
    "task-verify": _runner_task_verify,
    "agentic-quality": _corpus_runner(
        "apiforge.evals.agentic_quality",
        "run_agentic_quality",
        "evals/corpus/agentic-quality",
    ),
    "context-quality": _corpus_runner(
        "apiforge.evals.context_quality",
        "run_context_quality",
        "evals/corpus/context-quality",
    ),
    "graph-quality": _corpus_runner(
        "apiforge.evals.graph_quality",
        "run_graph_quality",
        "evals/corpus/graph-quality",
    ),
    "trace-grading": _corpus_runner(
        "apiforge.evals.trace_grading",
        "run_trace_grading",
        "evals/corpus/trace-grading",
    ),
    "frontier": _runner_frontier,
    "tool-surface": _corpus_runner(
        "apiforge.evals.tool_surface",
        "run_tool_surface",
        "evals/corpus/tool-surface",
    ),
    "forge-protocol": _corpus_runner(
        "apiforge.evals.forge_protocol",
        "run_forge_protocol",
        "evals/corpus/forge-protocol",
    ),
    "agent-routing": _runner_agent_routing,
    "telemetry-otlp": _corpus_runner(
        "apiforge.evals.otel_export",
        "run_otel_export",
        "evals/corpus/telemetry-otlp",
    ),
    "live": _runner_live,
}


def run_suite(suite_id: str, *, options: dict[str, str] | None = None) -> dict[str, Any]:
    """``evals run <suite>``: dispatch to the suite's native runner.

    Suites declaring ``inputs`` refuse until every one is supplied via
    ``--set name=value`` — a named refusal (``AF-EVALS-RUN-INPUT``) that names
    the native argv, never a silent skip.
    """
    suite = _suite(suite_id)
    opts = dict(options or {})
    missing = [name for name in suite.inputs if name not in opts]
    if missing:
        raise ContractError(
            "AF-EVALS-RUN-INPUT",
            f"suite {suite_id!r} requires inputs {', '.join(missing)} — "
            f"native verb: apiforge {' '.join(suite.argv)}",
        )
    runner = _RUNNERS.get(suite.id)
    if runner is None:
        raise ContractError(
            "AF-EVALS-RUN-INPUT",
            f"suite {suite_id!r} has no in-process adapter — "
            f"run the native verb: apiforge {' '.join(suite.argv)}",
        )
    result = runner(opts)
    if hasattr(result, "model_dump"):
        result = result.model_dump(mode="json")
    doc = result if isinstance(result, dict) else {"result": result}
    # §7.3: the environment marker travels with every result — simulated
    # fixture evidence is never real-environment proof, deferred-external
    # suites never fabricate a live result.
    doc.setdefault("environment", suite.environment)
    doc.setdefault("suite", suite.id)
    doc.setdefault("kind", suite.kind)
    return doc


def result(report: Path) -> dict[str, Any]:
    """``evals result --report <file>``: read a persisted eval report back.

    The report is re-emitted with its suite classification + environment
    marker so a host never confuses simulated evidence with real proof.
    """
    path = Path(report)
    if not path.is_file():
        raise ContractError(
            "AF-EVALS-RESULT-INVALID",
            f"no eval report at {path} — produce one with `apiforge evals <suite> [--out <file>]`",
        )
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(
            "AF-EVALS-RESULT-INVALID", f"{path}: not a JSON eval report ({exc})"
        ) from exc
    if not isinstance(doc, dict):
        raise ContractError("AF-EVALS-RESULT-INVALID", f"{path}: eval report must be a JSON object")
    suite_id = str(doc.get("suite") or doc.get("id") or "")
    out: dict[str, Any] = {
        "report": str(path),
        "report_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "schema": doc.get("schema"),
        "passed": doc.get("passed", doc.get("ok")),
        "document": doc,
    }
    if suite_id:
        try:
            suite = _suite(suite_id)
        except ContractError:
            pass
        else:
            out["suite"] = suite.id
            out["kind"] = suite.kind
            out["environment"] = suite.environment
            out["proof_note"] = describe(suite.id)["proof_note"]
    return out


__all__ = [
    "DEFERRED_EXTERNAL",
    "SIMULATED",
    "SUITES",
    "EvalSuite",
    "catalog",
    "describe",
    "manifest_suites",
    "result",
    "run_suite",
]
