"""L1–L3 deterministic selection: case fingerprint, graph impact and evidence candidates."""

from __future__ import annotations

import ast
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import yaml

from apiforge.context.gateway.canonical import digest
from apiforge.context.gateway.dedup import (
    brace_block_end,
    code_only,
    compare,
    find_models,
    schema_fields,
)
from apiforge.context.gateway.errors import GatewayError
from apiforge.contracts.context import RefKind, RefOrigin
from apiforge.contracts.graph import EdgeKind, NodeKind
from apiforge.graph.build import build_graph
from apiforge.graph.impact import assess_graph_impact
from apiforge.graph.store import NODES_FILE, read_graph

KIND_ORDER: dict[str, int] = {
    "contract": 0,
    "schema": 1,
    "code": 2,
    "policy": 3,
    "test": 4,
    "knowledge": 5,
}
_TEST_FILE = re.compile(r"(^test_.*\.py$|_test\.py$|Test\.java$|_test\.go$|Tests?\.kt$)")
_SCHEMA_REF = "#/components/schemas/"
_MAX_TEST_FILES = 3


@dataclass(frozen=True)
class Candidate:
    content: str
    kind: RefKind
    label: str
    source: str
    provenance: str
    origin: RefOrigin
    span: tuple[int, int] | None = None
    parity: bool | None = None
    delta: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def sort_key(self) -> tuple[int, str, str, tuple[int, int]]:
        return (KIND_ORDER[self.kind], self.label, self.source, self.span or (0, 0))


@dataclass
class Selection:
    fingerprint: dict[str, object] = field(default_factory=dict)
    impact: dict[str, int] = field(default_factory=dict)
    candidates: list[Candidate] = field(default_factory=list)
    policies: tuple[str, ...] = ()
    unresolved: list[str] = field(default_factory=list)
    graph_ready: bool = False


def parse_target(target: str) -> tuple[str, str]:
    text = target.strip().replace(":", " ", 1) if ":/" in target else target.strip()
    parts = text.split(None, 1)
    if len(parts) != 2 or not parts[1].startswith("/"):
        raise GatewayError(
            "AF-CONTEXT-TARGET-INVALID",
            f"{target!r} is not '<METHOD> /path'",
            field="target",
            unlock="pass an operation such as 'POST /orders' or 'POST:/orders'",
        )
    return parts[0].upper(), parts[1]


def load_case(case_dir: Path) -> dict[str, Any] | None:
    manifest = case_dir / "case.json"
    if not manifest.is_file():
        return None
    case = _read_json(manifest)
    for name in ("api-ir.json", "facts.json", "findings.json"):
        path = case_dir / name
        case[name] = _read_json(path) if path.is_file() else {}
    return case


def fingerprint(case: Mapping[str, Any], root: Path | None = None) -> dict[str, object]:
    facts = case["facts.json"].get("facts") or []
    extractors = sorted(
        {
            str((fact.get("source") or {}).get("extractor"))
            for fact in facts
            if str(fact.get("kind", "")).startswith("code.")
        }
    )
    inputs = case.get("inputs") or {}
    base = root or Path(".")
    return {
        "case_id": str(case.get("case_id", "unknown")),
        "contract": _rel(base / str(inputs.get("contract", "")), base),
        "project": _rel(base / str(inputs.get("project", "")), base),
        "frameworks": extractors,
        "operations": len(case["api-ir.json"].get("operations") or []),
    }


