"""Phase 9 §40–§43: surface audit, disclosure router, ToolPage and benchmark."""

from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.contracts.tool_surface import DisclosurePolicy
from apiforge.mcp.audit import _load_policy as load_surface_policy
from apiforge.mcp.audit import audit_surface
from apiforge.mcp.benchmark import benchmark_tools
from apiforge.mcp.disclosure import _load_policy as load_disclosure_policy
from apiforge.mcp.disclosure import disclose
from apiforge.mcp.gateway import full_tools
from apiforge.output.page import paged

# --- §40 audit --------------------------------------------------------------


def test_audit_reports_measured_surface() -> None:
    report = audit_surface()
    assert report.tool_count > 100
    assert report.total_bytes > 0
    assert "oversized_output requires a benchmark" in report.unresolved[0]
    for finding in report.findings:
        assert finding.evidence in ("observed", "estimated", "hypothesis")


def test_audit_bad_policy_refuses(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("not: a mapping\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-MCP-SURFACE-POLICY"):
        load_surface_policy(bad)


def test_audit_oversized_output_needs_samples() -> None:
    report = audit_surface(benchmark_bytes={"big_tool": 99999})
    assert any(f.kind == "oversized_output" and f.evidence == "observed" for f in report.findings)


def test_audit_deterministic() -> None:
    first = audit_surface().model_dump(mode="json")
    second = audit_surface().model_dump(mode="json")
    assert first == second


# --- §41 disclosure ---------------------------------------------------------


def test_disclose_routes_security_task() -> None:
    result = disclose("oauth security review")
    assert result.task_class == "security_governance"
    assert "decision_check" in result.active_tools
    assert len(result.dropped_tools) > len(result.active_tools)
    assert result.basis == "declared-policy"


def test_disclose_unclassified_falls_back_full() -> None:
    result = disclose("xyzzy nothing matches")
    assert result.task_class == "unclassified"
    assert result.basis == "fallback-full"
    assert result.dropped_tools == ()
    assert any("unclassified" in item or "keyword" in item for item in result.unresolved)


def test_disclose_declared_names_exist_on_registry() -> None:
    known = set(full_tools())
    policy = load_disclosure_policy()
    for name, tools in policy["task_classes"].items():
        missing = [tool for tool in tools if tool not in known]
        assert not missing, f"class {name} declares unknown tools {missing}"


def test_disclose_bad_policy_refuses(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("not: a mapping\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-MCP-DISCLOSURE-POLICY"):
        load_disclosure_policy(bad)


def test_disclosure_policy_rejects_empty_class() -> None:
    with pytest.raises(ValueError, match="declares no tools"):
        DisclosurePolicy(task_classes={"empty": ()})


# --- §42 ToolPage -----------------------------------------------------------


def test_paged_window_honest() -> None:
    page = paged(list(range(10)), offset=0, limit=4)
    assert page.pagination.total == 10
    assert len(page.items) == 4
    assert page.pagination.next_offset == 4
    tail = paged(list(range(10)), offset=8, limit=4)
    assert tail.pagination.next_offset is None
    assert len(tail.items) == 2


# --- §43 benchmark -----------------------------------------------------------


def test_benchmark_ranks_and_labels() -> None:
    report = benchmark_tools(
        {"rules_list": {"kwargs": {}}, "mcp_surface": {"kwargs": {"surface": "compact"}}},
        repeats=2,
    )
    assert len(report.tools) == 2
    assert report.ranking[0] == report.tools[0].tool
    assert report.tools[0].median_bytes >= report.tools[1].median_bytes
    for item in report.tools:
        assert item.basis == "estimated"
        assert item.median_tokens_est == item.median_bytes // 4 or item.median_tokens_est > 0


def test_benchmark_missing_tool_unresolved() -> None:
    report = benchmark_tools({"no_such_tool": {"kwargs": {}}})
    assert report.tools == ()
    assert "not on the registry" in report.unresolved[0]


def test_benchmark_bad_policy_refuses(tmp_path: Path) -> None:
    from apiforge.mcp.benchmark import _load_policy

    bad = tmp_path / "bad.yaml"
    bad.write_text("not: a mapping\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-MCP-BENCHMARK-POLICY"):
        _load_policy(bad)


# --- §40 engineering results ------------------------------------------------


def test_surface_engineering_fixes_hold() -> None:
    """Docstrings, limit params and declared exceptions keep findings at zero."""
    report = audit_surface()
    poor = [f.tool for f in report.findings if f.kind == "poor_description"]
    assert poor == []
    for tool in (
        "rules_list",
        "capabilities_list",
        "contract_list",
        "knowledge_list",
        "memory_quarantine_list",
        "cache_stats",
        "context_delta",
        "context_gc",
        "economy_pricing",
        "perf_chaos",
    ):
        assert not any(f.tool == tool and f.kind == "unbounded_list" for f in report.findings), tool


def test_audit_accepted_exceptions_are_recorded() -> None:
    """Declared policy exceptions land in `accepted` with reason — never dropped."""
    report = audit_surface()
    overlap = [f for f in report.findings if f.kind == "overlapping"]
    assert overlap == []
    perf = [f for f in report.accepted if f.tool == "perf_memory_search"]
    assert len(perf) == 1
    assert "accepted:" in perf[0].detail and "distinct domain" in perf[0].detail


def test_audit_bad_accepted_policy_refuses(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("thresholds: {}\naccepted: {nope: true}\n", encoding="utf-8")
    with pytest.raises(ContractError, match="AF-MCP-SURFACE-POLICY"):
        load_surface_policy(bad)
