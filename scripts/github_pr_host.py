#!/usr/bin/env python3
"""Dedicated GitHub host boundary for green-validation PR lifecycle.

This script is intentionally outside ``src/apiforge``. The deterministic core
never imports it and never receives a GitHub mutation client. CI supplies the
explicit policy approval and least-privilege token.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _run_gh(args: list[str]) -> str:
    completed = subprocess.run(
        ["gh", *args],
        check=True,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    return completed.stdout.strip()


def _write_receipt(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _require_approval(operation: str) -> None:
    if os.environ.get("APIFORGE_HOST_APPROVED", "").lower() != "true":
        raise RuntimeError(
            f"AF-GITHUB-HOST-APPROVAL: {operation} requires APIFORGE_HOST_APPROVED=true"
        )


def _find_pr(repository: str, head: str, base: str) -> dict[str, Any] | None:
    raw = _run_gh(
        [
            "pr",
            "list",
            "--repo",
            repository,
            "--state",
            "open",
            "--head",
            head,
            "--base",
            base,
            "--json",
            "number,url,headRefName,baseRefName,state",
        ]
    )
    rows = json.loads(raw or "[]")
    return rows[0] if isinstance(rows, list) and rows else None


def open_or_reuse(args: argparse.Namespace) -> dict[str, Any]:
    if args.dry_run:
        return {
            "schema_version": "af-github-pr-receipt/1",
            "operation": "create_or_reuse",
            "dry_run": True,
            "repository": args.repository,
            "head": args.head,
            "base": args.base,
            "mutation_allowed": False,
        }
    _require_approval("create_or_reuse")
    existing = _find_pr(args.repository, args.head, args.base)
    if existing is None:
        _run_gh(
            [
                "pr",
                "create",
                "--repo",
                args.repository,
                "--base",
                args.base,
                "--head",
                args.head,
                "--title",
                args.title,
                "--body",
                args.body,
            ]
        )
        existing = _find_pr(args.repository, args.head, args.base)
    if existing is None:
        raise RuntimeError("AF-GITHUB-PR-RECEIPT: created PR could not be read back")
    return {
        "schema_version": "af-github-pr-receipt/1",
        "operation": "create_or_reuse",
        "dry_run": False,
        "repository": args.repository,
        "head": args.head,
        "base": args.base,
        "pull_request": existing,
        "observed_at": datetime.now(UTC).isoformat(),
        "read_only": False,
        "mutation_allowed": True,
        "limitations": [
            "receipt proves the host read-back, not approval identity or merge safety",
            "merge and deployment remain separate operations",
        ],
    }


def enable_auto_merge(args: argparse.Namespace) -> dict[str, Any]:
    if args.dry_run:
        return {
            "schema_version": "af-github-pr-receipt/1",
            "operation": "enable_auto_merge",
            "dry_run": True,
            "repository": args.repository,
            "head": args.head,
            "base": args.base,
            "mutation_allowed": False,
        }
    _require_approval("enable_auto_merge")
    pr = _find_pr(args.repository, args.head, args.base)
    if pr is None:
        raise RuntimeError("AF-GITHUB-PR-NOT-FOUND: no open PR exists for the branch")
    _run_gh(
        [
            "pr",
            "merge",
            str(pr["number"]),
            "--repo",
            args.repository,
            "--auto",
            "--squash",
            "--delete-branch",
        ]
    )
    return {
        "schema_version": "af-github-pr-receipt/1",
        "operation": "enable_auto_merge",
        "dry_run": False,
        "repository": args.repository,
        "head": args.head,
        "base": args.base,
        "pull_request": pr,
        "observed_at": datetime.now(UTC).isoformat(),
        "read_only": False,
        "mutation_allowed": True,
        "limitations": [
            "GitHub branch protection and required approvals still control eligibility",
            "receipt proves the auto-merge request, not the eventual merge or deployment",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--operation", choices=("create_or_reuse", "enable_auto_merge"), required=True
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--title", default="Validate branch")
    parser.add_argument("--body", default="Automated PR opened after all validations passed.")
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        payload = (
            open_or_reuse(args) if args.operation == "create_or_reuse" else enable_auto_merge(args)
        )
        _write_receipt(args.receipt, payload)
        print(json.dumps(payload, sort_keys=True))
        return 0
    except subprocess.CalledProcessError as exc:
        print(
            "AF-GITHUB-HOST-PR: GitHub host command failed "
            f"(field=GH_TOKEN; unlock=configure the least-privilege token and repository policy): "
            f"{exc.stderr.strip() or exc}",
            file=sys.stderr,
        )
        return 2
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"AF-GITHUB-HOST-PR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
