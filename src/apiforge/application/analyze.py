"""End-to-end analysis orchestration.

``analyze_project`` composes the five stages — load contract, extract code,
build API-IR, judge findings, optionally diff a baseline — and persists a
reproducible case. Construction is one-directional: a pre-persistence
``CasePayload`` feeds ``save_case`` and the returned manifest completes the
``AnalysisResult``.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.adapters.go.extractor import extract_go
from apiforge.adapters.inventory import CodeInventory
from apiforge.adapters.spring.extractor import extract_spring
from apiforge.api_ir.builder import build_api_model
from apiforge.api_ir.models import ApiModel
from apiforge.case.models import CaseManifest, CasePayload
from apiforge.case.service import save_case
from apiforge.core.models import Diagnostic, Fact, Finding, JsonValue
from apiforge.openapi.diff import ContractChange, diff_contracts
from apiforge.openapi.loader import load_openapi
from apiforge.rules.judge import judge_api_model


class AnalysisError(ValueError):
    """An input or validation refusal; ``str()`` begins with the code."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


class AnalysisResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    manifest: CaseManifest
    model: ApiModel
    facts: tuple[Fact, ...]
    findings: tuple[Finding, ...]
    changes: tuple[ContractChange, ...]
    diagnostics: tuple[Diagnostic, ...]
    cache: Mapping[str, JsonValue] = Field(default_factory=dict)


def _require_file(path: Path, code: str = "AF-INPUT-NOT-FOUND") -> Path:
    if not path.is_file():
        raise AnalysisError(code, str(path))
    return path


def _require_dir(path: Path, code: str = "AF-INPUT-NOT-FOUND") -> Path:
    if not path.is_dir():
        raise AnalysisError(code, str(path))
    return path


# Provenance keys every upstream fact must carry under ``attrs["upstream"]``: the foreign
# engine that produced it, the run/node/item it derives from. ``extractor`` names the
# intake channel, never a native extractor (``apiforge`` would launder foreign facts as
# locally observed ones). ``kind``/``fact_id`` live in the ``upstream.*`` namespaces for
# the same reason: a foreign observation must never be indistinguishable from a local one.
UPSTREAM_EXTRACTOR = "theforge/handoff"
_UPSTREAM_KEYS = ("provider", "run_id", "node", "item")

# Keys that would turn evidence transport into instruction transport. The intake accepts
# declarative payloads (claims, severities, provenance, artifact references) and refuses
# imperative ones: an upstream document must never carry an agent prompt, a routing
# command or a directive for the receiving engine. The vocabulary is closed — widening
# it is a contract change, not a judgement call. Matching is exact after normalization
# (lowercase, ``-``/`` `` → ``_``), so ``plan_run`` stays a provenance key while ``plan``
# is refused.
_FORBIDDEN_KEYS = frozenset({
    "action", "actions", "agent", "command", "commands", "directive", "directives",
    "execute", "goal", "instruction", "instructions", "message", "messages",
    "objective", "persona", "plan", "prompt", "prompts", "request", "role",
    "route", "routes", "routing", "system", "task", "tasks", "tool_call",
    "workflow",
})


def _normalized_key(key: object) -> str:
    return str(key).strip().lower().replace("-", "_").replace(" ", "_")


def _forbidden_key(value: object) -> str | None:
    """First forbidden key found walking a JSON tree, or None. Iterative: payload
    depth is adversary-controlled."""
    stack = [value]
    while stack:
        node = stack.pop()
        if isinstance(node, Mapping):
            for key, item in node.items():
                if _normalized_key(key) in _FORBIDDEN_KEYS:
                    return str(key)
                stack.append(item)
        elif isinstance(node, (list, tuple)):
            stack.extend(node)
    return None


