from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


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
