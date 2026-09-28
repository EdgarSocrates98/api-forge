from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.agentops.projection import project_host
from apiforge.agentops.slicing import normalize_signature, slice_log, slice_tests
from apiforge.cli import app
from apiforge.contracts.base import ContractError
from apiforge.mcp import tools
from apiforge.mcp.gateway import apiforge_call, apiforge_discover, full_tools
from apiforge.mcp.main import resolve_surface
from apiforge.mcp.surface import measure_surface
from apiforge.output.render import prune, render, resolve_mode

runner = CliRunner()
REPO = Path(__file__).resolve().parents[2]
LOGS = REPO / "evals" / "corpus" / "tool-economy" / "logs"


def test_prune_keeps_every_non_empty_value() -> None:
    value = {"a": None, "b": "", "c": [], "d": {}, "e": 0, "f": False, "g": [{"h": None, "i": 1}]}
    assert prune(value) == {"e": 0, "f": False, "g": [{"i": 1}]}
    compact = render(value, "compact")
    assert json.loads(compact) == prune(value) and " " not in compact


def test_output_mode_resolution(monkeypatch) -> None:
    monkeypatch.delenv("APIFORGE_OUTPUT", raising=False)
    assert resolve_mode(None) == "json"
    monkeypatch.setenv("APIFORGE_OUTPUT", "compact")
    assert resolve_mode(None) == "compact"
    with pytest.raises(ContractError) as bad:
        resolve_mode("yaml")
    assert bad.value.code == "AF-OUTPUT-MODE-INVALID"


def test_cli_output_compact_is_lossless(monkeypatch) -> None:
    monkeypatch.delenv("APIFORGE_OUTPUT", raising=False)
    args = ["knowledge", "select", "--intent", "OAuth on the API Gateway"]
    full = runner.invoke(app, args)
    compact = runner.invoke(app, ["--output", "compact", *args])
    assert full.exit_code == compact.exit_code == 0
    assert len(compact.output) < len(full.output)
    assert json.loads(compact.output) == prune(json.loads(full.output))
    again = runner.invoke(app, args)
    assert again.output == full.output


def test_pytest_and_junit_slices_keep_every_failure(tmp_path: Path) -> None:
    pytest_slice = slice_tests(tmp_path, LOGS / "pytest-failures.log")
    assert (pytest_slice.passed, pytest_slice.failed) == (300, 2)
    assert {item.line for item in pytest_slice.failures} == {18, 31}
    assert pytest_slice.slice_bytes < 0.2 * pytest_slice.original_bytes
    junit = slice_tests(tmp_path, LOGS / "junit-payments.xml")
    assert (junit.failed, junit.errors, junit.skipped) == (1, 1, 1)
    assert "expected status 400" in junit.failures[0].assertion


def test_junit_doctype_is_refused(tmp_path: Path) -> None:
    evil = tmp_path / "evil.xml"
    evil.write_text(
        '<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "aaaa">]><testsuite/>', encoding="utf-8"
    )
    with pytest.raises(ContractError) as refused:
        slice_tests(tmp_path, evil, "junit")
    assert refused.value.code == "AF-SLICE-XML-REFUSED"


def test_log_slice_dedupes_signatures_and_keeps_frames(tmp_path: Path) -> None:
    log = slice_log(tmp_path, LOGS / "java-ci.log")
    top = log.signatures[0]
    assert top.count == 3 and len(top.spans) == 3
    assert top.frames[0].startswith("at com.example.payments.PaymentService.create")
    assert "openjdk 21" in log.environment
    from apiforge.context.gateway.refs import CtxStore

    assert CtxStore(tmp_path).get(log.log_ref).startswith("[INFO]")
    go = slice_log(tmp_path, LOGS / "go-panic.log")
    assert any(item.first_line.startswith("panic:") for item in go.signatures)


def test_signature_normalization_is_stable() -> None:
    assert normalize_signature("key 'k1' used by 120 at /a/b.py") == normalize_signature(
        "key 'k2' used by 999 at /c/d.py"
    )


def test_missing_slice_input_refuses(tmp_path: Path) -> None:
    result = runner.invoke(app, ["slice", "log", "--input", str(tmp_path / "nope.log")])
    assert result.exit_code == 2 and "AF-SLICE-INPUT-NOT-FOUND" in result.output


def test_compact_surface_reaches_everything() -> None:
    full = measure_surface("full")
    compact = measure_surface("compact")
    assert compact.tool_count == 6
    assert compact.total_bytes <= 0.25 * full.total_bytes
    assert compact.reachable_capabilities == full.tool_count == len(full_tools())
    assert apiforge_call("rules_list", {}) == prune(tools.rules_list())
    matches = [item["tool"] for item in apiforge_discover("grpc breaking diff", 5)["matches"]]
    assert "grpc_diff" in matches


def test_gateway_refusals() -> None:
    with pytest.raises(ContractError) as unknown:
        apiforge_call("nope")
    assert unknown.value.code == "AF-MCP-TOOL-UNKNOWN"
    with pytest.raises(ContractError) as args:
        apiforge_call("rules_list", {"bogus": 1})
    assert args.value.code == "AF-MCP-TOOL-ARGS"
    with pytest.raises(ContractError) as surface:
        measure_surface("tiny")
    assert surface.value.code == "AF-MCP-SURFACE-INVALID"


def test_host_projection_and_mcp_surface_resolution(monkeypatch) -> None:
    claude = project_host("claude")
    assert (claude.mcp_surface, claude.output, claude.deferred_tools) == (
        "compact",
        "compact",
        True,
    )
    assert claude.surface_bytes < claude.full_surface_bytes
    assert "why did CI fail" in claude.verb_map
    with pytest.raises(ContractError) as unknown:
        project_host("vim")
    assert unknown.value.code == "AF-HOST-UNKNOWN"
    monkeypatch.delenv("APIFORGE_MCP_SURFACE", raising=False)
    monkeypatch.delenv("APIFORGE_HOST", raising=False)
    assert resolve_surface([]) == "full"
    assert resolve_surface(["--host", "copilot"]) == "full"
    assert resolve_surface(["--host", "claude"]) == "compact"
    assert resolve_surface(["--surface", "full", "--host", "claude"]) == "full"


def test_cli_mcp_parity_for_surface_and_projection() -> None:
    cli = json.loads(runner.invoke(app, ["mcp", "surface", "--surface", "compact"]).output)
    assert cli == tools.mcp_surface("compact")
    proj = json.loads(runner.invoke(app, ["agentops", "projection", "--host", "devin"]).output)
    assert proj == tools.agentops_projection("devin")
