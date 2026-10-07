"""`collect neptune-explain`: allowlist, guards before any client, receipt (AT-010..012)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from apiforge.collectors.graph_explain import (
    ALLOWED_OPERATIONS,
    GraphCollectError,
    collect_neptune_explain,
    plan_request,
)

ENDPOINT = "https://db.cluster-ro.neptune.amazonaws.com:8182"


class Untouchable:
    def __getattr__(self, name: str) -> Any:
        raise AssertionError(f"client touched: {name}")


class Recorder:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def __getattr__(self, name: str) -> Any:
        def call(**kwargs: Any) -> dict[str, Any]:
            self.calls.append((name, kwargs))
            return {"output": "Neptune Gremlin Explain", "ResponseMetadata": {"x": 1}}

        return call


def test_default_gremlin_is_non_executing_explain(tmp_path: Path) -> None:
    client = Recorder()
    manifest = collect_neptune_explain(
        "gremlin", "g.V().hasLabel('p').limit(1)", ENDPOINT, tmp_path, client=client
    )
    assert client.calls == [
        ("execute_gremlin_explain_query", {"gremlinQuery": "g.V().hasLabel('p').limit(1)"})
    ]
    assert manifest.meta["executes_query"] is False
    assert manifest.meta["reader_verified"] is False
    assert "ResponseMetadata" not in json.loads(
        (tmp_path / "plan.json").read_text(encoding="utf-8")
    )


def test_default_cypher_is_static(tmp_path: Path) -> None:
    client = Recorder()
    collect_neptune_explain(
        "opencypher", "MATCH (n:P) RETURN n LIMIT 1", ENDPOINT, tmp_path, client=client
    )
    assert client.calls[0][1]["explainMode"] == "static"


def test_profile_with_reader_executes_on_allowlisted_op(tmp_path: Path) -> None:
    client = Recorder()
    manifest = collect_neptune_explain(
        "gremlin",
        "g.V().hasLabel('p').limit(1)",
        ENDPOINT,
        tmp_path,
        profile=True,
        reader_endpoint=ENDPOINT,
        client=client,
    )
    assert client.calls[0][0] == "execute_gremlin_profile_query"
    assert manifest.meta["executes_query"] is True
    assert client.calls[0][0] in ALLOWED_OPERATIONS


@pytest.mark.parametrize(
    ("language", "query", "kwargs", "code"),
    [
        ("gremlin", "g.addV('p')", {}, "AF-GDB-PROFILE-MUTATION"),
        ("opencypher", "MATCH (n:P) DETACH DELETE n", {}, "AF-GDB-PROFILE-MUTATION"),
        ("gremlin", "g.V().limit(1)", {"profile": True}, "AF-GDB-PROFILE-READER"),
        (
            "gremlin",
            "g.V().limit(1)",
            {"profile": True, "reader_endpoint": "https://writer:8182"},
            "AF-GDB-PROFILE-READER",
        ),
        (
            "gremlin",
            "g.V().limit(1)",
            {"profile": True, "reader_endpoint": ENDPOINT, "query_dynamic": True},
            "AF-GDB-PROFILE-DYNAMIC",
        ),
        ("sparql", "SELECT * WHERE {?s ?p ?o}", {}, "AF-GDB-EXPLAIN-SPARQL"),
        ("cypher", "MATCH (n) RETURN n", {}, "AF-GDB-COLLECT-ARG"),
        ("gremlin", "   ", {}, "AF-GDB-COLLECT-ARG"),
    ],
)
def test_refusals_never_touch_the_client(
    tmp_path: Path, language: str, query: str, kwargs: dict[str, Any], code: str
) -> None:
    with pytest.raises(GraphCollectError) as caught:
        collect_neptune_explain(language, query, ENDPOINT, tmp_path, client=Untouchable(), **kwargs)
    assert caught.value.code == code
    assert caught.value.field and caught.value.unlock
    assert not (tmp_path / "plan.json").exists()


def test_allowlist_is_closed() -> None:
    assert ALLOWED_OPERATIONS == {
        "execute_gremlin_explain_query",
        "execute_gremlin_profile_query",
        "execute_open_cypher_explain_query",
    }
    operation, _, executes = plan_request("opencypher", "MATCH (n:P) RETURN n LIMIT 1", ENDPOINT)
    assert operation in ALLOWED_OPERATIONS and executes is False
