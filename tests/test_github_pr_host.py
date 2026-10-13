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


def test_github_host_retries_transient_gateway(monkeypatch) -> None:
    module = _host_module()
    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        if len(calls) < 3:
            raise subprocess.CalledProcessError(1, command, stderr="HTTP 504: 504 Gateway Timeout")
        return subprocess.CompletedProcess(command, 0, stdout="ok\n", stderr="")

    monkeypatch.setattr(module.subprocess, "run", fake_run)
    monkeypatch.setattr(module.time, "sleep", lambda _seconds: None)

    assert module._run_gh(["pr", "list"]) == "ok"
    assert len(calls) == 3


def test_find_pr_falls_back_to_rest_on_graphql_gateway(monkeypatch) -> None:
    module = _host_module()
    calls: list[list[str]] = []

    def fake_run(args: list[str]) -> str:
        calls.append(args)
        if args[:2] == ["pr", "list"]:
            raise subprocess.CalledProcessError(1, args, stderr="HTTP 502: 502 Bad Gateway")
        assert args[0] == "api"
        return json.dumps([{"number": 7, "url": "https://github.com/example/repo/pull/7"}])

    monkeypatch.setattr(module, "_run_gh", fake_run)

    result = module._find_pr("example/repo", "feature", "main")

    assert result and result["number"] == 7
    assert calls[1][0] == "api"


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