def select(
    root: Path, case_dir: Path, case: Mapping[str, Any], target: str, mode: str
) -> Selection:
    method, path = parse_target(target)
    selection = Selection(fingerprint=fingerprint(case, root))
    inputs = case.get("inputs") or {}
    contract_path = root / str(inputs.get("contract", ""))
    project = root / str(inputs.get("project", ""))
    target_id = f"operation:{method} {path}"
    nodes, edges = _graph(root, case_dir, case)
    if target_id not in {node.id for node in nodes}:
        raise GatewayError(
            "AF-CONTEXT-TARGET-NOT-FOUND",
            f"{target_id} is not an operation of {selection.fingerprint['case_id']}",
            field="target",
            unlock="pick an operation listed in the case api-ir.json",
        )
    selection.graph_ready = True
    forward = [edge for edge in edges if edge.from_id == target_id]
    route_facts = [edge.to_id for edge in forward if edge.kind is EdgeKind.IMPLEMENTED_BY]
    via_graph = set(route_facts)
    route_facts.extend(
        sorted(
            fact_id
            for fact_id, fact in _route_facts(case, method, path).items()
            if fact_id not in via_graph
        )
    )
    findings: set[str] = set()
    for fact_id in route_facts:
        assessment = assess_graph_impact(nodes, edges, fact_id, mode=mode)
        findings.update(
            item.node_id for item in assessment.impacted_nodes if item.kind is NodeKind.FINDING
        )
        selection.unresolved.extend(assessment.unresolved)
    selection.impact = {"direct": len(forward), "transitive": len(findings)}
    if not route_facts:
        selection.unresolved.append(f"code-route-missing:{method} {path}")
    operation = _ir_operation(case, method, path)
    raw = _contract_raw(operation)
    selection.candidates.append(
        Candidate(
            content=_yaml({path: {method.lower(): raw}}),
            kind="contract",
            label=f"operation:{method} {path}",
            source=_rel(contract_path, root),
            provenance="target",
            origin="contract",
        )
    )
    schemas = _schemas(contract_path, raw, selection.unresolved)
    models = find_models(project, schemas)
    for name, schema in sorted(schemas.items()):
        selection.candidates.append(
            Candidate(
                content=_yaml({name: schema}),
                kind="schema",
                label=f"schema:{name}",
                source=_rel(contract_path, root),
                provenance=f"schema-ref:{name}",
                origin="contract",
            )
        )
        model = models.get(name)
        if model is not None:
            parity, delta = compare(schema_fields(schema), model.fields)
            selection.candidates.append(
                Candidate(
                    content=model.text,
                    kind="code",
                    label=f"model:{name}",
                    source=_rel(model.path, root),
                    provenance=f"schema-model:{name}",
                    origin="code",
                    span=model.span,
                    parity=parity,
                    delta=delta,
                )
            )
    facts = {str(fact.get("fact_id")): fact for fact in case["facts.json"].get("facts") or []}
    handlers: list[str] = []
    for fact_id in sorted(route_facts):
        fact = facts.get(fact_id)
        if fact is None:
            selection.unresolved.append(f"route-fact-missing:{fact_id}")
            continue
        provenance = (
            f"graph-edge:implemented_by:{fact_id}"
            if fact_id in via_graph
            else f"fact-match:code.route:{fact_id}"
        )
        candidate, handler = _handler(root, project, fact, provenance, selection.unresolved)
        if candidate is not None:
            selection.candidates.append(candidate)
        if handler:
            handlers.append(handler)
    finding_rows = {
        str(item.get("finding_id")): item for item in case["findings.json"].get("findings") or []
    }
    rules: set[str] = set()
    for finding_id in sorted(findings):
        finding = finding_rows.get(finding_id, {})
        rule = str(finding.get("rule_id", "unknown"))
        rules.add(rule)
        selection.candidates.append(
            Candidate(
                content=_yaml(
                    {
                        key: finding.get(key)
                        for key in ("rule_id", "severity", "status", "title", "evidence")
                    }
                ),
                kind="policy",
                label=f"finding:{rule}",
                source=_rel(case_dir / "findings.json", root),
                provenance=f"graph-edge:backed_by:{finding_id}",
                origin="graph",
            )
        )
    selection.policies = tuple(sorted(rules))
    selection.candidates.extend(_tests(root, project, handlers))
    unique: dict[tuple[str, str, str], Candidate] = {}
    for candidate in selection.candidates:
        unique.setdefault((digest(candidate.content), candidate.kind, candidate.label), candidate)
    selection.candidates = sorted(unique.values(), key=Candidate.sort_key)
    selection.unresolved = sorted(set(selection.unresolved))
    return selection


def _graph(root: Path, case_dir: Path, case: Mapping[str, Any]) -> tuple[list[Any], list[Any]]:
    out_dir = root / ".apiforge" / "ctx" / "graph" / digest(str(case.get("case_id", "")))[:16]
    if not (out_dir / NODES_FILE).is_file():
        build_graph(case_dir, out_dir)
    return read_graph(out_dir)


def _route_facts(case: Mapping[str, Any], method: str, path: str) -> dict[str, Mapping[str, Any]]:
    matched: dict[str, Mapping[str, Any]] = {}
    for fact in case["facts.json"].get("facts") or []:
        measures = fact.get("measures") or {}
        if (
            fact.get("kind") == "code.route"
            and str(measures.get("method", "")).upper() == method
            and str(measures.get("path", "")).rstrip("/") == path.rstrip("/")
        ):
            matched[str(fact.get("fact_id"))] = fact
    return matched


def _ir_operation(case: Mapping[str, Any], method: str, path: str) -> Mapping[str, Any]:
    for operation in case["api-ir.json"].get("operations") or []:
        if str(operation.get("method", "")).upper() == method and operation.get("path") == path:
            return cast(Mapping[str, Any], operation)
    return {}


