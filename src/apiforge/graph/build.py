"""Populate the graph from existing artifacts — case, facts, findings, tasks.

Every node and edge is derived from a named input artifact; nothing is
inferred beyond explicit references (evidence lists, rule ids, route
method+path equality). The output is deterministic: same inputs, same bytes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.graph import (
    EdgeKind,
    GraphEdge,
    GraphExport,
    GraphNode,
    NodeKind,
)
from apiforge.graph.store import node_sha256, write_graph


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError("AF-GRAPH-INPUT", f"{path}: {exc}") from exc


def _node(node_id: str, kind: NodeKind, **props: Any) -> GraphNode:
    node = GraphNode(id=node_id, kind=kind, props={k: v for k, v in props.items() if v is not None})
    return node.model_copy(update={"sha256": node_sha256(node)})


def _edge(from_id: str, to_id: str, kind: EdgeKind) -> GraphEdge:
    return GraphEdge(from_id=from_id, to_id=to_id, kind=kind)


def _contract_node_id(case: dict[str, Any], case_dir: Path) -> str | None:
    hashes = case.get("input_hashes") or {}
    for key, digest in sorted(hashes.items()):
        if str(key).startswith("contract"):
            return f"contract:{str(digest)[:16]}"
    contract_rel = (case.get("inputs") or {}).get("contract")
    if not contract_rel:
        return None
    contract_path = Path(str(contract_rel))
    if not contract_path.is_absolute():
        contract_path = case_dir / contract_path
    if contract_path.is_file():
        digest = hashlib.sha256(contract_path.read_bytes()).hexdigest()
        return f"contract:{digest[:16]}"
    return f"contract:unresolved:{contract_rel}"


def _task_nodes(tasks_root: Path) -> list[GraphNode]:
    nodes: list[GraphNode] = []
    tasks_dir = tasks_root / ".apiforge" / "tasks"
    if not tasks_dir.is_dir():
        tasks_dir = tasks_root / "tasks"
    if not tasks_dir.is_dir():
        return nodes
    from apiforge.core.yaml import StrictYamlError, load_yaml_mapping

    for spec_path in sorted(tasks_dir.glob("*/task.yaml")):
        try:
            data = load_yaml_mapping(
                spec_path.read_text(encoding="utf-8"), source=str(spec_path)
            )
        except (StrictYamlError, ValueError):
            continue
        task_id = str(data.get("id") or spec_path.parent.name)
        nodes.append(
            _node(
                f"task:{task_id}",
                NodeKind.TASK,
                state=data.get("state"),
                revision=data.get("revision"),
                strategy=data.get("strategy"),
                outcome=data.get("outcome"),
            )
        )
    return nodes


def build_graph(
    case_dir: Path,
    out_dir: Path,
    tasks_root: Path | None = None,
) -> GraphExport:
    """Build nodes/edges from a case directory; persist canonical JSONL."""
    case_dir = Path(case_dir)
    manifest_path = case_dir / "case.json"
    if not manifest_path.is_file():
        raise ContractError("AF-GRAPH-NO-CASE", f"no case.json under {case_dir}")
    case = _read_json(manifest_path)
    case_id = f"case:{case.get('case_id', 'unknown')}"

    nodes: list[GraphNode] = [
        _node(
            case_id,
            NodeKind.CASE,
            generator=case.get("generator"),
            diagnostics_count=case.get("diagnostics_count"),
        )
    ]
    edges: list[GraphEdge] = []
    built_from = ["case.json"]

    contract_id = _contract_node_id(case, case_dir)
    if contract_id:
        nodes.append(_node(contract_id, NodeKind.CONTRACT))
        edges.append(_edge(case_id, contract_id, EdgeKind.DERIVED_FROM))
    project_rel = (case.get("inputs") or {}).get("project")
    if project_rel:
        project_id = f"project:{project_rel}"
        nodes.append(_node(project_id, NodeKind.PROJECT))
        edges.append(_edge(case_id, project_id, EdgeKind.DERIVED_FROM))

    ir_path = case_dir / "api-ir.json"
    route_facts: dict[tuple[str, str], str] = {}
    if ir_path.is_file():
        built_from.append("api-ir.json")
        ir = _read_json(ir_path)
        for op in ir.get("operations") or []:
            op_id = f"operation:{str(op.get('method', '')).upper()} {op.get('path', '')}"
            nodes.append(
                _node(op_id, NodeKind.OPERATION, method=op.get("method"), path=op.get("path"))
            )
            if contract_id:
                edges.append(_edge(op_id, contract_id, EdgeKind.DESCRIBED_BY))

    facts_path = case_dir / "facts.json"
    if facts_path.is_file():
        built_from.append("facts.json")
        for fact in _read_json(facts_path).get("facts") or []:
            fact_id = str(fact.get("fact_id"))
            source = fact.get("source") or {}
            nodes.append(
                _node(
                    fact_id,
                    NodeKind.FACT,
                    fact_kind=fact.get("kind"),
                    path=source.get("path"),
                    line=source.get("line"),
                )
            )
            if fact.get("kind") == "code.route":
                measures = fact.get("measures") or {}
                key = (str(measures.get("method", "")).lower(), str(measures.get("path", "")))
                route_facts[key] = fact_id

    for node in nodes:
        if node.kind is NodeKind.OPERATION:
            parts = str(node.props.get("method", "")), str(node.props.get("path", ""))
            key = (parts[0].lower(), parts[1])
            route_fact = route_facts.get(key)
            if route_fact:
                edges.append(_edge(node.id, route_fact, EdgeKind.IMPLEMENTED_BY))

    findings_path = case_dir / "findings.json"
    if findings_path.is_file():
        built_from.append("findings.json")
        for finding in _read_json(findings_path).get("findings") or []:
            finding_id = str(finding.get("finding_id"))
            nodes.append(
                _node(
                    finding_id,
                    NodeKind.FINDING,
                    rule_id=finding.get("rule_id"),
                    severity=finding.get("severity"),
                    status=finding.get("status"),
                    title=finding.get("title"),
                )
            )
            for fact_id in finding.get("evidence") or []:
                edges.append(_edge(finding_id, str(fact_id), EdgeKind.BACKED_BY))
            rule_id = finding.get("rule_id")
            if rule_id:
                rule_node = f"rule:{rule_id}"
                nodes.append(_node(rule_node, NodeKind.RULE))
                edges.append(_edge(finding_id, rule_node, EdgeKind.VIOLATES))

    if tasks_root is not None:
        nodes.extend(_task_nodes(Path(tasks_root)))
        built_from.append("tasks/")

    digests = write_graph(out_dir, nodes, edges)
    return GraphExport(
        nodes_sha256=digests["nodes_sha256"],
        edges_sha256=digests["edges_sha256"],
        node_count=digests["node_count"],
        edge_count=digests["edge_count"],
        built_from=tuple(built_from),
    )
