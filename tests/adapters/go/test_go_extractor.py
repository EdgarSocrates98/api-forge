from pathlib import Path

import pytest

from apiforge.adapters.go.extractor import extract_go

FIXTURE = Path("tests/fixtures/go_orders")


@pytest.fixture
def inventory():
    return extract_go(FIXTURE)


def _routes(inventory):
    return {
        (f.measures["method"], f.measures["path"]): f
        for f in inventory.facts
        if f.kind == "code.route"
    }


def test_chi_routes_extracted(inventory) -> None:
    routes = _routes(inventory)
    for expected in (
        ("get", "/orders"),
        ("post", "/orders"),
        ("get", "/orders/{id}"),
        ("delete", "/orders/{id}"),
    ):
        assert expected in routes
    fact = routes[("post", "/orders")]
    assert fact.attrs["handler"] == "createOrder"
    assert fact.source is not None and fact.source.extractor == "go"


def test_chi_route_scope_joins_prefix(inventory) -> None:
    routes = _routes(inventory)
    assert ("get", "/admin/stats") in routes


def test_net_http_mux_routes(inventory) -> None:
    routes = _routes(inventory)
    assert ("get", "/health") in routes
    assert ("get", "/ready") in routes
    assert ("any", "/legacy") in routes


def test_gin_routes(inventory) -> None:
    routes = _routes(inventory)
    assert ("get", "/ping") in routes
    assert ("post", "/echo") in routes


def test_dynamic_shapes_are_unresolved(inventory) -> None:
    codes = [d.code for d in inventory.diagnostics]
    # non-literal path + unbindable Mount => at least two unresolved diagnostics
    assert codes.count("AF-GO-UNRESOLVED-ROUTE") >= 2


def test_broken_file_parsed_partial(inventory) -> None:
    codes = [d.code for d in inventory.diagnostics]
    assert "AF-GO-PARSE" in codes


def test_every_go_file_is_hashed(inventory) -> None:
    assert len(inventory.input_hashes) == 5
    assert all(k.endswith(".go") for k in inventory.input_hashes)


def test_framework_name(inventory) -> None:
    assert inventory.framework == "go"
