"""extract_graphql: SDL -> graphql.type + graphql.field facts."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.graphql_.extract import extract_graphql

SDL = """\
type Query {
  order(id: ID!): Order
  orders(limit: Int): [Order!]!
  legacyOrder: Order @deprecated(reason: "use order")
}

type Mutation {
  createOrder(input: OrderInput!): Order!
}

type Order {
  id: ID!
  total: Float!
}

input OrderInput {
  sku: String!
  qty: Int!
}
"""


def _write(tmp_path: Path, text: str) -> Path:
    doc = tmp_path / "schema.graphql"
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text, encoding="utf-8")
    return doc


def test_types_and_root_fields(tmp_path: Path) -> None:
    inv = extract_graphql(_write(tmp_path, SDL))
    assert inv.framework == "graphql"
    types = {f.measures["type"]: f for f in inv.facts if f.kind == "graphql.type"}
    assert types["Query"].attrs["root"] is True
    assert types["Query"].attrs["deprecated_fields"] == 1
    assert types["OrderInput"].attrs["kind"] == "inputobject"
    fields = {
        (f.measures["operation"], f.measures["field"]): f
        for f in inv.facts
        if f.kind == "graphql.field"
    }
    assert fields[("query", "order")].attrs["returns"] == "Order"
    assert fields[("query", "order")].attrs["args"] == ("id",)
    assert fields[("mutation", "createOrder")].attrs["returns"] == "Order!"
    assert fields[("query", "legacyOrder")].attrs["deprecated"] is True


def test_invalid_sdl_is_diagnostic(tmp_path: Path) -> None:
    inv = extract_graphql(_write(tmp_path, "type Query {\n"))
    assert [d.code for d in inv.diagnostics] == ["AF-GQL-INVALID"]
    assert inv.facts == ()


def test_deterministic(tmp_path: Path) -> None:
    a = extract_graphql(_write(tmp_path / "a", SDL))
    b = extract_graphql(_write(tmp_path / "b", SDL))
    assert [f.fact_id for f in a.facts] == [f.fact_id for f in b.facts]
