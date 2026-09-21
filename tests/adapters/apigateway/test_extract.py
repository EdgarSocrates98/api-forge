import shutil
from pathlib import Path

import pytest

from apiforge.adapters.apigateway.extract import extract_apigateway

FIXTURE = Path("tests/fixtures/aws/apigateway")


@pytest.fixture
def inventory():
    return extract_apigateway(FIXTURE)


def _facts(inventory, kind):
    return [f for f in inventory.facts if f.kind == kind]


def test_api_fact(inventory) -> None:
    api = _facts(inventory, "aws.apigateway.api")
    assert len(api) == 1
    assert api[0].measures["name"] == "orders"
    assert api[0].source is not None and api[0].source.extractor == "apigateway-dump"


def test_resource_method_facts(inventory) -> None:
    resources = _facts(inventory, "aws.apigateway.resource")
    paths = {f.measures["path"] for f in resources}
    assert "/orders" in paths and "/orders/{id}" in paths
    orders = next(f for f in resources if f.measures["path"] == "/orders")
    methods = orders.attrs["methods"]
    assert methods["GET"]["authorizationType"] == "AWS_IAM"
    assert methods["POST"]["authorizationType"] == "NONE"
    assert methods["POST"]["apiKeyRequired"] is True


def test_stage_facts(inventory) -> None:
    stages = _facts(inventory, "aws.apigateway.stage")
    prod = next(f for f in stages if f.measures["stage"] == "prod")
    assert prod.attrs["access_log"] is True
    assert prod.attrs["cache_cluster"] is True
    dev = next(f for f in stages if f.measures["stage"] == "dev")
    assert dev.attrs["access_log"] is False
    assert dev.attrs["cache_cluster"] is False


def test_authorizer_fact(inventory) -> None:
    auths = _facts(inventory, "aws.apigateway.authorizer")
    assert len(auths) == 1
    assert auths[0].attrs["type"] == "TOKEN"


def test_every_dump_file_hashed(inventory) -> None:
    assert len(inventory.input_hashes) == 5  # 4 data files + manifest


def test_missing_dump_is_named(tmp_path: Path) -> None:
    dump = tmp_path / "dump"
    shutil.copytree(FIXTURE, dump)
    (dump / "stages.json").unlink()
    inventory = extract_apigateway(dump)
    codes = [d.code for d in inventory.diagnostics]
    assert "AF-GW-DUMP-MISSING" in codes


def test_malformed_dump_is_named(tmp_path: Path) -> None:
    dump = tmp_path / "dump"
    shutil.copytree(FIXTURE, dump)
    (dump / "resources.json").write_text("{ not json", encoding="utf-8")
    inventory = extract_apigateway(dump)
    codes = [d.code for d in inventory.diagnostics]
    assert "AF-GW-DUMP-INVALID" in codes


def test_framework_name(inventory) -> None:
    assert inventory.framework == "apigateway-dump"
