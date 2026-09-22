"""Static OpenSearch/Redshift access extraction."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Literal, cast

from apiforge.adapters.inventory import CodeInventory, static_execution
from apiforge.contracts.stubs import AnalyticalAccessIR
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_TOKENS = {
    "opensearch": ("opensearch", "elasticsearch", "_search", "search_body", "query_string"),
    "redshift": ("redshift", "redshift-data", "jdbc:redshift", "copy ", "unload "),
}
_OPS = {
    "search": re.compile(r"\b(search|_search|msearch|query_string|scan)\b", re.IGNORECASE),
    "aggregate": re.compile(r"\b(aggs|aggregations|group\s+by|count\(|sum\(|avg\()\b", re.IGNORECASE),
    "write": re.compile(r"\b(index|bulk|insert|update|delete|copy|unload)\b", re.IGNORECASE),
    "pagination": re.compile(r"\b(from|size|search_after|scroll|limit|offset)\b", re.IGNORECASE),
    "partition": re.compile(r"\b(partition|distkey|sortkey|shard|routing)\b", re.IGNORECASE),
}
_NAME_RE = re.compile(r"(?:index|table|IndexName|TableName)\s*[=:,]\s*[\"']([^\"']+)", re.IGNORECASE)


def _fact(kind: str, rel: str, digest: str, line: int, **measures: Any) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"k": kind, "p": rel, "l": line, **measures}),
        kind=kind, source=SourceRef(path=rel, sha256=digest, line=line, extractor="analytical"),
        measures={key: value for key, value in measures.items() if value is not None}, attrs={},
    )


def extract_analytical(project_root: Path, engine: str = "opensearch") -> CodeInventory:
    if engine not in _TOKENS:
        raise ValueError(f"unsupported analytical engine {engine!r}")
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in {".py", ".java", ".go", ".ts", ".js", ".sql", ".json"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            diagnostics.append(Diagnostic(code="AF-ANALYTICAL-READ", status=FindingStatus.UNRESOLVED, message=f"{path}: {exc}", source=SourceRef(path=str(path.relative_to(root)), sha256="0" * 64, extractor="analytical")))
            continue
        lowered = text.lower()
        sql_candidate = path.suffix.lower() == ".sql" and engine == "redshift" and "select" in lowered
        if not sql_candidate and not any(token.lower() in lowered for token in _TOKENS[engine]):
            continue
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        input_hashes[rel] = digest
        for match in _NAME_RE.finditer(text):
            facts.append(_fact("data.analytical.name", rel, digest, text.count("\n", 0, match.start()) + 1, engine=engine, name=match.group(1)))
        for operation, pattern in _OPS.items():
            found = pattern.search(text)
            if found:
                facts.append(_fact("data.analytical.operation", rel, digest, text.count("\n", 0, found.start()) + 1, engine=engine, operation=operation))
        if not any(fact.source.path == rel and fact.kind == "data.analytical.name" for fact in facts):
            diagnostics.append(Diagnostic(
                code="AF-ANALYTICAL-DYNAMIC-NAME",
                status=FindingStatus.UNRESOLVED,
                message=f"{rel}: analytical usage found without a statically resolvable index or table",
                source=SourceRef(path=rel, sha256=digest, extractor="analytical"),
            ))
    return CodeInventory(
        framework=f"{engine}-analytical",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda fact: fact.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
        execution=static_execution(
            f"analytical.{engine}",
            input_hashes,
            tuple(diagnostics),
            limitations=("does not execute search or SQL", "does not prove shard or partition health"),
        ),
    )


def build_analytical_ir(inventory: CodeInventory, *, engine: str, provider: str = "aws") -> AnalyticalAccessIR:
    names = tuple(sorted({str(f.measures["name"]) for f in inventory.facts if f.kind == "data.analytical.name"}))
    operations = tuple(sorted({str(f.measures["operation"]) for f in inventory.facts if f.kind == "data.analytical.operation"}))
    risks: set[str] = set()
    if "search" in operations and "pagination" not in operations:
        risks.add("unbounded-search-possible")
    if "aggregate" in operations and "partition" not in operations:
        risks.add("aggregation-partition-signal-absent")
    return AnalyticalAccessIR(
        id=stable_id("analytical", {"root": inventory.root, "engine": engine}),
        engine=cast(Literal["opensearch", "redshift"], engine), provider=provider,
        indexes_or_tables=names, operations=operations,
        query_signals=tuple(sorted(set(operations) & {"aggregate", "pagination", "partition"})),
        risk_findings=tuple(sorted(risks)),
        unresolved=tuple(sorted(d.code for d in inventory.diagnostics)),
    )


def extract_opensearch(project_root: Path) -> CodeInventory:
    return extract_analytical(project_root, "opensearch")


def extract_redshift(project_root: Path) -> CodeInventory:
    return extract_analytical(project_root, "redshift")
