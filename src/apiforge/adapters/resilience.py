"""Static resilience scan — FASE 12 detection surface.

Regex-based scan of .py/.java/.go sources for the statically checkable
resilience signals: HTTP calls and their timeout, retry wrappers and
their backoff/jitter, connection pools, and project-level declarations
(circuit breaker, graceful shutdown, DLQ, idempotency). Pattern matches
are heuristic — every fact says what was *seen*, and the summary fact
turns project-level absence into a measure the rules can check.

What static scan cannot see (retry storms, load shedding behavior,
cancellation propagation) is documented as limitation, never inferred.
"""

from __future__ import annotations

import re
from pathlib import Path

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import (
    Diagnostic,
    Fact,
    FindingStatus,
    JsonValue,
    SourceRef,
)


def _digest(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


_HTTP_CALL = re.compile(
    r"(requests\.(get|post|put|delete|patch|head)\(|httpx\.(get|post|put|delete|patch|"
    r"AsyncClient|Client)\(|\.(getForObject|getForEntity|postForObject|postForEntity|"
    r"exchange)\(|http\.(Get|Post|Do)\(|fetch\(|axios\.(get|post|put|delete)\()",
    re.IGNORECASE,
)
_TIMEOUT_ARG = re.compile(r"timeout\s*[=:]|Timeout|setTimeout|context\.WithTimeout", re.IGNORECASE)
_RETRY = re.compile(
    r"@retry|retrying|Retryable|RetryPolicy|go-retry|"
    r"resilience4j\.retry|for\s+\w+\s+in\s+range\(.*retry",
    re.IGNORECASE,
)
_IMPORT_LINE = re.compile(r"^\s*(import|from)\s")
_BACKOFF = re.compile(r"backoff|wait_exponential|ExponentialBackOff|expo\b", re.IGNORECASE)
_JITTER = re.compile(r"jitter|full_jitter|random", re.IGNORECASE)
_MUTATING = re.compile(r"\bpost\b|\bput\b|\bdelete\b|\bpatch\b|postForObject|postForEntity|insert|update|write", re.IGNORECASE)
_CB = re.compile(r"CircuitBreaker|circuit_breaker|pybreaker|gobreaker|resilience4j|Polly|hystrix", re.IGNORECASE)
_POOL = re.compile(r"pool|Pool|maxPoolSize|pool_maxsize|MaxIdleConns|connection_pool", re.IGNORECASE)
_POOL_BOUND = re.compile(r"pool_maxsize\s*=|maxPoolSize|MaxIdleConns|Pool\(.*max|max_connections|maxsize", re.IGNORECASE)
_SHUTDOWN = re.compile(
    r"@PreDestroy|addShutdownHook|signal\.signal|Shutdown\(|graceful|atexit\.register|"
    r"defer\s+\w+\.Close\(\)",
    re.IGNORECASE,
)
_DLQ = re.compile(r"dead.?letter|deadLetter|DeadLetterQueue|dlq\b|redrive", re.IGNORECASE)
_IDEM = re.compile(r"idempot|Idempotency-Key|X-Idempotency|dedup|deduplication", re.IGNORECASE)


def _scan_file(path: Path, rel: str, digest: str) -> list[Fact]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    lines = text.splitlines()
    facts: list[Fact] = []
    fid = 0

    def fact(kind: str, line: int, **measures: JsonValue) -> None:
        nonlocal fid
        fid += 1
        facts.append(
            Fact(
                fact_id=stable_id(
                    "fact", {"k": kind, "p": rel, "l": line, **measures}
                ),
                kind=kind,
                measures=dict(measures),
                attrs={},
                source=SourceRef(
                    path=rel, sha256=digest, line=line, extractor="resilience"
                ),
            )
        )

    window = 6  # lines after a call site where timeout/retry config plausibly sits
    for i, line in enumerate(lines):
        ctx = "\n".join(lines[i : i + window])
        if _HTTP_CALL.search(line):
            method = "unknown"
            m = re.search(r"\.(get|post|put|delete|patch|head)\b|\.(Get|Post|Do)\(", line)
            if m:
                method = m.group(1).upper()
            fact(
                "resilience.http_call",
                i + 1,
                has_timeout=bool(_TIMEOUT_ARG.search(ctx)),
                method=method,
                heuristic="pattern-match",
            )
        if _RETRY.search(line) and not _IMPORT_LINE.match(line):
            fact(
                "resilience.retry",
                i + 1,
                has_backoff=bool(_BACKOFF.search(ctx)),
                has_jitter=bool(_JITTER.search(ctx)),
                mutating_target=bool(_MUTATING.search(ctx)),
                heuristic="pattern-match",
            )
        if _POOL.search(line) and not _POOL_BOUND.search(ctx):
            fact("resilience.pool", i + 1, bounded=False, heuristic="pattern-match")
    return facts


def _summary(facts: list[Fact], all_text: str) -> Fact:
    import hashlib

    digest = hashlib.sha256(all_text.encode("utf-8", errors="replace")).hexdigest()
    http_calls = sum(1 for f in facts if f.kind == "resilience.http_call")
    retries = sum(1 for f in facts if f.kind == "resilience.retry")
    pools = sum(1 for f in facts if f.kind == "resilience.pool")
    dependency_surface = int(http_calls + retries + pools > 0)
    measures = {
        "http_calls": http_calls,
        "retries": retries,
        "dependency_surface": dependency_surface,
        "circuit_breaker_declared": int(bool(_CB.search(all_text))),
        "graceful_shutdown_declared": int(bool(_SHUTDOWN.search(all_text))),
        "dlq_declared": int(bool(_DLQ.search(all_text))),
        "idempotency_declared": int(bool(_IDEM.search(all_text))),
        # gaps: absence counts only where dependency surface exists — a file
        # with no calls has no breaker to miss (absence is not a defect there)
        "circuit_breaker_gap": int(
            dependency_surface and not _CB.search(all_text)
        ),
        "graceful_shutdown_gap": int(
            dependency_surface and not _SHUTDOWN.search(all_text)
        ),
        "idempotency_gap": int(
            dependency_surface and not _IDEM.search(all_text)
        ),
    }
    return Fact(
        fact_id=stable_id("fact", {"k": "resilience.summary", **measures}),
        kind="resilience.summary",
        measures=measures,
        attrs={},
        source=SourceRef(path=".", sha256=digest, extractor="resilience"),
    )


def extract_resilience(project_root: Path) -> CodeInventory:
    """Scan a project tree for resilience signals — no code executes."""
    root = Path(project_root)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    all_text_parts: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink() or path.suffix not in {
            ".py", ".java", ".go",
        }:
            continue
        rel = path.relative_to(root).as_posix()
        digest = _digest(path)
        input_hashes[rel] = digest
        file_facts = _scan_file(path, rel, digest)
        facts.extend(file_facts)
        try:
            all_text_parts.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    all_text = "\n".join(all_text_parts)
    if facts or all_text:
        facts.append(_summary(facts, all_text))
    diagnostics.append(
        Diagnostic(
            code="AF-RES-HEURISTIC",
            status=FindingStatus.UNRESOLVED,
            message=(
                "resilience signals are pattern-matched; absence of a match "
                "is a blind spot, not proof of absence"
            ),
        )
    )
    return CodeInventory(
        framework="resilience",
        root=str(root),
        facts=tuple(sorted(facts, key=lambda f: f.fact_id)),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )
