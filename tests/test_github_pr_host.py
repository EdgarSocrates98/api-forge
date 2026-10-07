from __future__ import annotations

import json
import subprocess
import sys
from argparse import Namespace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _host_module():
    path = Path("scripts/github_pr_host.py")
    spec = spec_from_file_location("github_pr_host_under_test", path)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_github_pr_host_dry_run_is_non_mutating(tmp_path: Path) -> None:
    receipt = tmp_path / "receipt.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/github_pr_host.py",
            "--operation",
            "create_or_reuse",
            "--repository",
            "example/repo",
            "--head",
            "feature",
            "--receipt",
            str(receipt),
            "--dry-run",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["mutation_allowed"] is False
    assert json.loads(receipt.read_text(encoding="utf-8"))["operation"] == "create_or_reuse"


def test_auto_merge_receipt_contains_post_mutation_readback(monkeypatch) -> None:
    module = _host_module()
    monkeypatch.setenv("APIFORGE_HOST_APPROVED", "true")
    calls: list[list[str]] = []

    def fake_run(args: list[str]) -> str:
        calls.append(args)
        if args[:2] == ["pr", "list"]:
            return json.dumps(
                [{"number": 7, "url": "https://github.com/example/repo/pull/7", "state": "OPEN"}]
            )
        if args[:2] == ["pr", "view"]:
            return json.dumps(
                {
                    "number": 7,
                    "url": "https://github.com/example/repo/pull/7",
                    "state": "MERGED",
                    "mergedAt": "2026-09-23T00:00:00Z",
                }
            )
        return ""

    monkeypatch.setattr(module, "_run_gh", fake_run)
    payload = module.enable_auto_merge(
        Namespace(repository="example/repo", head="feature", base="main", dry_run=False)
    )
    assert payload["pull_request_before"]["number"] == 7
    assert payload["pull_request_after"]["state"] == "MERGED"
    assert any(args[:2] == ["pr", "merge"] for args in calls)
