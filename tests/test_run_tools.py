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


def test_registry_covers_every_runnable_tool() -> None:
    from apiforge.run_tools import TOOL_REGISTRY, TOOLS

    for name in TOOLS:
        entry = TOOL_REGISTRY[name]
        assert entry["runnable"] is True
        assert entry["parser"] == TOOLS[name]["reader"]


def test_registry_fields_complete() -> None:
    from apiforge.run_tools import TOOL_REGISTRY

    required = {
        "category", "license", "input", "output", "capabilities", "limits",
        "cost", "needs_network", "needs_credentials", "local_support",
        "aws_support", "parser", "compat", "evidence_producer", "modes",
        "runnable", "install",
    }
    for name, meta in TOOL_REGISTRY.items():
        missing = required - set(meta)
        assert not missing, f"{name}: {missing}"
        for field in ("capabilities", "limits", "modes"):
            assert meta[field], f"{name}.{field} empty"


def test_import_only_tool_named() -> None:
    from apiforge.run_tools import run_tool

    with pytest.raises(RunError, match="AF-RUN-IMPORT-ONLY"):
        run_tool("locust", Path("."), Path("o.json"), {}, 5)


def test_list_tools_measures_install_not_declares() -> None:
    from apiforge.run_tools import list_tools

    rows = list_tools()
    assert len(rows) == 12
    by_name = {r["name"]: r for r in rows}
    assert "installed" in by_name["k6"]  # measured via shutil.which
    assert by_name["locust"]["runnable"] is False


def _k6_script(tmp_path: Path, url: str | None) -> Path:
    script = tmp_path / "s.js"
    body = (
        f'import http from "k6/http";\n'
        f'export default function() {{ http.get("{url}"); }}\n'
        if url
        else 'export default function() { http.get(__ENV.BASE_URL); }\n'
    )
    script.write_text(body)
    return script


def test_remote_load_target_gated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    script = _k6_script(tmp_path, "https://api.example.com/orders")
    with pytest.raises(RunError, match="AF-RUN-PROD-GATE"):
        run_tool("k6", script, tmp_path / "o.json", {}, 5)
    with pytest.raises(RunError, match="AF-RUN-PROD-GATE"):
        run_tool("k6", script, tmp_path / "o.json", {}, 5, approval=None)


def test_unresolvable_load_target_gated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    script = _k6_script(tmp_path, None)
    with pytest.raises(RunError, match="AF-RUN-PROD-GATE"):
        run_tool("k6", script, tmp_path / "o.json", {}, 5)


def test_local_target_passes_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    script = _k6_script(tmp_path, "http://localhost:8080/orders")
    # passes the policy gate; then fails honestly on the missing binary
    with pytest.raises(RunError, match="AF-RUN-TOOL-MISSING|AF-RUN-NO-REPORT"):
        run_tool("k6", script, tmp_path / "o.json", {}, 5)


def test_dry_run_never_gates(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    script = _k6_script(tmp_path, "https://api.example.com")
    result = run_tool("k6", script, tmp_path / "o.json", {}, 5, dry_run=True)
    assert result["dry_run"] is True


def test_approved_remote_reaches_binary_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    script = _k6_script(tmp_path, "https://api.example.com/orders")
    with pytest.raises(RunError, match="AF-RUN-TOOL-MISSING|AF-RUN-NO-REPORT"):
        run_tool("k6", script, tmp_path / "o.json", {}, 5, approval="CHG-1234")


def test_non_load_tools_never_gated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RunError, match="AF-RUN-TOOL-MISSING|AF-RUN-NO-REPORT"):
        run_tool("trivy", tmp_path, tmp_path / "o.json", {}, 5)
