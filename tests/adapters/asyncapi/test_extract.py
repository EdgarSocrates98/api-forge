"""extract_asyncapi: AsyncAPI 2.x/3.x -> asyncapi.* facts; $ref never followed."""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.adapters.asyncapi.extract import extract_asyncapi

V2_DOC = """\
asyncapi: "2.6.0"
servers:
  prod:
    host: broker.example.com
    protocol: kafka
channels:
  orders/created:
    publish:
      message:
        $ref: "#/components/messages/OrderCreated"
    subscribe:
      message:
        name: OrderRequested
components:
  messages:
    OrderCreated:
      payload:
        type: object
"""

V3_DOC = """\
asyncapi: "3.0.0"
servers:
  prod:
    host: wss://api.example.com
    protocol: websocket
channels:
  orderEvents:
    address: orders.events
operations:
  onOrderCreated:
    action: receive
    channel:
      $ref: "#/channels/orderEvents"
    messages:
      - $ref: "#/components/messages/OrderCreated"
"""


def _write(tmp_path: Path, text: str, name: str = "asyncapi.yaml") -> Path:
    doc = tmp_path / name
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text, encoding="utf-8")
    return doc


def test_v2_publish_subscribe_map_to_send_receive(tmp_path: Path) -> None:
    inv = extract_asyncapi(_write(tmp_path, V2_DOC))
    assert inv.framework == "asyncapi"
    ops = {f.measures["operation"]: f for f in inv.facts if f.kind == "asyncapi.operation"}
    # 2.x: publish on channel = provider sends; subscribe = provider receives.
    assert ops["publish"].attrs["action"] == "send"
    assert ops["subscribe"].attrs["action"] == "receive"
    server = next(f for f in inv.facts if f.kind == "asyncapi.server")
    assert server.attrs["protocol"] == "kafka"
    channel = next(f for f in inv.facts if f.kind == "asyncapi.channel")
    assert channel.measures["name"] == "orders/created"


def test_v3_operations(tmp_path: Path) -> None:
    inv = extract_asyncapi(_write(tmp_path, V3_DOC))
    op = next(f for f in inv.facts if f.kind == "asyncapi.operation")
    assert op.measures["operation"] == "onOrderCreated"
    assert op.attrs["action"] == "receive"
    assert op.attrs["channel"] == "#/channels/orderEvents"
    channel = next(f for f in inv.facts if f.kind == "asyncapi.channel")
    assert channel.attrs["address"] == "orders.events"


def test_refs_become_named_diagnostics(tmp_path: Path) -> None:
    inv = extract_asyncapi(_write(tmp_path, V2_DOC))
    refs = [d for d in inv.diagnostics if d.code == "AF-ASYNC-UNRESOLVED"]
    assert refs
    assert all("dereferenced" in d.message for d in refs)


def test_unknown_version_is_diagnostic(tmp_path: Path) -> None:
    doc = _write(tmp_path, 'asyncapi: "4.0.0"\nchannels: {}\n')
    inv = extract_asyncapi(doc)
    assert [d.code for d in inv.diagnostics] == ["AF-ASYNC-VERSION"]
    assert inv.facts == ()


def test_malformed_document_is_diagnostic(tmp_path: Path) -> None:
    doc = _write(tmp_path, "info:\n  title: nope\n")  # no asyncapi key
    inv = extract_asyncapi(doc)
    assert [d.code for d in inv.diagnostics] == ["AF-ASYNC-INVALID"]


def test_deterministic_ids(tmp_path: Path) -> None:
    a = extract_asyncapi(_write(tmp_path / "a", V2_DOC))
    b = extract_asyncapi(_write(tmp_path / "b", V2_DOC))
    assert [f.fact_id for f in a.facts] == [f.fact_id for f in b.facts]


@pytest.mark.parametrize("doc", [V2_DOC, V3_DOC])
def test_facts_carry_input_hash(tmp_path: Path, doc: str) -> None:
    inv = extract_asyncapi(_write(tmp_path, doc))
    assert all(f.source.sha256 == inv.input_hashes["asyncapi.yaml"] for f in inv.facts)
