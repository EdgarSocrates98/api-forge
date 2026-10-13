from pathlib import Path

import pytest

from apiforge.adapters.spring.extractor import extract_spring

FIXTURE = Path("tests/fixtures/spring_orders")


@pytest.fixture
def inventory():
    return extract_spring(FIXTURE)


def _routes(inventory):
    return {
        (f.measures["method"], f.measures["path"]): f
        for f in inventory.facts
        if f.kind == "code.route"
    }


def test_controller_routes_extracted(inventory) -> None:
    routes = _routes(inventory)
    assert ("get", "/orders") in routes
    assert ("get", "/orders/{id}") in routes
    assert ("post", "/orders") in routes
    assert ("delete", "/orders/{id}") in routes
    fact = routes[("post", "/orders")]
    assert fact.attrs["handler"] == "OrderController.create"
    assert fact.source is not None and fact.source.extractor == "spring"


def test_router_function_route_extracted(inventory) -> None:
    routes = _routes(inventory)
    assert ("get", "/orders/status") in routes
    assert routes[("get", "/orders/status")].attrs["via"] == "router-function"


def test_jaxrs_route_extracted(inventory) -> None:
    routes = _routes(inventory)
    assert ("get", "/health") in routes
    assert routes[("get", "/health")].attrs["via"] == "jaxrs"


def test_dynamic_path_is_unresolved(inventory) -> None:
    codes = [d.code for d in inventory.diagnostics]
    assert "AF-SPRING-UNRESOLVED-ROUTE" in codes


def test_every_java_file_is_hashed(inventory) -> None:
    assert len(inventory.input_hashes) == 4
    assert all(k.endswith(".java") for k in inventory.input_hashes)


def test_framework_name(inventory) -> None:
    assert inventory.framework == "spring"
