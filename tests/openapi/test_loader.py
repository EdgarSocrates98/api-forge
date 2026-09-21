import json
from pathlib import Path

import pytest

from apiforge.core.io import sha256_file
from apiforge.openapi.loader import OpenApiLoadError, load_openapi

FIXTURES = Path("tests/fixtures/openapi")


def test_loads_operations_in_stable_order() -> None:
    document = load_openapi(FIXTURES / "orders-v1.yaml")
    assert document.version == "3.1.0"
    assert [(op.method, op.path) for op in document.operations] == [
        ("get", "/orders"),
        ("post", "/orders"),
    ]


def test_rejects_unsupported_openapi_version(tmp_path: Path) -> None:
    path = tmp_path / "openapi.yaml"
    path.write_text(
        "openapi: 3.0.3\ninfo: {title: x, version: '1'}\npaths: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-UNSUPPORTED-VERSION"):
        load_openapi(path)


def test_safe_loader_rejects_python_tag() -> None:
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(FIXTURES / "unsafe-tag.yaml")


def test_rejects_yaml_aliases() -> None:
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(FIXTURES / "aliased.yaml")


def test_rejects_duplicate_keys(tmp_path: Path) -> None:
    path = tmp_path / "dup.yaml"
    path.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths: {}\npaths: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(path)


def test_rejects_merge_keys(tmp_path: Path) -> None:
    path = tmp_path / "merge.yaml"
    path.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\nbase: &b {a: 1}\nmerged: {<<: *b}\n",
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-YAML"):
        load_openapi(path)


def test_rejects_non_mapping_root(tmp_path: Path) -> None:
    path = tmp_path / "list.yaml"
    path.write_text("- just\n- a\n- list\n", encoding="utf-8")
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-NOT-MAPPING"):
        load_openapi(path)


def test_json_duplicate_keys_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dup.json"
    path.write_text(
        '{"openapi": "3.1.0", "openapi": "3.1.0", "info": {"title": "x", "version": "1"}, "paths": {}}',
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-JSON"):
        load_openapi(path)


def test_json_non_finite_numbers_rejected(tmp_path: Path) -> None:
    path = tmp_path / "nan.json"
    path.write_text(
        '{"openapi": "3.1.0", "info": {"title": "x", "version": "1"}, '
        '"paths": {"/x": {"get": {"x": NaN}}}}',
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-INVALID-JSON"):
        load_openapi(path)


def test_trailing_slashes_are_distinct_operations(tmp_path: Path) -> None:
    path = tmp_path / "slashes.yaml"
    path.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths:\n"
        "  /orders:\n    get: {operationId: a, responses: {}}\n"
        "  /orders/:\n    get: {operationId: b, responses: {}}\n",
        encoding="utf-8",
    )
    document = load_openapi(path)
    assert [(op.method, op.path) for op in document.operations] == [
        ("get", "/orders"),
        ("get", "/orders/"),
    ]


def test_duplicate_method_path_pair_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "dupop.yaml"
    path.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths:\n"
        "  /orders:\n    get: {operationId: a, responses: {}}\n"
        "    GET: {operationId: b, responses: {}}\n",
        encoding="utf-8",
    )
    with pytest.raises(OpenApiLoadError, match="AF-OPENAPI-DUPLICATE-OPERATION"):
        load_openapi(path)


def test_raw_operation_and_components_preserved() -> None:
    document = load_openapi(FIXTURES / "orders-v1.yaml")
    post = next(op for op in document.operations if op.method == "post")
    assert post.raw["requestBody"]["required"] is True
    assert document.components["schemas"]["Order"]["required"] == ("id", "total")
    assert post.operation_id == "createOrder"


def test_operation_identity_is_deterministic() -> None:
    first = load_openapi(FIXTURES / "orders-v1.yaml")
    second = load_openapi(FIXTURES / "orders-v1.yaml")
    assert [op.fact_id for op in first.operations] == [op.fact_id for op in second.operations]
    assert len({op.fact_id for op in first.operations}) == len(first.operations)
    for op in first.operations:
        assert op.fact_id.startswith("fact:")
        assert op.source.sha256 == first.sha256 == sha256_file(FIXTURES / "orders-v1.yaml")


def test_error_string_starts_with_code(tmp_path: Path) -> None:
    path = tmp_path / "bad.yaml"
    path.write_text("openapi: 2.0\n", encoding="utf-8")
    with pytest.raises(OpenApiLoadError) as excinfo:
        load_openapi(path)
    assert str(excinfo.value).startswith(excinfo.value.code)


def test_json_input_loads(tmp_path: Path) -> None:
    doc = {
        "openapi": "3.1.0",
        "info": {"title": "x", "version": "1"},
        "paths": {"/orders": {"get": {"operationId": "list", "responses": {}}}},
    }
    path = tmp_path / "doc.json"
    path.write_text(json.dumps(doc), encoding="utf-8")
    document = load_openapi(path)
    assert [(op.method, op.path) for op in document.operations] == [("get", "/orders")]
