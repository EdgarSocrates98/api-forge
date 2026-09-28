"""`evidence://` refs over the case graph (§60): one node, one hop, on demand.

``evidence://finding/<id>`` returns the finding, refs to the facts that back
it and the rule it violates — never the whole chain. Each neighbor is another
``evidence://`` ref the caller can resolve next. Facts that point at a source
line also carry a ``ctx://`` ref to a small slice of that file.
"""

from __future__ import annotations

import re
from pathlib import Path

from apiforge.contracts.base import ContractError
from apiforge.contracts.economy_extras import EvidenceNode

KINDS = {"operation": "operation:", "fact": "fact:", "finding": "finding:", "rule": "rule:"}
_REF = re.compile(r"^evidence://(operation|fact|finding|rule)/(.+)$")
_SLICE = 4


def _refusal(code: str, detail: str, unlock: str) -> ContractError:
    error = ContractError(code, detail)
    error.field = "ref"  # type: ignore[attr-defined]
    error.unlock = unlock  # type: ignore[attr-defined]
    return error


def to_ref(node_id: str) -> str | None:
    for kind, prefix in KINDS.items():
        if node_id.startswith(prefix):
            return f"evidence://{kind}/{node_id.removeprefix(prefix)}"
    return None


def resolve(root: Path, ref: str, *, case_dir: Path | None = None) -> EvidenceNode:
    from apiforge.context.gateway.levels import load_case, load_graph
    from apiforge.context.gateway.refs import CtxStore

    match = _REF.match(ref.strip())
    if match is None:
        raise _refusal(
            "AF-EVIDENCE-REF-INVALID",
            f"{ref!r} is not evidence://{{operation|fact|finding|rule}}/<id>",
            "pass a ref such as evidence://finding/<id> or one returned as a neighbor",
        )
    kind, value = match.groups()
    root = Path(root).resolve()
    case_path = Path(case_dir).resolve() if case_dir else root / ".apiforge" / "case"
    case = load_case(case_path)
    if case is None:
        raise _refusal(
            "AF-EVIDENCE-NOT-FOUND",
            f"no case.json under {case_path}",
            f"run `apiforge analyze --out-dir {case_path}` first",
        )
    nodes, edges, _ = load_graph(root, case_path)
    node_id = value if value.startswith(KINDS[kind]) else KINDS[kind] + value
    node = next((item for item in nodes if item.id == node_id), None)
    if node is None:
        raise _refusal(
            "AF-EVIDENCE-NOT-FOUND",
            f"{node_id} is not in the case graph",
            "resolve a ref listed as a neighbor or taken from findings/facts",
        )
    neighbors = sorted(
        {
            ref_id
            for edge in edges
            if node_id in (edge.from_id, edge.to_id)
            for ref_id in [to_ref(edge.to_id if edge.from_id == node_id else edge.from_id)]
            if ref_id is not None
        }
    )
    source_ref: str | None = None
    props = dict(node.props)
    path, line = props.get("path"), props.get("line")
    if kind == "fact" and isinstance(path, str) and isinstance(line, int):
        inputs = case.get("inputs") or {}
        project = root / str(inputs.get("project", ""))
        file = project / path if (project / path).is_file() else root / path
        if file.is_file():
            lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
            start = max(1, line - _SLICE)
            text = chr(10).join(lines[start - 1 : line + _SLICE])
            source_ref = CtxStore(root).put(f"{path}:{start}\n{text}")
    return EvidenceNode(
        ref=f"evidence://{kind}/{node_id.removeprefix(KINDS[kind])}",
        kind=kind,
        node_id=node_id,
        props=props,
        neighbors=tuple(neighbors),
        source_ref=source_ref,
    )


__all__ = ["KINDS", "resolve", "to_ref"]
