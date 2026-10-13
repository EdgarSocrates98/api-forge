from pathlib import Path

from apiforge.core.models import FindingStatus
from apiforge.openapi.diff import diff_contracts
from apiforge.openapi.loader import load_openapi

FIXTURES = Path("tests/fixtures/openapi")


def _load(name: str):
    return load_openapi(FIXTURES / name)


def test_classifies_breaking_and_non_breaking_changes() -> None:
    changes = diff_contracts(_load("orders-v1.yaml"), _load("orders-v2-breaking.yaml"))
    observed = {(c.code, c.breaking) for c in changes}
    assert ("AF-BREAKING-OPERATION-REMOVED", True) in observed
    assert ("AF-BREAKING-RESPONSE-REMOVED", True) in observed
    assert ("AF-BREAKING-REQUEST-REQUIRED-ADDED", True) in observed
    assert ("AF-COMPAT-RESPONSE-OPTIONAL-ADDED", False) in observed


def test_change_ids_and_order_are_deterministic() -> None:
    first = diff_contracts(_load("orders-v1.yaml"), _load("orders-v2-breaking.yaml"))
    second = diff_contracts(_load("orders-v1.yaml"), _load("orders-v2-breaking.yaml"))
    assert [c.change_id for c in first] == [c.change_id for c in second]
    keys = [(c.code, c.path, c.method or "", c.pointer) for c in first]
    assert keys == sorted(keys)
    assert len({c.change_id for c in first}) == len(first)


def test_operation_added_is_compatible(tmp_path: Path) -> None:
    v2 = tmp_path / "added.yaml"
    v2.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '2'}\npaths:\n"
        "  /orders:\n"
        "    get: {operationId: listOrders, responses: {'200': {description: ok}}}\n"
        "    post:\n      operationId: createOrder\n"
        "      requestBody:\n        required: true\n"
        "        content:\n          application/json:\n"
        "            schema: {$ref: '#/components/schemas/Order'}\n"
        "      responses: {'200': {description: ok}, '201': {description: ok}}\n"
        "  /health:\n    get: {operationId: health, responses: {'200': {description: ok}}}\n"
        "components:\n  schemas:\n    Order:\n      type: object\n"
        "      required: [id, total]\n"
        "      properties: {id: {type: string}, total: {type: number}, note: {type: string}}\n",
        encoding="utf-8",
    )
    changes = diff_contracts(_load("orders-v1.yaml"), _load(str(v2)))
    added = [c for c in changes if c.code == "AF-COMPAT-OPERATION-ADDED"]
    assert len(added) == 1
    assert added[0].path == "/health"
    assert added[0].breaking is False


def test_external_ref_is_unresolved_not_guessed(tmp_path: Path) -> None:
    ext = tmp_path / "ext.yaml"
    ext.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths:\n"
        "  /orders:\n    post:\n      operationId: create\n"
        "      requestBody:\n        required: true\n"
        "        content:\n          application/json:\n"
        "            schema: {$ref: 'https://example.com/schemas.yaml#/Order'}\n"
        "      responses: {'201': {description: ok}}\n",
        encoding="utf-8",
    )
    changes = diff_contracts(_load("orders-v2-breaking.yaml"), _load(str(ext)))
    unresolved = [c for c in changes if c.code == "AF-OPENAPI-REF-UNRESOLVED"]
    assert unresolved
    assert all(c.status == FindingStatus.UNRESOLVED for c in unresolved)
    assert all(c.breaking is False for c in unresolved)


def test_missing_component_ref_is_unresolved(tmp_path: Path) -> None:
    missing = tmp_path / "missing.yaml"
    missing.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths:\n"
        "  /orders:\n    post:\n      operationId: create\n"
        "      requestBody:\n        required: true\n"
        "        content:\n          application/json:\n"
        "            schema: {$ref: '#/components/schemas/Ghost'}\n"
        "      responses: {'201': {description: ok}}\n",
        encoding="utf-8",
    )
    changes = diff_contracts(_load("orders-v2-breaking.yaml"), _load(str(missing)))
    assert any(c.code == "AF-OPENAPI-REF-UNRESOLVED" for c in changes)


def test_cyclic_local_refs_are_bounded(tmp_path: Path) -> None:
    cyclic = tmp_path / "cyclic.yaml"
    cyclic.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '1'}\npaths:\n"
        "  /orders:\n    post:\n      operationId: create\n"
        "      requestBody:\n        required: true\n"
        "        content:\n          application/json:\n"
        "            schema: {$ref: '#/components/schemas/A'}\n"
        "      responses: {'201': {description: ok}}\n"
        "components:\n  schemas:\n"
        "    A: {$ref: '#/components/schemas/B'}\n"
        "    B: {$ref: '#/components/schemas/A'}\n",
        encoding="utf-8",
    )
    changes = diff_contracts(_load("orders-v2-breaking.yaml"), _load(str(cyclic)))
    cyclic_hits = [c for c in changes if c.code == "AF-OPENAPI-REF-UNRESOLVED"]
    assert cyclic_hits
    assert all(c.status == FindingStatus.UNRESOLVED for c in cyclic_hits)


def test_identical_documents_produce_no_changes() -> None:
    assert diff_contracts(_load("orders-v1.yaml"), _load("orders-v1.yaml")) == ()


def test_required_removed_from_request_is_compatible(tmp_path: Path) -> None:
    relaxed = tmp_path / "relaxed.yaml"
    relaxed.write_text(
        "openapi: 3.1.0\ninfo: {title: x, version: '2'}\npaths:\n"
        "  /orders:\n    post:\n      operationId: createOrder\n"
        "      requestBody:\n        required: true\n"
        "        content:\n          application/json:\n"
        "            schema: {$ref: '#/components/schemas/Order'}\n"
        "      responses: {'201': {description: ok}}\n"
        "components:\n  schemas:\n    Order:\n      type: object\n"
        "      required: [id]\n"
        "      properties: {id: {type: string}, total: {type: number}, note: {type: string}}\n",
        encoding="utf-8",
    )
    changes = diff_contracts(_load("orders-v2-breaking.yaml"), _load(str(relaxed)))
    assert any(
        c.code == "AF-COMPAT-REQUEST-REQUIRED-REMOVED" and c.breaking is False for c in changes
    )
