"""Parse graph explain/profile dumps into GraphPlanIR and ``data.graph.plan`` facts.

Formats: Neptune Gremlin explain/profile, Neptune openCypher explain
(static or dynamic/details), Neptune SPARQL explain, Neo4j EXPLAIN/PROFILE
(cypher-shell table). The dump is text the operator produced or the
allowlisted collector fetched; parsing never contacts a database. A plan
counts as executed only when its format records runtime columns.
"""

from __future__ import annotations

import hashlib
import json
import re
from itertools import pairwise
from pathlib import Path
from typing import Any, get_args

from apiforge.adapters.inventory import CodeInventory
from apiforge.contracts.base import ContractError
from apiforge.contracts.graph_access import GraphPlanIR, PlanFormat, PlanOperator
from apiforge.core.ids import stable_id
from apiforge.core.models import Fact, SourceRef

FACT_KIND = "data.graph.plan"
FORMATS: tuple[str, ...] = get_args(PlanFormat)
FANOUT_ROWS = 1000
_EXECUTED = {
    "neptune-gremlin-explain": False,
    "neptune-gremlin-profile": True,
    "neptune-opencypher-static": False,
    "neptune-opencypher-dynamic": True,
    "neptune-sparql-explain": False,
    "neo4j-explain": False,
    "neo4j-profile": True,
}
_UNBOUNDED_ESTIMATE = re.compile(
    r"estimatedCardinality=INFINITY|rangeCountEstimate=9223372036854775807", re.IGNORECASE
)
_NOT_CONVERTED = re.compile(r"not converted into Neptune steps:\s*\[?([^\n\]]*)")
_WARNING = re.compile(r"^\s*WARNING:\s*(.+)$", re.MULTILINE)
_PREDICATES = re.compile(r"#\s*of predicates:\s*(\d+)")
_PATTERN_NODE = re.compile(r"(PatternNode\[[^\]]*\]|DFEPatternNode\[[^\]]*\])([^\n]*)")
_ALL_LABEL = re.compile(r"label\s+'ALL'")
_SPARQL_QUERY = re.compile(
    r"^\s*(PREFIX|SELECT|ASK|CONSTRUCT|DESCRIBE)\b", re.IGNORECASE | re.MULTILINE
)
_PROFILE_ROW = re.compile(r"^(\S.*?)\s{2,}(\d+)\s+(\d+)\s+([\d.]+)(\s+[\d.]+)?\s*$")
_NEO4J_FULL = re.compile(r"\b(AllNodesScan|CartesianProduct)\b")


class PlanError(ContractError):
    """A plan dump refused by format or parse; carries ``field`` and ``unlock``."""

    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


def _int(value: str) -> int | None:
    value = value.strip().replace(",", "")
    return int(float(value)) if re.fullmatch(r"\d+(\.\d+)?", value) else None


def detect_format(text: str) -> str:
    """Name the dump format from its own markers; unknown is a refusal."""
    if "Neptune Gremlin Explain" in text:
        return "neptune-gremlin-explain"
    if "Neptune Gremlin Profile" in text:
        return "neptune-gremlin-profile"
    if re.search(r"^\|\s*Operator\s*\|", text, re.MULTILINE):
        header = next(line for line in text.splitlines() if re.match(r"^\|\s*Operator\s*\|", line))
        cells = [cell.strip() for cell in header.strip("|").split("|")]
        return "neo4j-profile" if "Rows" in cells else "neo4j-explain"
    if "║" in text and re.search(r"║\s*ID\s*│", text):
        query = text.split("╔", 1)[0]
        if _SPARQL_QUERY.search(query.replace("Query:", "")):
            return "neptune-sparql-explain"
        return "neptune-opencypher-dynamic" if "Time (ms)" in text else "neptune-opencypher-static"
    raise PlanError(
        "AF-GDB-PLAN-FORMAT",
        "dump matches no known explain/profile format",
        field="path",
        unlock=f"pass --format with one of {', '.join(FORMATS)}",
    )


