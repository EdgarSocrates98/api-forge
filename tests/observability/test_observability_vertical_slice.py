import json

from apiforge.observability.supervisor import run_fixture


def test_offline_vertical_slice(tmp_path) -> None:
    source = tmp_path / "otel.json"
    source.write_text(json.dumps({"records": [{"kind": "span", "service": "orders", "status_code": 200, "duration_ms": 12}]}), encoding="utf-8")
    result = run_fixture(tmp_path, source)
    assert result["snapshot_path"]
    assert result["signals"][0]["throughput_tps"] == 1
