"""``apiforge ai`` — observe an AI host and open it when supported.

Real flow per host, every step a documented command verified against the
installed versions (devin 3000.11.3, Claude Code 2.1.295, codex-cli
0.160.0, observed 2026-10):

1. detect the binary (``shutil.which``);
2. read the version (``<bin> --version``);
3. check authentication through the official status subcommand — the
   receipt carries only the ``logged_in`` boolean, never raw output (it
   may list credential paths);
4. read the install integration state in the repo (``install status`` +
   the managed ``.mcp.json`` server key);
5. with ``--launch`` and a TTY, run ``<bin>`` in the repo directory — the
   host REPL inherits the terminal and its exit code lands in the receipt.
   Without a TTY or ``--launch``, the receipt carries ``launch_command``
   for the operator to paste.

A logged-out host is never launched: the receipt names the official login
command and never prompts for a credential.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HOSTS: tuple[str, ...] = ("claude", "devin", "codex", "copilot")

Runner = Callable[[list[str]], tuple[int, str]]
Which = Callable[[str], str | None]

_OUTPUT_MAX = 400
_TIMEOUT_S = 10

LOGIN_HINTS: dict[str, str] = {
    "devin": "devin auth login",
    "claude": "claude auth login",
    "codex": "codex login",
    "copilot": "copilot",  # copilot login happens inside the REPL
}


@dataclass(frozen=True)
class _HostCmd:
    binary: str
    auth_status: tuple[str, ...] | None


_HOST_CMDS: dict[str, _HostCmd] = {
    "devin": _HostCmd("devin", ("auth", "status")),
    "claude": _HostCmd("claude", ("auth", "status")),
    "codex": _HostCmd("codex", ("login", "status")),
    "copilot": _HostCmd("copilot", None),
}


def _default_runner(argv: list[str]) -> tuple[int, str]:
    proc = subprocess.run(  # fixed argv from _HOST_CMDS, never shell
        argv,
        check=False,
        capture_output=True,
        text=True,
        timeout=_TIMEOUT_S,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _logged_in(host: str, output: str) -> bool | None:
    """Only the boolean. No readable positive/negative evidence → ``None``."""
    if host == "claude":
        try:
            doc = json.loads(output)
        except ValueError:
            doc = None
        if isinstance(doc, dict) and "loggedIn" in doc:
            return bool(doc["loggedIn"])
    low = output.lower()
    # negative before positive: "Not logged in" contains "logged in"
    if any(frag in low for frag in ("not logged", "logged out", "no credentials", "unauthorized")):
        return False
    if "logged in" in low:
        return True
    return None


def _call(
    executable: str,
    argv: list[str],
    runner: Runner,
) -> tuple[int, str] | dict[str, Any]:
    try:
        return runner([executable, *argv])
    except subprocess.TimeoutExpired as exc:
        return {
            "status": "refused",
            "reason": "host_cli_timeout",
            "command": " ".join(argv),
            "timeout_s": exc.timeout,
        }
    except OSError as exc:
        return {
            "status": "refused",
            "reason": "host_cli_failed",
            "command": " ".join(argv),
            "output": str(exc)[-_OUTPUT_MAX:],
        }


def _mcp_key_state(root: Path) -> dict[str, Any]:
    """Observe the managed ``mcpServers.apiforge`` key without writing."""
    mcp_file = root / ".mcp.json"
    if not mcp_file.is_file():
        return {"file": ".mcp.json", "state": "missing"}
    try:
        doc = json.loads(mcp_file.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, ValueError):
        return {"file": ".mcp.json", "state": "unreadable"}
    servers = doc.get("mcpServers") or {}
    return {
        "file": ".mcp.json",
        "state": "present" if "apiforge" in servers else "absent",
    }


def _integration(root: Path) -> dict[str, Any]:
    """Install state in the repo, read-only — ``unverified`` when never
    installed; status must never crash the host-opening flow."""
    from apiforge import _installkit as kit
    from apiforge.install import service

    try:
        st = service.status(scope="project", root=root)
    except (kit.InstallError, OSError, ValueError, TypeError, KeyError) as exc:
        return {"state": "unknown", "error": str(exc)[:200]}
    return {
        "state": st.get("status", "unknown"),
        "drift_ok": (st.get("drift") or {}).get("ok"),
        "ledger_entries": st.get("ledger_entries"),
        "mcp": _mcp_key_state(root),
    }


def host_state(
    host: str,
    *,
    root: Path,
    which: Which | None = None,
    runner: Runner | None = None,
) -> dict[str, Any]:
    """Observed host state: binary, version, auth, integration, open cmd."""
    if host not in HOSTS:
        return {
            "host": host,
            "state": "refused",
            "reason": "host_unknown",
            "code": "AF-HOST-UNKNOWN",
            "known": list(HOSTS),
        }
    which = which or shutil.which
    runner = runner or _default_runner
    cmd = _HOST_CMDS[host]
    state: dict[str, Any] = {
        "host": host,
        "binary": cmd.binary,
        "launch_command": cmd.binary,
    }
    path = which(cmd.binary)
    if not path:
        state["state"] = "NOT_DETECTED"
        return state
    state["binary_path"] = path
    state["state"] = "DETECTED"

    version = _call(path, ["--version"], runner)
    if isinstance(version, dict):
        state["version_refused"] = version
    else:
        rc, out = version
        first = next((line.strip() for line in out.splitlines() if line.strip()), "")
        state["version"] = first or None
        state["state"] = "SUPPORTED" if rc == 0 else "DETECTED"

    if cmd.auth_status is None:
        state["logged_in"] = None
        state["auth_note"] = "no documented status subcommand in this revision"
    else:
        auth = _call(path, list(cmd.auth_status), runner)
        if isinstance(auth, dict):
            state["auth_refused"] = auth
            state["logged_in"] = None
        else:
            state["logged_in"] = _logged_in(host, auth[1])
    if state.get("logged_in") is False:
        state["login_hint"] = LOGIN_HINTS[host]

    state["integration"] = _integration(root)
    state["state"] = _final_state(state)
    return state


def _final_state(state: dict[str, Any]) -> str:
    if state.get("logged_in") is False:
        return "NEEDS_LOGIN"
    integ = (state.get("integration") or {}).get("state")
    if integ == "healthy":
        return "READY"
    if integ in {"degraded", "broken"}:
        return "INTEGRATION_" + str(integ).upper()
    return "SUPPORTED"


def ai_flow(
    target: str,
    *,
    root: Path,
    launch: bool = False,
    tty: bool | None = None,
    which: Which | None = None,
    runner: Runner | None = None,
    exec_host: Callable[[str, Path], int] | None = None,
) -> dict[str, Any]:
    """The host-open flow: ``target`` ``all`` measures the four hosts; a
    single host plus ``launch`` + TTY opens the real binary in ``root``.

    ``exec_host(path, root)`` is the launch seam — the CLI injects
    ``subprocess.call``; tests inject a spy. Without a TTY, ``launched``
    is false and ``launch_refused`` says why — never silence."""
    root = Path(root)
    names = list(HOSTS) if target == "all" else [target]
    states = [host_state(name, root=root, which=which, runner=runner) for name in names]
    receipt: dict[str, Any] = {
        "repo": root.as_posix(),
        "hosts": states,
        "launched": False,
    }
    if target == "all" or not launch:
        if launch:
            receipt["launch_refused"] = "selector `all` does not launch: pick one host"
        return receipt

    state = states[0]
    tty = sys.stdin.isatty() if tty is None else tty
    if state["state"] == "NOT_DETECTED":
        receipt["launch_refused"] = "host_missing"
    elif state["state"] == "NEEDS_LOGIN":
        receipt["launch_refused"] = "login_required"
        receipt["login_hint"] = state.get("login_hint")
    elif not tty:
        receipt["launch_refused"] = "no_tty"
    else:
        # Path came from shutil.which — same trust level as any REPL start.
        exec_fn = exec_host or (lambda path, cwd: subprocess.call([path], cwd=str(cwd)))
        receipt["launched"] = True
        receipt["host_exit_code"] = exec_fn(state["binary_path"], root)
    return receipt


__all__ = ["HOSTS", "ai_flow", "host_state"]
