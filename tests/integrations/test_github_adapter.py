from __future__ import annotations

from collections.abc import Mapping

import pytest

from apiforge.contracts.change_control import ChangeCollectRequest
from apiforge.integrations.github import GitHubReadOnlyAdapter
from apiforge.integrations.transport import TransportError


class FakeTransport:
    def __init__(self) -> None:
        self.paths: list[str] = []

    def get_json(self, path: str, *, params: Mapping[str, str] | None = None) -> object:
        self.paths.append(path)
        if path.endswith("check-runs"):
            return {
                "check_runs": [{"name": "unit", "conclusion": "success", "token": "secret-value"}]
            }
        return {"id": 1, "head": {"sha": "redacted"}, "token": "secret-value"}


def test_github_adapter_is_read_only_and_normalizes_observations() -> None:
    transport = FakeTransport()
    request = ChangeCollectRequest(
        repository="example/repo",
        base_sha="0" * 40,
        head_sha="1" * 40,
        pull_number=7,
    )
    bundle = GitHubReadOnlyAdapter(transport).collect(request)
    assert bundle.provider == "github"
    assert bundle.policy.mutation_allowed is False
    assert [item.conclusion for item in bundle.checks] == ["success"]
    assert "secret-value" not in bundle.model_dump_json()
    assert all("/repos/example/repo/" in path for path in transport.paths)


def test_github_adapter_refuses_malformed_provider_payload() -> None:
    class BadTransport:
        def get_json(self, path: str, *, params: Mapping[str, str] | None = None) -> object:
            return []

    request = ChangeCollectRequest(
        repository="example/repo",
        base_sha="0" * 40,
        head_sha="1" * 40,
    )
    with pytest.raises(TransportError) as captured:
        GitHubReadOnlyAdapter(BadTransport()).collect(request)
    assert captured.value.code == "AF-GITHUB-PAYLOAD"
