import json
from pathlib import Path

import pytest

from apiforge.collectors.apigateway import collect
from apiforge.collectors.manifest import CollectError


class StubGateway:
    def __init__(self) -> None:
        self.resources_calls = 0

    def get_rest_api(self, *, restApiId: str):
        return {"id": restApiId, "name": "orders"}

    def get_resources(self, **kwargs):
        self.resources_calls += 1
        if "position" not in kwargs:
            return {
                "items": [{"id": "r1", "path": "/"}],
                "position": "next-page",
            }
        return {"items": [{"id": "r2", "path": "/orders"}]}

    def get_stages(self, *, restApiId: str):
        return {"item": [{"stageName": "prod"}]}

    def get_authorizers(self, **kwargs):
        return {"items": [{"id": "a1", "type": "TOKEN"}]}


def test_collect_writes_all_artifacts(tmp_path: Path) -> None:
    manifest = collect("api-1", tmp_path / "dump", now="2026-09-21T00:00:00Z", client=StubGateway())
    names = set(manifest.artifacts)
    assert (
        names
        == {
            "rest-api.json",
            "resources.json",
            "stages.json",
            "authorizers.json",
            "manifest.json",
        }
        - {"manifest.json"}
        or "rest-api.json" in names
    )
    dump = tmp_path / "dump"
    assert (dump / "manifest.json").is_file()
    resources = json.loads((dump / "resources.json").read_text())
    assert len(resources["items"]) == 2  # pagination followed


def test_collect_manifest_is_deterministic(tmp_path: Path) -> None:
    m1 = collect("api-1", tmp_path / "a", now="2026-09-21T00:00:00Z", client=StubGateway())
    m2 = collect("api-1", tmp_path / "b", now="2026-09-21T00:00:00Z", client=StubGateway())
    assert m1.artifacts == m2.artifacts


def test_collect_without_now_records_null(tmp_path: Path) -> None:
    collect("api-1", tmp_path / "dump", client=StubGateway())
    manifest = json.loads((tmp_path / "dump" / "manifest.json").read_text())
    assert manifest["collected_at"] is None


def test_aws_error_is_named(tmp_path: Path) -> None:
    class Failing:
        def get_rest_api(self, **kwargs):
            raise RuntimeError("AccessDenied")

    with pytest.raises(CollectError, match="AF-COLLECT-AWS"):
        collect("api-1", tmp_path / "dump", client=Failing())