def _check_upstream(facts: Sequence[Fact]) -> None:
    """Refuse foreign facts that cannot be told apart from local evidence — and any
    that try to carry instructions instead of observations."""
    for index, fact in enumerate(facts):
        upstream = fact.attrs.get("upstream")
        if (
            fact.source.extractor == "apiforge"
            or not isinstance(upstream, Mapping)
            or not fact.fact_id.startswith("upstream:")
            or not fact.kind.startswith("upstream.")
        ):
            raise AnalysisError(
                "AF-UPSTREAM-UNMARKED",
                f"upstream fact {index} ({fact.fact_id!r}) is not marked: it needs a "
                f"non-'apiforge' source.extractor, an attrs.upstream provenance map "
                f"and the upstream: / upstream. id/kind namespaces",
            )
        missing = [key for key in _UPSTREAM_KEYS if not isinstance(upstream.get(key), str)
                   or not upstream[key]]
        if missing:
            raise AnalysisError(
                "AF-UPSTREAM-UNMARKED",
                f"upstream fact {index} ({fact.fact_id!r}): attrs.upstream is missing "
                f"or has empty keys {missing}",
            )
        for field_name, payload in (("attrs", fact.attrs), ("measures", fact.measures)):
            bad = _forbidden_key(payload)
            if bad is not None:
                raise AnalysisError(
                    "AF-UPSTREAM-FORBIDDEN",
                    f"upstream fact {index} ({fact.fact_id!r}): {field_name} carries "
                    f"key {bad!r}, which transports instructions — the upstream intake "
                    f"accepts evidence, never commands",
                )


def _contract_facts(model: ApiModel) -> tuple[Fact, ...]:
    """Synthesize contract.operation Facts so every evidence id resolves."""
    facts: list[Fact] = []
    for op in model.operations:
        for projection in op.contract_projections:
            operation_id = projection.detail.get("operation_id")
            facts.append(
                Fact(
                    fact_id=projection.fact_id,
                    kind="contract.operation",
                    source=projection.source,
                    measures={"method": op.method, "path": op.path},
                    attrs={"operation_id": operation_id} if operation_id else {},
                )
            )
    return tuple(facts)


_EXTRACTORS = {
    "fastapi": extract_fastapi,
    "spring": extract_spring,
    "go": extract_go,
}


def _detect_framework(project: Path) -> str:
    counts = {
        "spring": sum(1 for _ in project.rglob("*.java")),
        "fastapi": sum(1 for _ in project.rglob("*.py")),
        "go": sum(1 for _ in project.rglob("*.go")),
    }
    present = {k: v for k, v in counts.items() if v}
    if not present:
        raise AnalysisError(
            "AF-INPUT-FRAMEWORK-UNKNOWN",
            f"{project}: no .java, .py or .go files to detect a framework from",
        )
    # majority wins; ties break alphabetically for determinism
    return max(sorted(present), key=present.__getitem__)


def analyze_project(
    contract: Path,
    project: Path,
    baseline: Path | None,
    out_dir: Path,
    framework: str = "auto",
    cache_dir: Path | None = None,
    ledger_root: Path | None = None,
    upstream: Sequence[Fact] = (),
) -> AnalysisResult:
    """Run the deterministic slice and persist a verified case.

    ``upstream`` facts are foreign evidence admitted through a marked intake
    (``_check_upstream``): they are persisted with the case so downstream verbs
    (``graph``, ``evidence``, ``brief``, ``judge --facts``) see them with their
    provenance intact, but they are never part of the judged API model — a claim
    about another project must not trigger a rule of this one.
    """
    contract_path = _require_file(Path(contract))
    project_path = _require_dir(Path(project))
    baseline_path = _require_file(Path(baseline)) if baseline else None
    if framework == "auto":
        framework = _detect_framework(project_path)
    extractor = _EXTRACTORS.get(framework)
    if extractor is None:
        raise AnalysisError(
            "AF-INPUT-FRAMEWORK-UNKNOWN",
            f"unknown framework {framework!r}; expected one of {sorted(_EXTRACTORS)} or 'auto'",
        )

    document = load_openapi(contract_path)
    cache_meta: dict[str, JsonValue] = {"enabled": False}
    inventory: CodeInventory
    if cache_dir is not None:
        from apiforge.index.cache import extract_cached

        inventory, meta = extract_cached(project_path, framework, extractor, cache_dir, ledger_root)
        cache_meta = dict(meta)
    else:
        inventory = extractor(project_path)
    model = build_api_model(document, inventory)
    findings = judge_api_model(model)
    changes = diff_contracts(load_openapi(baseline_path), document) if baseline_path else ()
    _check_upstream(upstream)

    payload = CasePayload(
        contract_path=str(contract),
        project_path=str(project),
        model=model,
        facts=(*inventory.facts, *_contract_facts(model), *upstream),
        findings=findings,
        changes=changes,
        diagnostics=model.diagnostics,
    )
    manifest = save_case(out_dir, payload)
    return AnalysisResult(
        manifest=manifest,
        model=model,
        facts=payload.facts,
        findings=findings,
        changes=changes,
        diagnostics=model.diagnostics,
        cache=cache_meta,
    )
