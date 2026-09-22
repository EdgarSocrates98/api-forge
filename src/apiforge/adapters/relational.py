"""Static PostgreSQL/MySQL/MariaDB/RDS/Aurora access extraction.

The adapter reads source text only. It records declared SQL and client
signals, never executes a query and never infers an index or a query plan.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory, static_execution
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_PROVIDERS = {
    "postgres": ("postgres", "psycopg", "asyncpg", "pgx", "jdbc:postgresql", "org.postgresql"),
    "mysql": ("mysql", "pymysql", "mysqlclient", "mysql-connector", "jdbc:mysql", "com.mysql"),
}
_SQL_RE = re.compile(
    r"\b(SELECT|INSERT|UPDATE|DELETE|UPSERT|MERGE|CREATE|ALTER|DROP)\b[\s\S]{0,500}",
    re.IGNORECASE,
)
_CALL_RE = re.compile(r"\b(execute|executemany|query|raw|fetchone|fetchall|begin|commit|rollback)\s*\(", re.IGNORECASE)
_POOL_RE = re.compile(r"\b(pool|connectionpool|hikaricp|sqlalchemy\.create_engine|pgbouncer)\b", re.IGNORECASE)
_TX_RE = re.compile(r"\b(begin|commit|rollback|transaction|atomic)\b", re.IGNORECASE)
_PAGING_RE = re.compile(r"\b(limit|offset|fetch\s+first|keyset|cursor)\b", re.IGNORECASE)


def _fact(kind: str, rel: str, digest: str, line: int, **measures: Any) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"k": kind, "p": rel, "l": line, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, line=line, extractor="relational"),
        measures={key: value for key, value in measures.items() if value is not None},
        attrs={},
    )


def extract_relational(project_root: Path, database: str = "postgres") -> CodeInventory:
    """Extract declared relational access patterns for PostgreSQL or MySQL."""

    if database not in _PROVIDERS:
        raise ValueError(f"unsupported relational database {database!r}")
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    tokens = _PROVIDERS[database]
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix.lower() not in {".py", ".java", ".go", ".sql", ".ts", ".js"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            diagnostics.append(Diagnostic(
                code="AF-RELATIONAL-READ",
                status=FindingStatus.UNRESOLVED,
                message=f"{path}: {exc}",
                source=SourceRef(
                    path=str(path.relative_to(root)),
                    sha256="0" * 64,
                    extractor="relational",
                ),
            ))
            continue
        lowered = text.lower()
        if path.suffix.lower() != ".sql" and not any(token in lowered for token in tokens):
            continue
        rel = path.relative_to(root).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        input_hashes[rel] = digest
        for match in _SQL_RE.finditer(text):
            query = " ".join(match.group(0).split())
            operation = query.split(" ", 1)[0].lower()
            line = text.count("\n", 0, match.start()) + 1
            facts.append(_fact(
                "data.relational.query", rel, digest, line,
                database=database, operation=operation, query=query[:500],
                parameterized="%s" in query or "?" in query or ":" in query,
                paginated=bool(_PAGING_RE.search(query)),
            ))
        for match in _CALL_RE.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            facts.append(_fact("data.relational.operation", rel, digest, line,
                               database=database, operation=match.group(1).lower()))
        if _POOL_RE.search(text):
            facts.append(_fact("data.relational.pool", rel, digest, 1, database=database, declared=True))
        if _TX_RE.search(text):
            facts.append(_fact("data.relational.transaction", rel, digest, 1, database=database, declared=True))
        if path.suffix.lower() != ".sql" and not any(
            fact.source.path == rel and fact.kind in {"data.relational.query", "data.relational.operation"}
            for fact in facts
        ):
            diagnostics.append(Diagnostic(
                code="AF-RELATIONAL-DYNAMIC-QUERY",
                status=FindingStatus.UNRESOLVED,
                message=f"{rel}: relational client signal found without a statically resolvable query or operation",
                source=SourceRef(path=rel, sha256=digest, extractor="relational"),
            ))
    return CodeInventory(
        framework=f"{database}-relational",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda fact: fact.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
        execution=static_execution(
            f"relational.{database}",
            input_hashes,
            tuple(diagnostics),
            limitations=("does not execute SQL", "does not prove query plan or index usage"),
        ),
    )


def extract_postgres(project_root: Path) -> CodeInventory:
    return extract_relational(project_root, "postgres")


def extract_mysql(project_root: Path) -> CodeInventory:
    return extract_relational(project_root, "mysql")


def extract_rds_access(project_root: Path) -> CodeInventory:
    """Scan both PostgreSQL and MySQL drivers under the declared RDS boundary."""
    postgres = extract_postgres(project_root)
    mysql = extract_mysql(project_root)
    return CodeInventory(
        framework="rds-relational",
        root=str(project_root),
        facts=tuple(sorted((*postgres.facts, *mysql.facts), key=lambda fact: fact.fact_id)),
        diagnostics=postgres.diagnostics + mysql.diagnostics,
        input_hashes={**postgres.input_hashes, **mysql.input_hashes},
        execution=static_execution(
            "rds-relational",
            {**postgres.input_hashes, **mysql.input_hashes},
            postgres.diagnostics + mysql.diagnostics,
            limitations=("does not connect to RDS", "does not execute SQL"),
        ),
    )
