"""Execute allowlisted scanner binaries, then read their reports.

`run <tool>` is the only verb family that executes an external binary — a
closed table of argv templates, resolved by ``shutil.which``, run without a
shell and under a timeout. The tool's report file then goes through the same
offline reader `model <tool>` uses. The analyzed code is still never
executed: the *scanner* runs, the target stays data.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


class RunError(ValueError):
    """A refused or failed tool run; ``str()`` begins with the AF code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def _argv_semgrep(target: Path, out: Path, extra: dict[str, str]) -> list[str]:
    config = extra.get("config")
    if not config:
        raise RunError(
            "AF-RUN-CONFIG-MISSING",
            "semgrep needs --config <local rules dir/file> — `auto` would hit the network",
        )
    return ["semgrep", "scan", "--config", config, "--json", "--output", str(out), str(target)]


def _argv_trivy(target: Path, out: Path, extra: dict[str, str]) -> list[str]:
    return ["trivy", "fs", "--format", "json", "--output", str(out), str(target)]


def _argv_gitleaks(target: Path, out: Path, extra: dict[str, str]) -> list[str]:
    return [
        "gitleaks", "dir", str(target),
        "--report-format", "json", "--report-path", str(out),
    ]


def _argv_k6(target: Path, out: Path, extra: dict[str, str]) -> list[str]:
    return ["k6", "run", "--summary-export", str(out), str(target)]


TOOLS: dict[str, dict[str, Any]] = {
    "semgrep": {
        "binary": "semgrep",
        "argv": _argv_semgrep,
        "reader": "apiforge.adapters.secreports.extract_semgrep",
        "install": "pip install semgrep",
        "hint": "semgrep exits nonzero when it finds findings — exit code is data",
    },
    "trivy": {
        "binary": "trivy",
        "argv": _argv_trivy,
        "reader": "apiforge.adapters.secreports.extract_trivy",
        "install": "https://aquasecurity.github.io/trivy/latest/getting-started/installation/",
        "hint": "scans the filesystem target; no daemon needed",
    },
    "gitleaks": {
        "binary": "gitleaks",
        "argv": _argv_gitleaks,
        "reader": "apiforge.adapters.secreports.extract_gitleaks",
        "install": "https://github.com/gitleaks/gitleaks#installing",
        "hint": "dir mode scans without git history",
    },
    "k6": {
        "binary": "k6",
        "argv": _argv_k6,
        "reader": "apiforge.adapters.testreports.extract_k6",
        "install": "https://k6.io/docs/get-started/installation/",
        "hint": "executes the k6 script — it makes real HTTP calls to its target",
    },
}


