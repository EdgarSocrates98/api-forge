"""run tool: allowlisted argv, no shell, timeout, missing binary named."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from apiforge.run_tools import RunError, build_argv, run_tool


def test_unknown_tool_named(tmp_path: Path) -> None:
    with pytest.raises(RunError, match="AF-RUN-TOOL-UNKNOWN"):
        build_argv("nmap", tmp_path, tmp_path / "o.json", {})


def test_semgrep_requires_local_config(tmp_path: Path) -> None:
    with pytest.raises(RunError, match="AF-RUN-CONFIG-MISSING"):
        build_argv("semgrep", tmp_path, tmp_path / "o.json", {})
    argv = build_argv("semgrep", tmp_path, tmp_path / "o.json", {"config": "rules/"})
    assert argv[:3] == ["semgrep", "scan", "--config"]
    assert "--json" in argv


def test_argv_templates_are_fixed(tmp_path: Path) -> None:
    out = tmp_path / "r.json"
    assert build_argv("trivy", tmp_path, out, {}) == [
        "trivy", "fs", "--format", "json", "--output", str(out), str(tmp_path),
    ]
    assert build_argv("gitleaks", tmp_path, out, {})[:2] == ["gitleaks", "dir"]
    assert build_argv("k6", tmp_path / "s.js", out, {})[:3] == [
        "k6", "run", "--summary-export",
    ]


def test_dry_run_never_executes(tmp_path: Path) -> None:
    result = run_tool(
        "trivy", tmp_path, tmp_path / "o.json", {}, 10, dry_run=True
    )
    assert result["dry_run"] is True
    assert result["argv"][0] == "trivy"
    assert not (tmp_path / "o.json").exists()


def test_missing_binary_is_named(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("shutil.which", lambda _: None)
    with pytest.raises(RunError, match="AF-RUN-TOOL-MISSING"):
        run_tool("trivy", tmp_path, tmp_path / "o.json", {}, 10)


def test_run_then_read_through_reader(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "trivy.json"

    def fake_run(argv: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        out.write_text(
            json.dumps(
                {
                    "Results": [
                        {
                            "Target": "app",
                            "Vulnerabilities": [
                                {"Severity": "CRITICAL", "VulnerabilityID": "V-1"}
                            ],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(subprocess, "run", fake_run)
    result = run_tool("trivy", tmp_path, out, {}, 10)
    assert result["exit_code"] == 0
    fact = next(f for f in result["facts"] if f["kind"] == "sec.trivy.report")
    assert fact["measures"]["findings"] == 1


def test_timeout_is_named(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def hang(argv: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(argv, 1)

    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(subprocess, "run", hang)
    with pytest.raises(RunError, match="AF-RUN-TIMEOUT"):
        run_tool("trivy", tmp_path, tmp_path / "o.json", {}, 1)


def test_tool_without_report_is_named(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def silent_fail(argv: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 2, "", "boom")

    monkeypatch.setattr("shutil.which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(subprocess, "run", silent_fail)
    with pytest.raises(RunError, match="AF-RUN-NO-REPORT"):
        run_tool("trivy", tmp_path, tmp_path / "o.json", {}, 10)
