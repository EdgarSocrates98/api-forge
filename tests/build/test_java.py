from pathlib import Path

import pytest

from apiforge.build.java import BuildError, operation_to_sources
from apiforge.openapi.loader import load_openapi

CONTRACT = Path("tests/fixtures/openapi/orders-v1.yaml")


@pytest.fixture
def document():
    return load_openapi(CONTRACT)


def test_create_order_generates_controller_and_dto(document) -> None:
    sources = operation_to_sources(document, "createOrder")
    controller = sources["src/main/java/com/apiforge/generated/CreateOrderController.java"]
    dto = sources["src/main/java/com/apiforge/generated/dto/Order.java"]
    assert '@PostMapping("/orders")' in controller
    assert "@RequestBody Order body" in controller
    assert "ResponseEntity<Order>" in controller
    assert "@RestController" in controller
    assert "public record Order(String id, BigDecimal total, String note)" in dto


def test_list_orders_array_response(document) -> None:
    sources = operation_to_sources(document, "listOrders")
    controller = sources["src/main/java/com/apiforge/generated/ListOrdersController.java"]
    assert '@GetMapping("/orders")' in controller
    assert "ResponseEntity<List<Order>>" in controller
    assert "import java.util.List;" in controller
    # no requestBody -> no @RequestBody parameter
    assert "@RequestBody" not in controller


def test_path_variable_extracted(tmp_path: Path) -> None:
    f = tmp_path / "c.yaml"
    f.write_text(
        """
openapi: 3.1.0
info: {title: t, version: "1"}
paths:
  /orders/{id}:
    get:
      operationId: getOrder
      responses:
        "200": {description: ok}
""",
        encoding="utf-8",
    )
    doc = load_openapi(f)
    sources = operation_to_sources(doc, "getOrder")
    controller = next(iter(sources.values()))
    assert '@GetMapping("/orders/{id}")' in controller
    assert '@PathVariable("id") String id' in controller


def test_missing_operation_is_named(document) -> None:
    with pytest.raises(BuildError, match="AF-BUILD-OP-MISSING"):
        operation_to_sources(document, "nonexistent")


def test_untyped_property_is_named(tmp_path: Path) -> None:
    doc_yaml = """
openapi: 3.1.0
info: {title: t, version: "1"}
paths:
  /x:
    post:
      operationId: makeX
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: "#/components/schemas/X"}
      responses:
        "200": {description: ok}
components:
  schemas:
    X:
      type: object
      properties:
        a: {}
"""
    f = tmp_path / "c.yaml"
    f.write_text(doc_yaml, encoding="utf-8")
    doc = load_openapi(f)
    with pytest.raises(BuildError, match="AF-BUILD-SCHEMA-MISSING"):
        operation_to_sources(doc, "makeX")


def test_output_is_deterministic(document) -> None:
    assert operation_to_sources(document, "createOrder") == operation_to_sources(
        document, "createOrder"
    )
