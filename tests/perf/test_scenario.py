"""Load-scenario generation — deterministic templates, never executed."""

from __future__ import annotations

import pytest

from apiforge.perf.scenario import generate_scenario
from apiforge.run_tools import RunError

SPEC = {
    "base_url": "http://localhost:8080",
    "rps": 50,
    "duration": "120s",
    "endpoints": [
        {"method": "GET", "path": "/orders"},
        {"method": "POST", "path": "/orders"},
    ],
}


def test_k6_template() -> None:
    out = generate_scenario("k6", SPEC)
    assert "constant-arrival-rate" in out["script"]
    assert "rate: 50" in out["script"]
    assert 'http.request("GET", `${base}/orders`)' in out["script"]
    assert 'http.request("POST", `${base}/orders`)' in out["script"]
    assert out["endpoints"] == [
        {"method": "GET", "path": "/orders"},
        {"method": "POST", "path": "/orders"},
    ]


def test_k6_env_base_url() -> None:
    out = generate_scenario("k6", {**SPEC, "base_url": "__ENV.BASE_URL"})
    assert "const base = __ENV.BASE_URL" in out["script"]


def test_jmeter_xml() -> None:
    out = generate_scenario("jmeter", SPEC)
    assert "jmeterTestPlan" in out["script"]
    assert 'HTTPSampler.method">POST' in out["script"]
    assert 'ThreadGroup.num_threads">50' in out["script"]


def test_locust_py() -> None:
    out = generate_scenario("locust", SPEC)
    assert "HttpUser" in out["script"]
    assert 'self.client.get("/orders")' in out["script"]
    assert 'self.client.post("/orders")' in out["script"]


def test_unknown_tool_named() -> None:
    with pytest.raises(RunError, match="AF-SCENARIO-TOOL"):
        generate_scenario("gatling", SPEC)


def test_missing_endpoints_named() -> None:
    with pytest.raises(RunError, match="AF-SCENARIO-SCHEMA"):
        generate_scenario("k6", {"rps": 10})


def test_deterministic() -> None:
    assert generate_scenario("k6", SPEC) == generate_scenario("k6", SPEC)
