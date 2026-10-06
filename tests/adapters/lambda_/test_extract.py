"""Lambda dump extractor: facts offline, env names only, named diagnostics."""

import json
from pathlib import Path

from apiforge.adapters.lambda_.extract import extract_lambda
from apiforge.collectors.lambda_ import collect
from apiforge.collectors.manifest import CollectError
from apiforge.core.models import FindingStatus

FIXTURE = Path(__file__).resolve().parents[2] / "fixtures" / "lambda_dump"


def test_function_facts_extracted() -> None:
    inv = extract_lambda(FIXTURE)
    (fact,) = inv.facts
    assert fact.kind == "aws.lambda.function"
    assert fact.measures["function_name"] == "orders-api"
    assert fact.attrs["runtime"] == "python3.12"
    assert fact.attrs["memory_mb"] == 256
    assert fact.attrs["env_keys"] == ("LOG_LEVEL", "ORDERS_TABLE")
    assert "secret-value-not-read" not in str(fact.attrs)


def test_missing_dump_is_named_diagnostic(tmp_path: Path) -> None:
    inv = extract_lambda(tmp_path)
    (diag,) = inv.diagnostics
    assert diag.code == "AF-LAM-DUMP-MISSING"
    assert diag.status == FindingStatus.UNRESOLVED


def test_invalid_json_is_named_diagnostic(tmp_path: Path) -> None:
    (tmp_path / "function.json").write_text("{broken")
    inv = extract_lambda(tmp_path)
    codes = [d.code for d in inv.diagnostics]
    assert "AF-LAM-DUMP-INVALID" in codes


class _StubClient:
    def get_function(self, *, FunctionName: str) -> dict:
        return {
            "Configuration": {"FunctionName": FunctionName, "Runtime": "python3.12"},
            "Code": {"Location": "https://presigned-url.example/never-persisted"},
        }

    def get_policy(self, *, FunctionName: str) -> dict:
        raise ValueError("ResourceNotFoundException")


def test_collect_writes_configuration_only(tmp_path: Path) -> None:
    manifest = collect("orders-api", tmp_path, now="2026-09-21T00:00:00Z", client=_StubClient())
    assert "function.json" in manifest.artifacts
    body = json.loads((tmp_path / "function.json").read_text())
    assert body["Runtime"] == "python3.12"
    assert "presigned-url" not in (tmp_path / "function.json").read_text()
    assert "policy.json" not in manifest.artifacts  # absent policy is data, not failure


def test_collect_without_boto3_refuses() -> None:
    import pytest

    with pytest.raises(CollectError, match="AF-COLLECT-AWS"):
        from apiforge.collectors.lambda_ import default_client

        default_client()
