"""perfprofiles readers: JFR JSON, pprof -top, Pyroscope flamebearer."""

from __future__ import annotations

import json
from pathlib import Path

from apiforge.adapters.perfprofiles import (
    extract_jfr,
    extract_pprof,
    extract_pyroscope,
)

JFR = {
    "recording": {
        "events": [
            {
                "type": "jdk.ExecutionSample",
                "values": {
                    "stackTrace": {
                        "frames": [{"method": {"type": "app.OrderService", "name": "find"}}]
                    }
                },
            },
            {
                "type": "jdk.ExecutionSample",
                "values": {
                    "stackTrace": {
                        "frames": [{"method": {"type": "app.OrderService", "name": "find"}}]
                    }
                },
            },
            {"type": "jdk.CPULoad", "values": {}},
        ]
    }
}

PPROF_TOP = """\
      flat  flat%   sum%        cum   cum%
     320ms 32.00% 32.00%      520ms 52.00%  app.orders.HandleList
     200ms 20.00% 52.00%      200ms 20.00%  runtime.mallocgc
"""

PYRO = {
    "flamebearer": {
        "names": ["total", "app.main", "app.orders.list", "runtime.gc"],
        "levels": [
            [0, 1000, 0, 0],
            [0, 1000, 100, 1],
            [0, 700, 500, 2, 500, 200, 200, 3],
        ],
    }
}


def _write(tmp_path: Path, name: str, payload: object) -> Path:
    p = tmp_path / name
    p.write_text(
        payload if isinstance(payload, str) else json.dumps(payload),
        encoding="utf-8",
    )
    return p


def test_jfr_counts_and_top_frames(tmp_path: Path) -> None:
    inv = extract_jfr(_write(tmp_path, "jfr.json", JFR))
    rec = next(f for f in inv.facts if f.kind == "perf.jfr.recording")
    assert rec.measures["events"] == 3
    assert rec.attrs["by_type"]["jdk.ExecutionSample"] == 2
    frame = next(f for f in inv.facts if f.kind == "perf.jfr.frame")
    assert frame.measures["frame"] == "app.OrderService.find"
    assert frame.attrs["execution_samples"] == 2


def test_jfr_invalid(tmp_path: Path) -> None:
    inv = extract_jfr(_write(tmp_path, "bad.json", "{not json"))
    assert [d.code for d in inv.diagnostics] == ["AF-PERF-REPORT-INVALID"]


def test_pprof_top_rows(tmp_path: Path) -> None:
    inv = extract_pprof(_write(tmp_path, "top.txt", PPROF_TOP))
    entries = {f.measures["function"]: f for f in inv.facts if f.kind == "perf.pprof.entry"}
    assert entries["app.orders.HandleList"].attrs["flat"] == 320.0
    assert entries["app.orders.HandleList"].attrs["cum"] == 520.0


def test_pprof_unrecognized(tmp_path: Path) -> None:
    inv = extract_pprof(_write(tmp_path, "top.txt", "no rows here\n"))
    assert [d.code for d in inv.diagnostics] == ["AF-PERF-REPORT-INVALID"]


def test_pyroscope_self_and_total(tmp_path: Path) -> None:
    inv = extract_pyroscope(_write(tmp_path, "flame.json", PYRO))
    entries = {f.measures["function"]: f for f in inv.facts if f.kind == "perf.pyroscope.entry"}
    assert entries["app.orders.list"].attrs["self"] == 500
    assert entries["app.orders.list"].attrs["total"] == 700
    assert entries["runtime.gc"].attrs["self"] == 200


def test_pyroscope_malformed(tmp_path: Path) -> None:
    inv = extract_pyroscope(_write(tmp_path, "flame.json", {"nope": 1}))
    assert [d.code for d in inv.diagnostics] == ["AF-PERF-REPORT-INVALID"]
