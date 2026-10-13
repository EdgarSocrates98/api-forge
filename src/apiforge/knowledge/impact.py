"""§29 knowledge impact graph — source -> pack -> rule -> skill -> eval.

Every edge derives from declared data only: `pack.yaml` rule_ids and
areas, `source_authority.yaml` receipts, `evals.yaml` expectations, the
rule catalog and skill manifests that name rule ids. Relations that have
no declared carrier — today the agent -> knowledge edge — are listed in
``unresolved`` instead of being guessed.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from apiforge.contracts.graph import EdgeKind, GraphEdge, GraphNode, NodeKind
from apiforge.contracts.knowledge import KnowledgeImpactReport
from apiforge.knowledge.loader import load_packs

_RULE_ID = re.compile(r"AF-[A-Z][A-Z0-9]*-[0-9]{3}")


def _node(node_id: str, kind: NodeKind, **props: Any) -> GraphNode:
    return GraphNode(id=node_id, kind=kind, props=props)


def _edge(from_id: str, to_id: str, kind: EdgeKind) -> GraphEdge:
    return GraphEdge(from_id=from_id, to_id=to_id, kind=kind)


def _skill_rule_refs(skills_root: Path) -> dict[str, set[str]]:
    """Map skill name -> declared rule ids referenced by its manifest."""
    refs: dict[str, set[str]] = {}
    if not skills_root.is_dir():
        return refs
    for manifest in sorted(skills_root.glob("*/SKILL.md")):
        ids = set(_RULE_ID.findall(manifest.read_text(encoding="utf-8")))
        if ids:
            refs[manifest.parent.name] = ids
    return refs


def build_knowledge_impact(
    packs_root: Path,
    *,
    skills_root: Path | None = None,
    catalog: dict[str, Any] | None = None,
) -> KnowledgeImpactReport:
    """Build the declared relation graph over local knowledge packs."""
    packs = load_packs(packs_root)
    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []
    unresolved: list[str] = []
    catalog_ids = set(catalog) if catalog is not None else None

    for domain, pack in sorted(packs.items()):
        pack_id = f"pack:{domain}"
        nodes[pack_id] = _node(
            pack_id,
            NodeKind.KNOWLEDGE,
            domain=pack.domain,
            pack_version=pack.version,
            areas=tuple(pack.areas),
        )
        for source in pack.sources:
            source_id = f"source:{source.authority}:{source.name}"
            nodes[source_id] = _node(
                source_id,
                NodeKind.SOURCE,
                name=source.name,
                url=source.url,
                authority=source.authority,
                verified=source.verified,
            )
            edges.append(_edge(pack_id, source_id, EdgeKind.BACKED_BY))
        for rule_id in pack.rule_ids:
            rule_node_id = f"rule:{rule_id}"
            if rule_node_id not in nodes:
                in_catalog = catalog_ids is None or rule_id in catalog_ids
                nodes[rule_node_id] = _node(
                    rule_node_id, NodeKind.RULE, rule_id=rule_id, in_catalog=in_catalog
                )
                if catalog_ids is not None and rule_id not in catalog_ids:
                    unresolved.append(
                        f"{domain}: rule {rule_id} is declared but absent from the catalog"
                    )
            edges.append(_edge(pack_id, rule_node_id, EdgeKind.CONTAINS))
        for entry in pack.evals:
            eval_id = str(entry.get("id", ""))
            if not eval_id:
                unresolved.append(f"{domain}: evals.yaml entry without id")
                continue
            eval_node_id = f"eval:{eval_id}"
            nodes[eval_node_id] = _node(
                eval_node_id,
                NodeKind.TEST,
                eval_id=eval_id,
                eval_type=str(entry.get("type", "")),
            )
            edges.append(_edge(pack_id, eval_node_id, EdgeKind.CONTAINS))
            expect = entry.get("expect")
            if isinstance(expect, dict) and expect.get("kind") == "rule":
                target = str(expect.get("id", ""))
                if target:
                    rule_node_id = f"rule:{target}"
                    if rule_node_id not in nodes:
                        nodes[rule_node_id] = _node(
                            rule_node_id,
                            NodeKind.RULE,
                            rule_id=target,
                            in_catalog=catalog_ids is None or target in catalog_ids,
                        )
                    edges.append(_edge(eval_node_id, rule_node_id, EdgeKind.VERIFIED_BY))

    skill_refs = _skill_rule_refs(skills_root) if skills_root else {}
    known_rules = {node.props["rule_id"] for node in nodes.values() if node.kind is NodeKind.RULE}
    for skill_name, rule_ids in sorted(skill_refs.items()):
        hits = rule_ids & set(known_rules)
        if not hits:
            continue
        skill_id = f"skill:{skill_name}"
        nodes.setdefault(skill_id, _node(skill_id, NodeKind.SKILL, name=skill_name))
        for rule_id in sorted(hits):
            edges.append(_edge(skill_id, f"rule:{rule_id}", EdgeKind.USES))

    unresolved.append(
        "agent -> knowledge: no declared agent->pack relation exists in agents/*.md; "
        "the edge is named, never inferred"
    )
    totals = {
        "packs": len(packs),
        "nodes": len(nodes),
        "edges": len(edges),
        "sources": sum(len(pack.sources) for pack in packs.values()),
        "rules": sum(1 for n in nodes.values() if n.kind is NodeKind.RULE),
        "evals": sum(1 for n in nodes.values() if n.kind is NodeKind.TEST),
        "skills": sum(1 for n in nodes.values() if n.kind is NodeKind.SKILL),
    }
    return KnowledgeImpactReport(
        nodes=tuple(nodes.values()),
        edges=tuple(edges),
        totals=totals,
        unresolved=tuple(unresolved),
    )