# The tool registry — every tool the platform knows how to read, whether or
# not `run tool` can execute it locally. Fields are *declared* metadata about
# the tool (with a source URL), except `installed`, which is measured via
# shutil.which at query time. `version` stays null: a registry entry does not
# pin a version, and we never guess one — the run's own report carries it.
# `modes` lists the execution modes the tool itself supports (declared data);
# `run tool` only ever executes `local` — docker/ECS/scheduled execution is
# the tool's own capability, invoked outside this platform. Distributed Load
# Testing on AWS is deliberately not integrated: `run` never touches AWS, so
# a DLT submission would break the collector boundary; it stays an external,
# policy-gated option the plan can name, never a verb here.
TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    # runnable locally via `run tool` — closed argv templates above
    "semgrep": {
        "category": "sast",
        "license": "LGPL-2.1",
        "input": "source tree",
        "output": "JSON report file",
        "capabilities": ["static analysis", "custom rules"],
        "limits": ["no interprocedural taint on all languages"],
        "cost": "oss",
        "needs_network": False,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.secreports.extract_semgrep",
        "compat": {"runtime": "python>=3.8"},
        "evidence_producer": "sec.semgrep.finding",
        "modes": ["local", "ci"],
        "runnable": True,
        "install": "pip install semgrep",
    },
    "trivy": {
        "category": "sca",
        "license": "Apache-2.0",
        "input": "filesystem or image",
        "output": "JSON report file",
        "capabilities": ["cve scan", "iac scan", "secret scan"],
        "limits": ["vulnerability db must be fetched by the tool itself"],
        "cost": "oss",
        "needs_network": False,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.secreports.extract_trivy",
        "compat": {"runtime": "binary"},
        "evidence_producer": "sec.trivy.finding",
        "modes": ["local", "ci"],
        "runnable": True,
        "install": "https://aquasecurity.github.io/trivy/latest/getting-started/installation/",
    },
    "gitleaks": {
        "category": "secret-scan",
        "license": "MIT",
        "input": "directory or git history",
        "output": "JSON report file",
        "capabilities": ["secret detection"],
        "limits": ["entropy rules produce false positives by design"],
        "cost": "oss",
        "needs_network": False,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.secreports.extract_gitleaks",
        "compat": {"runtime": "binary"},
        "evidence_producer": "sec.gitleaks.finding",
        "modes": ["local", "ci"],
        "runnable": True,
        "install": "https://github.com/gitleaks/gitleaks#installing",
    },
    # load generators — runnable or import-only per entry
    "k6": {
        "category": "load",
        "license": "AGPL-3.0",
        "input": "JS test script",
        "output": "--summary-export JSON",
        "capabilities": ["vu scripting", "thresholds", "rps/iterations metrics", "dropped_iterations signal"],
        "limits": ["generator can saturate before the target — watch dropped_iterations"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": True,  # Distributed Load Testing on AWS — external, policy-gated
        "parser": "apiforge.adapters.testreports.extract_k6",
        "compat": {"runtime": "binary"},
        "evidence_producer": "test.k6.summary",
        "modes": ["local", "docker", "ci", "aws-dlt"],
        "runnable": True,
        "install": "https://k6.io/docs/get-started/installation/",
    },
    "locust": {
        "category": "load",
        "license": "MIT",
        "input": "Python locustfile",
        "output": "--csv stats files / --html report",
        "capabilities": ["python user classes", "distributed workers"],
        "limits": ["stats CSV lacks per-request detail"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": True,
        "parser": "apiforge.adapters.testreports.extract_locust",
        "compat": {"runtime": "python>=3.9"},
        "evidence_producer": "test.locust.summary",
        "modes": ["local", "docker", "ci", "aws-dlt"],
        "runnable": False,
        "install": "pip install locust",
    },
    "jmeter": {
        "category": "load",
        "license": "Apache-2.0",
        "input": "JMX test plan",
        "output": "JTL CSV",
        "capabilities": ["gui plan authoring", "distributed mode", "plugins"],
        "limits": ["jtl is per-sample — aggregate here, never infer TPS"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": True,
        "parser": "apiforge.adapters.testreports.extract_jmeter",
        "compat": {"runtime": "java>=8"},
        "evidence_producer": "test.jmeter.summary",
        "modes": ["local", "docker", "ci", "aws-dlt"],
        "runnable": False,
        "install": "https://jmeter.apache.org/usermanual/get-started.html",
    },
    "gatling": {
        "category": "load",
        "license": "Apache-2.0",
        "input": "Scala/Java/Kotlin simulation",
        "output": "global_stats.json in the report bundle",
        "capabilities": ["high-throughput engine", "detailed percentile report"],
        "limits": ["report bundle must be generated by the run (-ro or post)"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.testreports.extract_gatling",
        "compat": {"runtime": "jvm"},
        "evidence_producer": "test.gatling.summary",
        "modes": ["local", "docker", "ci"],
        "runnable": False,
        "install": "https://docs.gatling.io/",
    },
    "vegeta": {
        "category": "load",
        "license": "MIT",
        "input": "targets file + rate",
        "output": "vegeta report -type=json",
        "capabilities": ["constant-rate attack", "precise latency histograms"],
        "limits": ["no scenario scripting — single request shape per run"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.testreports.extract_vegeta",
        "compat": {"runtime": "binary"},
        "evidence_producer": "test.vegeta.summary",
        "modes": ["local", "docker", "ci"],
        "runnable": False,
        "install": "https://github.com/tsenart/vegeta",
    },
    "wrk": {
        "category": "load",
        "license": "Apache-2.0",
        "input": "CLI flags + optional Lua script",
        "output": "stdout summary text",
        "capabilities": ["minimal high-rate generation"],
        "limits": ["no per-endpoint breakdown without scripting"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.testreports.extract_wrk",
        "compat": {"runtime": "binary"},
        "evidence_producer": "test.wrk.summary",
        "modes": ["local", "docker"],
        "runnable": False,
        "install": "https://github.com/wg/wrk",
    },
    "hey": {
        "category": "load",
        "license": "Apache-2.0",
        "input": "CLI flags",
        "output": "-o csv per-request times or stdout summary",
        "capabilities": ["quick single-endpoint probing"],
        "limits": ["no multi-step scenarios"],
        "cost": "oss",
        "needs_network": True,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.testreports.extract_hey",
        "compat": {"runtime": "binary"},
        "evidence_producer": "test.hey.summary",
        "modes": ["local", "docker"],
        "runnable": False,
        "install": "https://github.com/rakyll/hey",
    },
    "pytest-benchmark": {
        "category": "microbenchmark",
        "license": "BSD-2-Clause",
        "input": "pytest benchmark tests",
        "output": "--benchmark-json JSON",
        "capabilities": ["in-process timing", "histogram data"],
        "limits": ["measures code, not the deployed API — never a load run"],
        "cost": "oss",
        "needs_network": False,
        "needs_credentials": False,
        "local_support": True,
        "aws_support": False,
        "parser": "apiforge.adapters.testreports.extract_pytest_benchmark",
        "compat": {"runtime": "python"},
        "evidence_producer": "test.pytest_benchmark.summary",
        "modes": ["local", "ci"],
        "runnable": False,
        "install": "pip install pytest-benchmark",
    },
}


_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "[::1]"}


def _script_urls(target: Path) -> list[str]:
    """URL literals in the load script — the argv names the script, not the API."""
    import re

    try:
        text = Path(target).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    return sorted(set(re.findall(r"https?://[^\s\"'`<>{}]+", text)))


def _is_local(url: str) -> bool:
    from urllib.parse import urlparse

    return (urlparse(url).hostname or "").lower() in _LOCAL_HOSTS


def _load_target_gate(tool: str, target: Path, approval: str | None) -> None:
    """No load run against an unverifiable or remote target without approval.

    The script's URL literals are the evidence: every one local → the run is
    `local_reversible`. Any remote host — or *no* literal at all (e.g. a
    `__ENV.BASE_URL` we cannot resolve) → `sensitive`, which the default
    policy gates on `evidence` + `approval`.
    """
    if TOOL_REGISTRY[tool]["category"] != "load":
        return
    urls = _script_urls(target)
    if urls and all(_is_local(u) for u in urls):
        return
    from apiforge.policy.decide import ActionRequest, decide
    from apiforge.policy.loader import load_policy

    decision = decide(
        load_policy(),
        ActionRequest(
            verb="run.load",
            autonomy_class="sensitive",
            args=tuple(urls) or ("unresolvable-target",),
            target=str(target),
            detail={
                "evidence": ",".join(urls) or "no-url-literal",
                "approval": approval or "",
            },
        ),
    )
    if decision.outcome != "allow":
        missing = ", ".join(decision.missing_requirements) or "policy"
        raise RunError(
            "AF-RUN-PROD-GATE",
            f"{tool} targets {urls or ['unresolvable']} — {decision.outcome}: "
            f"missing {missing}; pass --approve <ref> once approval exists",
        )


def list_tools() -> list[dict[str, Any]]:
    """Registry rows + *measured* install status — never declared."""
    rows: list[dict[str, Any]] = []
    for name, meta in sorted(TOOL_REGISTRY.items()):
        binary = (TOOLS.get(name) or {}).get("binary", name)
        rows.append(
            {
                "name": name,
                "installed": shutil.which(str(binary)) is not None,
                **meta,
            }
        )
    return rows


def build_argv(
    tool: str, target: Path, out: Path, extra: dict[str, str]
) -> list[str]:
    """The fixed argv for a tool — visible via `--dry-run`."""
    spec = TOOLS.get(tool)
    if spec is None:
        raise RunError(
            "AF-RUN-TOOL-UNKNOWN",
            f"no runner for {tool!r}; allowlist: {sorted(TOOLS)}",
        )
    argv: list[str] = spec["argv"](Path(target), Path(out), extra)
    return argv


def run_tool(
    tool: str,
    target: Path,
    out: Path,
    extra: dict[str, str],
    timeout: int,
    dry_run: bool = False,
    approval: str | None = None,
) -> dict[str, object]:
    """Run the binary, read its report, return the inventory payload."""
    spec = TOOLS.get(tool)
    if spec is None:
        if tool in TOOL_REGISTRY:
            raise RunError(
                "AF-RUN-IMPORT-ONLY",
                f"{tool!r} is a report reader, not a runner — run it yourself "
                "(`local` mode only ever executes allowlisted binaries) and feed "
                "the report to `model "
                + tool
                + "`; registry install hint: "
                + str(TOOL_REGISTRY[tool].get("install", "")),
            )
        raise RunError(
            "AF-RUN-TOOL-UNKNOWN",
            f"no runner for {tool!r}; allowlist: {sorted(TOOLS)}",
        )
    argv = build_argv(tool, target, out, extra)
    if dry_run:
        return {"dry_run": True, "argv": argv}
    _load_target_gate(tool, Path(target), approval)
    binary = shutil.which(str(spec["binary"]))
    if binary is None:
        raise RunError(
            "AF-RUN-TOOL-MISSING",
            f"{spec['binary']} not on PATH — install: {spec['install']}",
        )
    argv[0] = binary
    try:
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RunError("AF-RUN-TIMEOUT", f"{tool} exceeded {timeout}s") from exc
    out_path = Path(out)
    if not out_path.is_file():
        raise RunError(
            "AF-RUN-NO-REPORT",
            f"{tool} exited {proc.returncode} without writing {out}: "
            f"{(proc.stderr or '').strip()[:300]}",
        )
    import importlib

    module, func = str(spec["reader"]).rsplit(".", 1)
    extract = getattr(importlib.import_module(module), func)
    inventory = extract(out_path)
    return {
        "tool": tool,
        "argv": argv,
        "exit_code": proc.returncode,
        "stderr_tail": (proc.stderr or "").strip()[-300:],
        "report": str(out_path),
        "diagnostics": [d.model_dump(mode="json") for d in inventory.diagnostics],
        "facts": [f.model_dump(mode="json") for f in inventory.facts],
        "framework": inventory.framework,
        "input_hashes": dict(inventory.input_hashes),
    }
