"""extract_protobuf: *.proto -> proto.* facts; no protoc, no codegen."""

from __future__ import annotations

from pathlib import Path

from apiforge.adapters.protobuf.extract import extract_protobuf

ORDERS = """\
syntax = "proto3";

package orders.v1;

import "common/money.proto";

// An order aggregate.
message Order {
  string id = 1;
  double total = 2;
  repeated string items = 3;
}

message CreateRequest {
  string sku = 1;
}

service OrderService {
  rpc GetOrder (GetRequest) returns (Order);
  rpc CreateOrder (CreateRequest) returns (Order);
  rpc WatchOrders (stream GetRequest) returns (stream Order);
}

message GetRequest {
  string id = 1;
}
"""


def test_services_rpcs_messages(tmp_path: Path) -> None:
    (tmp_path / "orders.proto").write_text(ORDERS, encoding="utf-8")
    inv = extract_protobuf(tmp_path)
    assert inv.framework == "protobuf"
    rpcs = {f.measures["rpc"]: f for f in inv.facts if f.kind == "proto.rpc"}
    assert set(rpcs) == {"GetOrder", "CreateOrder", "WatchOrders"}
    watch = rpcs["WatchOrders"]
    assert watch.attrs["client_streaming"] is True
    assert watch.attrs["server_streaming"] is True
    assert rpcs["GetOrder"].attrs["request"] == "GetRequest"
    msgs = {f.measures["message"]: f for f in inv.facts if f.kind == "proto.message"}
    assert msgs["Order"].attrs["fields"] == 3
    file = next(f for f in inv.facts if f.kind == "proto.file")
    assert file.attrs["package"] == "orders.v1"
    assert file.attrs["imports"] == ("common/money.proto",)


def test_unbalanced_braces_is_diagnostic(tmp_path: Path) -> None:
    (tmp_path / "bad.proto").write_text(
        "message Broken {\n  string id = 1;\n", encoding="utf-8"
    )
    inv = extract_protobuf(tmp_path)
    assert any(d.code == "AF-PROTO-PARSE" for d in inv.diagnostics)


def test_empty_dir_is_named_blind_spot(tmp_path: Path) -> None:
    inv = extract_protobuf(tmp_path)
    assert [d.code for d in inv.diagnostics] == ["AF-PROTO-EMPTY"]


def test_deterministic(tmp_path: Path) -> None:
    (tmp_path / "orders.proto").write_text(ORDERS, encoding="utf-8")
    a, b = extract_protobuf(tmp_path), extract_protobuf(tmp_path)
    assert [f.fact_id for f in a.facts] == [f.fact_id for f in b.facts]
