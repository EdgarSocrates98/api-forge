"""`collect neptune-explain` — read-only explain/profile over a closed allowlist.

Every guard runs before a client exists, so a refusal never touches the
network. Default plans do not run the query (Gremlin explain, openCypher
``explainMode=static``). ``profile=True`` executes the query, so it also
requires mutation-free literal text and a declared reader endpoint equal
to the target endpoint. SPARQL explain has no ``neptunedata`` operation
and is refused: import a dump with ``model graph-explain`` instead.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from apiforge.adapters.graph_ import cypher, gremlin
from apiforge.collectors.manifest import CollectError, CollectManifest, write_artifact

ALLOWED_OPERATIONS = frozenset(
    {
        "execute_gremlin_explain_query",
        "execute_gremlin_profile_query",
        "execute_open_cypher_explain_query",
    }
)
LANGUAGES = ("gremlin", "opencypher", "sparql")


class GraphCollectError(CollectError):
    """Collector refusal with the ``field`` it concerns and how to ``unlock`` it."""

    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


def plan_request(
    language: str,
    query: str,
    endpoint: str,
    *,
    profile: bool = False,
    reader_endpoint: str | None = None,
    query_dynamic: bool = False,
) -> tuple[str, dict[str, str], bool]:
    """Choose the allowlisted operation and its kwargs, or refuse."""
    if language not in LANGUAGES:
        raise GraphCollectError(
            "AF-GDB-COLLECT-ARG",
            f"language {language!r} not in {LANGUAGES}",
            field="language",
            unlock="pass --language gremlin or --language opencypher",
        )
    if language == "sparql":
        raise GraphCollectError(
            "AF-GDB-EXPLAIN-SPARQL",
            "neptunedata exposes no SPARQL explain operation",
            field="language",
            unlock="run explain=static against /sparql yourself and import it with `model graph-explain`",
        )
    if not query.strip() or not endpoint.strip():
        raise GraphCollectError(
            "AF-GDB-COLLECT-ARG",
            "query and endpoint must be non-empty",
            field="query" if not query.strip() else "endpoint",
            unlock="pass --query (or --query-file) and --endpoint",
        )
    analysis = (gremlin.analyze if language == "gremlin" else cypher.analyze)(query)
    if analysis["mutation"]:
        raise GraphCollectError(
            "AF-GDB-PROFILE-MUTATION",
            "query mutates the graph; API Forge only explains read queries",
            field="query",
            unlock="submit the read-only part of the query",
        )
    if profile:
        if query_dynamic:
            raise GraphCollectError(
                "AF-GDB-PROFILE-DYNAMIC",
                "an executing plan needs the literal query text",
                field="query",
                unlock="pass the final literal query; templated text cannot be proven read-only",
            )
        if reader_endpoint is None or reader_endpoint.strip() != endpoint.strip():
            raise GraphCollectError(
                "AF-GDB-PROFILE-READER",
                "profile/dynamic explain executes the query",
                field="reader_endpoint",
                unlock="pass --reader-endpoint equal to --endpoint, naming a reader instance",
            )
    if language == "gremlin":
        operation = "execute_gremlin_profile_query" if profile else "execute_gremlin_explain_query"
        return operation, {"gremlinQuery": query}, profile
    mode = "dynamic" if profile else "static"
    return (
        "execute_open_cypher_explain_query",
        {"openCypherQuery": query, "explainMode": mode},
        profile,
    )


def _client(endpoint: str) -> Any:
    try:
        import boto3  # type: ignore[import-not-found]
    except ImportError as exc:
        raise CollectError(
            "AF-COLLECT-AWS",
            "boto3 is not installed; install the 'aws' extra (pip install apiforge[aws])",
        ) from exc
    return boto3.client("neptunedata", endpoint_url=endpoint)


def _payload(response: Any) -> dict[str, Any]:
    if not isinstance(response, dict):
        return {"output": str(response)}
    out: dict[str, Any] = {}
    for key, value in response.items():
        if key == "ResponseMetadata":
            continue
        out[key] = value.read().decode("utf-8") if hasattr(value, "read") else value
    return out


def collect_neptune_explain(
    language: str,
    query: str,
    endpoint: str,
    out_dir: Path,
    *,
    profile: bool = False,
    reader_endpoint: str | None = None,
    query_dynamic: bool = False,
    now: str | None = None,
    client: Any = None,
) -> CollectManifest:
    """Fetch one plan through the allowlist and record a receipt."""
    operation, kwargs, executes = plan_request(
        language,
        query,
        endpoint,
        profile=profile,
        reader_endpoint=reader_endpoint,
        query_dynamic=query_dynamic,
    )
    if operation not in ALLOWED_OPERATIONS:
        raise GraphCollectError(
            "AF-GDB-COLLECT-OP",
            f"{operation} is outside the read-only allowlist",
            field="operation",
            unlock="only explain/profile operations listed in ALLOWED_OPERATIONS are callable",
        )
    if client is None:
        client = _client(endpoint)
    try:
        response = getattr(client, operation)(**kwargs)
    except CollectError:
        raise
    except Exception as exc:  # boto3 ClientError subclasses vary; name them all
        raise CollectError("AF-COLLECT-AWS", f"{operation} failed: {exc}") from exc
    manifest = CollectManifest(source="neptune-explain", collected_at=now)
    name, digest = write_artifact(out_dir, "plan.json", _payload(response))
    manifest.record(name, digest)
    manifest.meta.update(
        {
            "operation": operation,
            "language": language,
            "executes_query": executes,
            "endpoint": endpoint,
            "reader_declared": bool(profile),
            "reader_verified": False,
            "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest(),
        }
    )
    manifest.write(out_dir)
    return manifest
