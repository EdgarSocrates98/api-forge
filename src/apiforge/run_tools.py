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
) -> dict[str, object]:
    """Run the binary, read its report, return the inventory payload."""
    spec = TOOLS.get(tool)
    if spec is None:
        raise RunError(
            "AF-RUN-TOOL-UNKNOWN",
            f"no runner for {tool!r}; allowlist: {sorted(TOOLS)}",
        )
    argv = build_argv(tool, target, out, extra)
    if dry_run:
        return {"dry_run": True, "argv": argv}
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
