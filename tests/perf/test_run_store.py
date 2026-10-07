"""perf memory — append-only run store; search filters declared fields only."""

from pathlib import Path

import pytest

from apiforge.contracts.stubs import PerformanceRun
from apiforge.perf.run_store import MemoryError, add_run, read_runs, search_runs


def _run(subject: str, tool: str | None = None, **kw: object) -> PerformanceRun:
    attrs = {"tool": tool} if tool else {}
    return PerformanceRun.model_validate(
        {"id": f"run-{subject}", "subject": subject, "attributes": attrs, **kw}
    )


def test_memory_round_trip_and_subject_filter(tmp_path: Path) -> None:
    add_run(tmp_path, _run("orders"), recorded_at="2026-09-01T00:00:00Z")
    add_run(tmp_path, _run("orders", "k6"), recorded_at="2026-09-02T00:00:00Z")
    add_run(tmp_path, _run("billing"), recorded_at="2026-09-03T00:00:00Z")

    orders = search_runs(tmp_path, subject="orders")
    assert [r["recorded_at"] for r in orders] == [
        "2026-09-01T00:00:00Z",
        "2026-09-02T00:00:00Z",
    ]
    assert search_runs(tmp_path, subject="nope") == []


def test_tool_and_since_filters(tmp_path: Path) -> None:
    add_run(tmp_path, _run("orders", "k6"), recorded_at="2026-09-01T00:00:00Z")
    add_run(tmp_path, _run("orders", "jmeter"), recorded_at="2026-09-05T00:00:00Z")

    assert len(search_runs(tmp_path, subject="orders", tool="k6")) == 1
    assert len(search_runs(tmp_path, since="2026-09-03T00:00:00Z")) == 1
    # records without recorded_at never satisfy a since filter
    add_run(tmp_path, _run("orders"))
    assert len(search_runs(tmp_path, since="2026-01-01")) == 2


def test_empty_store_returns_empty(tmp_path: Path) -> None:
    assert search_runs(tmp_path, subject="orders") == []


def test_corrupt_line_is_named_not_skipped(tmp_path: Path) -> None:
    add_run(tmp_path, _run("orders"))
    path = tmp_path / ".apiforge" / "perf" / "runs.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write("{corrupt\n")
    with pytest.raises(MemoryError, match="AF-PERF-MEMORY-CORRUPT"):
        read_runs(tmp_path)


def test_record_carries_payload_hash(tmp_path: Path) -> None:
    meta = add_run(tmp_path, _run("orders"))
    record = read_runs(tmp_path)[0]
    assert record["sha256"] == meta["sha256"]
    assert len(record["sha256"]) == 64