def _box_rows(text: str) -> tuple[list[str], list[list[str]]]:
    header: list[str] = []
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.startswith("║"):
            continue
        cells = [cell.strip() for cell in line.strip("║").split("│")]
        if cells and cells[0] == "ID":
            header = cells
            continue
        if header and len(cells) == len(header):
            rows.append(cells)
    return header, rows


def _box_operators(text: str) -> list[PlanOperator]:
    operators: list[PlanOperator] = []
    header, rows = _box_rows(text)
    index = {name: i for i, name in enumerate(header)}
    current: dict[str, Any] | None = None
    for cells in rows:
        if cells[index["ID"]] == "" and current is not None:
            current["arguments"] += " " + cells[index.get("Arguments", 0)]
            continue
        if current is not None:
            operators.append(PlanOperator(**current))
        current = {
            "op_id": f"{len(operators)}:{cells[index['ID']]}",
            "name": cells[index.get("Name", 0)],
            "arguments": cells[index["Arguments"]] if "Arguments" in index else "",
            "units_in": _int(cells[index["Units In"]]) if "Units In" in index else None,
            "units_out": _int(cells[index["Units Out"]]) if "Units Out" in index else None,
        }
    if current is not None:
        operators.append(PlanOperator(**current))
    return operators


def _split_top(text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in text:
        depth += {"(": 1, "[": 1, ")": -1, "]": -1}.get(char, 0)
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return parts


def _gremlin_operators(text: str, profile: bool) -> list[PlanOperator]:
    operators: list[PlanOperator] = []
    section = text.split("Optimized Traversal", 1)[-1]
    for index, match in enumerate(_PATTERN_NODE.finditer(section)):
        estimate = re.search(r"(estimatedCardinality|rangeCountEstimate)=([\w]+)", match.group(0))
        operators.append(
            PlanOperator(
                op_id=f"p{index}",
                name=match.group(1).split("[", 1)[0],
                arguments=match.group(1),
                estimate=estimate.group(2) if estimate else None,
            )
        )
    for raw in _NOT_CONVERTED.findall(section):
        for step in (part.strip() for part in _split_top(raw)):
            if step:
                operators.append(
                    PlanOperator(op_id=f"n{len(operators)}", name=step.split("(")[0], native=False)
                )
    if profile and "Traversal Metrics" in text:
        metrics = text.split("Traversal Metrics", 1)[1]
        previous: int | None = None
        for line in metrics.splitlines():
            row = _PROFILE_ROW.match(line.strip())
            if row is None or row.group(1).startswith(("Step", "TOTAL", ">")):
                continue
            count = int(row.group(2))
            operators.append(
                PlanOperator(
                    op_id=f"m{len(operators)}",
                    name=row.group(1).strip(),
                    units_in=previous,
                    units_out=count,
                )
            )
            previous = count
    return operators


def _neo4j_operators(text: str) -> list[PlanOperator]:
    lines = text.splitlines()
    header = next(line for line in lines if re.match(r"^\|\s*Operator\s*\|", line))
    bars = [i for i, char in enumerate(header) if char == "|"]
    spans = list(pairwise(bars))
    names = [header[a + 1 : b].strip() for a, b in spans]
    index = {name: i for i, name in enumerate(names)}
    parsed: list[dict[str, Any]] = []
    for line in lines:
        if not line.startswith("|") or line == header or len(line) < bars[-1]:
            continue
        cells = [line[a + 1 : b].strip() for a, b in spans]
        name = cells[0].replace("|", " ").replace("\\", " ").strip().lstrip("+").strip()
        if not name or name == "Operator" or "+" in name:
            continue
        parsed.append(
            {
                "name": name,
                "arguments": cells[index["Details"]] if "Details" in index else "",
                "estimate": cells[index["Estimated Rows"]] if "Estimated Rows" in index else None,
                "units_out": _int(cells[index["Rows"]]) if "Rows" in index else None,
            }
        )
    operators: list[PlanOperator] = []
    for position, row in enumerate(parsed):
        child = parsed[position + 1] if position + 1 < len(parsed) else None
        operators.append(
            PlanOperator(
                op_id=f"o{position}",
                units_in=child["units_out"] if child else None,
                **row,
            )
        )
    return operators


def _max_ratio(operators: list[PlanOperator]) -> float | None:
    ratios = [
        op.units_out / op.units_in
        for op in operators
        if op.units_in and op.units_out is not None and op.units_in > 0
    ]
    return round(max(ratios), 2) if ratios else None


def parse_plan(
    text: str, fmt: str | None = None, *, synthetic: bool = False
) -> tuple[GraphPlanIR, dict[str, Any]]:
    """Parse one dump; returns the IR and the fact measures it backs."""
    chosen = fmt or detect_format(text)
    if chosen not in FORMATS:
        raise PlanError(
            "AF-GDB-PLAN-FORMAT",
            f"format {chosen!r} is not supported",
            field="format",
            unlock=f"use one of {', '.join(FORMATS)}",
        )
    try:
        if chosen.startswith("neptune-gremlin"):
            operators = _gremlin_operators(text, chosen.endswith("profile"))
        elif chosen.startswith("neo4j"):
            operators = _neo4j_operators(text)
        else:
            operators = _box_operators(text)
    except (StopIteration, KeyError, ValueError) as exc:
        raise PlanError(
            "AF-GDB-PLAN-PARSE",
            f"{chosen} dump could not be parsed: {exc}",
            field="path",
            unlock="pass the unmodified explain/profile output or name the right --format",
        ) from exc
    if not operators:
        raise PlanError(
            "AF-GDB-PLAN-PARSE",
            f"{chosen} dump has no operators",
            field="path",
            unlock="pass the complete explain/profile output",
        )
    predicates = _PREDICATES.search(text)
    warnings = tuple(w.strip() for w in _WARNING.findall(text))
    executed = _EXECUTED[chosen] or (
        chosen == "neptune-sparql-explain" and any(op.units_in is not None for op in operators)
    )
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    plan = GraphPlanIR(
        id=stable_id("graphplan", {"sha": digest, "format": chosen}),
        format=chosen,  # type: ignore[arg-type]
        executed=executed,
        source_sha256=digest,
        synthetic=synthetic,
        operators=tuple(operators),
        warnings=warnings,
        predicate_count=int(predicates.group(1)) if predicates else None,
    )
    measures: dict[str, Any] = {
        "format": chosen,
        "executed": executed,
        "synthetic": synthetic,
        "operator_count": len(operators),
        "non_native_steps": any(not op.native for op in operators),
        "unbounded_estimate": bool(_UNBOUNDED_ESTIMATE.search(text)),
        "predicate_warning": any(
            re.search(r"predicate|edge label", warning, re.IGNORECASE) for warning in warnings
        ),
        "all_label_scan": any(
            _ALL_LABEL.search(op.arguments)
            for op in operators
            if "Scan" in op.name or "Join" in op.name
        ),
        "full_scan_operator": any(_NEO4J_FULL.search(op.name) for op in operators),
    }
    ratio = _max_ratio(operators) if executed else None
    if ratio is not None:
        measures["max_fanout_ratio"] = ratio
    return plan, measures


def extract_graph_plan(
    path: Path, fmt: str | None = None, *, synthetic: bool = False
) -> tuple[CodeInventory, GraphPlanIR]:
    """Read a dump file (text, or JSON with an ``output``/``results`` string)."""
    source = Path(path)
    if not source.is_file():
        raise PlanError(
            "AF-GDB-PLAN-PARSE",
            f"{source} is not a file",
            field="path",
            unlock="point --path at one explain/profile dump file",
        )
    raw = source.read_text(encoding="utf-8")
    text = raw
    if source.suffix == ".json":
        doc = json.loads(raw)
        text = str(doc.get("output") or doc.get("results") or "") if isinstance(doc, dict) else ""
    plan, measures = parse_plan(text, fmt, synthetic=synthetic)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    fact = Fact(
        fact_id=stable_id("fact", {"k": FACT_KIND, "p": source.name, **measures}),
        kind=FACT_KIND,
        source=SourceRef(path=source.name, sha256=digest, extractor="graph-plan"),
        measures=measures,
        attrs={},
    )
    inventory = CodeInventory(
        framework="graph-plan",
        root=str(source.parent),
        facts=(fact,),
        diagnostics=(),
        input_hashes={source.name: digest},
    )
    return inventory, plan
