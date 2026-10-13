from __future__ import annotations

import json
from pathlib import Path

from apiforge.contracts.change_control import ChangeBundle
from apiforge.core.io import sha256_file
from apiforge.integrations.replay import ReplayAdapter


def test_replay_adapter_loads_fixture() -> None:
    path = Path("tests/fixtures/api_git_cicd/change_bundle.json")
    bundle = ReplayAdapter().load(path)
    assert bundle.provider == "artifact"
    assert bundle.policy.mutation_allowed is False


def test_replay_adapter_loads_real_anonymized_provider_example() -> None:
    path = Path("tests/fixtures/api_git_cicd/real_anonymized/github-actions-success.bundle.json")
    bundle = ReplayAdapter().load(path)
    assert isinstance(bundle, ChangeBundle)
    assert bundle.provider == "github"
    assert bundle.policy.mutation_allowed is False
    assert bundle.checks[0].conclusion == "success"


def test_live_receipt_binds_committed_live_bundle() -> None:
    bundle_path = Path("tests/fixtures/api_git_cicd/live/github-success.bundle.json")
    receipt_path = Path("tests/fixtures/api_git_cicd/live/github-success.receipt.json")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    bundle = ReplayAdapter().load(bundle_path)
    assert bundle.provider == "github"
    assert receipt["schema_version"] == "af-change-collection-receipt/1"
    assert receipt["bundle_sha256"] == sha256_file(bundle_path)
    assert receipt["mutation_allowed"] is False
    assert all(conclusion == "success" for conclusion in receipt["check_conclusions"])