def _contract_raw(operation: Mapping[str, Any]) -> Mapping[str, Any]:
    for projection in operation.get("contract_projections") or []:
        raw = (projection.get("detail") or {}).get("raw")
        if isinstance(raw, Mapping):
            return raw
    return {}


def _schemas(contract_path: Path, raw: Mapping[str, Any], unresolved: list[str]) -> dict[str, Any]:
    if not contract_path.is_file():
        unresolved.append(f"contract-missing:{contract_path.name}")
        return {}
    document = yaml.safe_load(contract_path.read_text(encoding="utf-8")) or {}
    components = ((document.get("components") or {}).get("schemas")) or {}
    found: dict[str, Any] = {}
    pending = sorted(_refs(raw))
    while pending:
        name = pending.pop(0)
        if name in found:
            continue
        schema = components.get(name)
        if schema is None:
            unresolved.append(f"schema-unresolved:{name}")
            continue
        found[name] = schema
        pending.extend(sorted(_refs(schema) - set(found)))
    return found


def _refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith(_SCHEMA_REF):
            refs.add(ref.removeprefix(_SCHEMA_REF))
        for item in value.values():
            refs |= _refs(item)
    elif isinstance(value, list):
        for item in value:
            refs |= _refs(item)
    return refs


def _handler(
    root: Path, project: Path, fact: Mapping[str, Any], provenance: str, unresolved: list[str]
) -> tuple[Candidate | None, str]:
    source = fact.get("source") or {}
    attrs = fact.get("attrs") or {}
    handler = str(attrs.get("function") or attrs.get("handler") or "").split(".")[-1]
    file = project / str(source.get("path", ""))
    line = int(source.get("line") or 0)
    if not file.is_file() or line < 1:
        unresolved.append(f"handler-source-missing:{fact.get('fact_id')}")
        return None, handler
    located = _locate(project, file, line, handler)
    if located is None:
        unresolved.append(f"handler-unresolved:{handler or fact.get('fact_id')}")
        return None, handler
    path, span, text = located
    return (
        Candidate(
            content=text,
            kind="code",
            label=f"handler:{handler or path.name}",
            source=_rel(path, root),
            provenance=provenance,
            origin="code",
            span=span,
        ),
        handler,
    )


def _locate(
    project: Path, file: Path, line: int, handler: str
) -> tuple[Path, tuple[int, int], str] | None:
    lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
    if file.suffix == ".py":
        span = _python_span(lines, line)
        return (file, span, _slice(lines, span)) if span else None
    if (
        file.suffix == ".go"
        and handler
        and not re.search(rf"\bfunc\b.*\b{re.escape(handler)}\s*\(", lines[line - 1])
    ):
        for candidate in sorted(project.rglob("*.go")):
            other = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
            for index, text in enumerate(other):
                if re.match(rf"^func\s+(\([^)]*\)\s*)?{re.escape(handler)}\s*\(", text):
                    span = (index + 1, brace_block_end(other, index))
                    return candidate, span, _slice(other, span)
        return file, (line, line), lines[line - 1]
    start = next(
        (
            index
            for index in range(line - 1, min(len(lines), line + 20))
            if "{" in code_only(lines[index])
        ),
        None,
    )
    if start is None:
        return file, (line, line), lines[line - 1]
    span = (line, brace_block_end(lines, start))
    return file, span, _slice(lines, span)


def _python_span(lines: list[str], line: int) -> tuple[int, int] | None:
    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        start = min([node.lineno, *(item.lineno for item in node.decorator_list)])
        end = node.end_lineno or node.lineno
        if start <= line <= end:
            return start, end
    return None


def _tests(root: Path, project: Path, handlers: list[str]) -> list[Candidate]:
    names = sorted({name for name in handlers if name})
    if not names or not project.is_dir():
        return []
    found: list[Candidate] = []
    for path in sorted(project.rglob("*")):
        if len(found) >= _MAX_TEST_FILES:
            break
        if not path.is_file() or not _TEST_FILE.search(path.name) or ".apiforge" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = [name for name in names if re.search(rf"\b{re.escape(name)}\b", text)]
        if hits:
            found.append(
                Candidate(
                    content=text,
                    kind="test",
                    label=f"test:{path.name}",
                    source=_rel(path, root),
                    provenance=f"symbol-match:{hits[0]}",
                    origin="filesystem",
                )
            )
    return found


def _slice(lines: list[str], span: tuple[int, int]) -> str:
    return "\n".join(lines[span[0] - 1 : span[1]])


def _yaml(value: Any) -> str:
    return yaml.safe_dump(json.loads(json.dumps(value)), sort_keys=True, allow_unicode=True)


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


__all__ = ["Candidate", "Selection", "fingerprint", "load_case", "parse_target", "select"]
