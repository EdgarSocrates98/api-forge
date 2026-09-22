"""Load-scenario generation — deterministic k6/JMeter/Locust templates.

Input is a declared scenario mapping (endpoints, rps, duration, ramp).
Output is the tool's script text — API Forge generates the scenario; the
operator runs it. Generation never executes the tool.
"""

from __future__ import annotations

import json
from typing import Any

from apiforge.run_tools import RunError

_TOOLS = ("k6", "jmeter", "locust")


def _endpoints(scenario: dict[str, Any]) -> list[dict[str, str]]:
    eps = scenario.get("endpoints")
    if not isinstance(eps, list) or not eps:
        raise RunError("AF-SCENARIO-SCHEMA", "scenario.endpoints must be a non-empty list")
    out: list[dict[str, str]] = []
    for i, ep in enumerate(eps):
        if not isinstance(ep, dict) or not ep.get("path"):
            raise RunError("AF-SCENARIO-SCHEMA", f"endpoints[{i}] needs a path")
        out.append(
            {
                "method": str(ep.get("method", "GET")).upper(),
                "path": str(ep["path"]),
            }
        )
    return out


def _k6(scenario: dict[str, Any]) -> str:
    base = str(scenario.get("base_url", "__ENV.BASE_URL"))
    base_expr = (
        f'"{base}"' if base.startswith("http") else base
    )
    rps = scenario.get("rps")
    duration = str(scenario.get("duration", "60s"))
    eps = _endpoints(scenario)
    calls = "\n".join(
        f'  http.request("{ep["method"]}", `${{base}}{ep["path"]}`);'
        for ep in eps
    )
    rps_line = (
        f"      rate: {json.dumps(rps)},\n      timeUnit: '1s',\n"
        if rps
        else ""
    )
    preallocated = max(1, int(rps or 10))
    return f"""import http from 'k6/http';

const base = {base_expr};

export const options = {{
  scenarios: {{
    default: {{
      executor: 'constant-arrival-rate',
{rps_line}      duration: '{duration}',
      preAllocatedVUs: {preallocated},
    }},
  }},
}};

export default function () {{
{calls}
}}
"""


def _locust(scenario: dict[str, Any]) -> str:
    eps = _endpoints(scenario)
    users = int(scenario.get("users") or scenario.get("rps") or 10)
    spawn = int(scenario.get("spawn_rate") or max(1, users // 10))
    methods = "\n\n".join(
        f'    @task\n'
        f'    def ep_{i}(self):\n'
        f'        self.client.{ep["method"].lower()}("{ep["path"]}")'
        for i, ep in enumerate(eps)
    )
    duration = scenario.get("duration", "60s")
    return (
        "from locust import HttpUser, task, between\n\n\n"
        "class GeneratedUser(HttpUser):\n"
        "    wait_time = between(0.1, 0.5)\n\n"
        f"{methods}\n\n"
        f"# run: locust -f locustfile.py --users {users} "
        f"--spawn-rate {spawn} --run-time {duration}\n"
    )


def _jmeter(scenario: dict[str, Any]) -> str:
    eps = _endpoints(scenario)
    threads = int(scenario.get("users") or scenario.get("rps") or 10)
    duration = str(scenario.get("duration", "60")).rstrip("s")
    samplers = "\n".join(
        f"""        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testname="{ep['method']} {ep['path']}">
          <stringProp name="HTTPSampler.path">{ep['path']}</stringProp>
          <stringProp name="HTTPSampler.method">{ep['method']}</stringProp>
          <stringProp name="HTTPSampler.domain">${{__P(host,localhost)}}</stringProp>
          <stringProp name="HTTPSampler.protocol">${{__P(scheme,http)}}</stringProp>
        </HTTPSamplerProxy>
        <hashTree/>"""
        for ep in eps
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testname="apiforge-scenario"/>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testname="default">
        <stringProp name="ThreadGroup.num_threads">{threads}</stringProp>
        <stringProp name="ThreadGroup.duration">{duration}</stringProp>
      </ThreadGroup>
      <hashTree>
{samplers}
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""


_GENERATORS = {"k6": _k6, "jmeter": _jmeter, "locust": _locust}


def generate_scenario(tool: str, scenario: dict[str, Any]) -> dict[str, Any]:
    """Emit the tool's script text for a declared scenario."""
    gen = _GENERATORS.get(tool)
    if gen is None:
        raise RunError(
            "AF-SCENARIO-TOOL",
            f"no scenario generator for {tool!r}; supported: {_TOOLS}",
        )
    if not isinstance(scenario, dict):
        raise RunError("AF-SCENARIO-SCHEMA", "scenario must be a JSON object")
    return {
        "tool": tool,
        "script": gen(scenario),
        "endpoints": _endpoints(scenario),
        "note": "generated template — review before running; execution is external",
    }
