from __future__ import annotations

from pathlib import Path

from apiforge.integrations.replay import ReplayAdapter


def test_replay_adapter_loads_fixture() -> None:
    path = Path("tests/fixtures/api_git_cicd/change_bundle.json")
    bundle = ReplayAdapter().load(path)
    assert bundle.provider == "artifact"
    assert bundle.policy.mutation_allowed is False
