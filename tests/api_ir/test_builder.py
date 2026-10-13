import pytest

from apiforge.adapters.fastapi.models import FastApiInventory
from apiforge.api_ir.builder import build_api_model
from apiforge.openapi.models import OpenApiDocument


def test_operation_keeps_contract_and_code_provenance(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    operation = model.operation("post", "/orders")
    assert operation.contract is not None
    assert operation.contract.source.sha256 == openapi_document.sha256
    assert operation.code_projections
    assert all(item.fact_id for item in operation.code_projections)


def test_model_order_is_stable(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    first = build_api_model(openapi_document, fastapi_inventory).model_dump_json()
    second = build_api_model(openapi_document, fastapi_inventory).model_dump_json()
    assert first == second


def test_code_only_operation_has_no_contract_projection(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    delete = model.operation("delete", "/orders/{order_id}")
    assert delete.contract is None
    assert delete.contract_projections == ()
    assert len(delete.code_projections) == 1


def test_missing_operation_raises_key_error(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    with pytest.raises(KeyError):
        model.operation("get", "/absent")


def test_input_hashes_cover_contract_and_all_sources(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    assert model.input_hashes[f"contract:{openapi_document.source_path}"] == openapi_document.sha256
    for rel, digest in fastapi_inventory.input_hashes.items():
        assert model.input_hashes[f"code:{rel}"] == digest


def test_operations_sorted_and_schema_version(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    keys = [(op.path, op.method) for op in model.operations]
    assert keys == sorted(keys)
    assert model.schema_version == "1"
    assert model.generator.startswith("apiforge ")


def test_diagnostics_from_both_sources(
    openapi_document: OpenApiDocument, fastapi_inventory: FastApiInventory
) -> None:
    model = build_api_model(openapi_document, fastapi_inventory)
    codes = {d.code for d in model.diagnostics}
    assert codes <= {"AF-OPENAPI-UNSUPPORTED", "AF-FASTAPI-DYNAMIC-ROUTE"} or not codes
    assert model.diagnostics == tuple(
        sorted(
            model.diagnostics,
            key=lambda d: (
                d.code,
                d.source.path if d.source else "",
                d.source.line if d.source and d.source.line else 0,
            ),
        )
    )
