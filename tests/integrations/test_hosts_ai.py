from __future__ import annotations

import subprocess
from pathlib import Path

from apiforge.integrations import hosts


def _which(present: dict[str, str]):
    return lambda name: present.get(name)


def _runner(script: dict[tuple[str, ...], tuple[int, str]]):
    def run(argv: list[str]) -> tuple[int, str]:
        key = tuple(argv[1:])
        return script.get(key, (1, "unknown command"))

    return run


def _devin_which() -> hosts.Which:
    return _which({"devin": "/usr/bin/devin"})


def _devin_runner() -> hosts.Runner:
    return _runner(
        {
            ("--version",): (0, "devin 3000.11.3 (9c803229faa4)\n"),
            ("auth", "status"): (0, "Logged in as edgar\n"),
        }
    )


def test_unknown_host_is_refused(tmp_path: Path) -> None:
    state = hosts.host_state("gemini", root=tmp_path)
    assert state["state"] == "refused"
    assert state["code"] == "AF-HOST-UNKNOWN"
    assert "claude" in state["known"]


def test_missing_binary_is_not_detected(tmp_path: Path) -> None:
    state = hosts.host_state("devin", root=tmp_path, which=_which({}))
    assert state["state"] == "NOT_DETECTED"
    assert state["launch_command"] == "devin"


def test_detected_logged_out_host_needs_login(tmp_path: Path) -> None:
    runner = _runner(
        {
            ("--version",): (0, "devin 3000.11.3\n"),
            ("auth", "status"): (0, "Not logged in\n"),
        }
    )
    state = hosts.host_state("devin", root=tmp_path, which=_devin_which(), runner=runner)
    assert state["logged_in"] is False
    assert state["state"] == "NEEDS_LOGIN"
    assert state["login_hint"] == "devin auth login"


def test_not_logged_in_is_not_parsed_as_logged_in() -> None:
    assert hosts._logged_in("codex", "Not logged in") is False
    assert hosts._logged_in("codex", "Logged in using ChatGPT") is True
    assert hosts._logged_in("claude", '{"loggedIn": true}') is True
    assert hosts._logged_in("claude", '{"loggedIn": false}') is False
    assert hosts._logged_in("devin", "garbage") is None


def test_supported_host_without_install(tmp_path: Path) -> None:
    state = hosts.host_state("devin", root=tmp_path, which=_devin_which(), runner=_devin_runner())
    assert state["state"] == "SUPPORTED"
    assert state["version"] == "devin 3000.11.3 (9c803229faa4)"
    assert state["integration"]["state"] == "unverified"
    assert state["integration"]["mcp"]["state"] == "missing"


def test_version_timeout_is_refused_not_crash(tmp_path: Path) -> None:
    def runner(argv: list[str]) -> tuple[int, str]:
        raise subprocess.TimeoutExpired(argv, 10)

    state = hosts.host_state("devin", root=tmp_path, which=_devin_which(), runner=runner)
    assert state["version_refused"]["reason"] == "host_cli_timeout"
    # refused probe is recorded, never hidden — final state still lands
    # SUPPORTED via the shared state machine (parity with spark-forge-aws)
    assert state["state"] == "SUPPORTED"


def test_all_selector_never_launches(tmp_path: Path) -> None:
    called: list[str] = []
    receipt = hosts.ai_flow(
        "all",
        root=tmp_path,
        launch=True,
        tty=True,
        which=_devin_which(),
        runner=_devin_runner(),
        exec_host=lambda path, cwd: called.append(path) or 0,
    )
    assert receipt["launched"] is False
    assert receipt["launch_refused"].startswith("selector `all`")
    assert called == []


def test_launch_requires_tty(tmp_path: Path) -> None:
    receipt = hosts.ai_flow(
        "devin",
        root=tmp_path,
        launch=True,
        tty=False,
        which=_devin_which(),
        runner=_devin_runner(),
    )
    assert receipt["launched"] is False
    assert receipt["launch_refused"] == "no_tty"


def test_launch_logged_out_is_refused(tmp_path: Path) -> None:
    runner = _runner(
        {
            ("--version",): (0, "devin x\n"),
            ("auth", "status"): (0, "Not logged in"),
        }
    )
    receipt = hosts.ai_flow(
        "devin",
        root=tmp_path,
        launch=True,
        tty=True,
        which=_devin_which(),
        runner=runner,
    )
    assert receipt["launched"] is False
    assert receipt["launch_refused"] == "login_required"
    assert receipt["login_hint"] == "devin auth login"


def test_launch_runs_binary_in_repo(tmp_path: Path) -> None:
    seen: list[tuple[str, Path]] = []
    receipt = hosts.ai_flow(
        "devin",
        root=tmp_path,
        launch=True,
        tty=True,
        which=_devin_which(),
        runner=_devin_runner(),
        exec_host=lambda path, cwd: seen.append((path, cwd)) or 0,
    )
    assert receipt["launched"] is True
    assert receipt["host_exit_code"] == 0
    assert seen == [("/usr/bin/devin", tmp_path)]


def test_copilot_has_no_auth_subcommand(tmp_path: Path) -> None:
    state = hosts.host_state(
        "copilot",
        root=tmp_path,
        which=_which({"copilot": "/usr/bin/copilot"}),
        runner=_runner({("--version",): (0, "copilot 1.0\n")}),
    )
    assert state["logged_in"] is None
    assert "auth_note" in state
    assert state["state"] == "SUPPORTED"


def test_healthy_install_is_ready(tmp_path: Path, monkeypatch) -> None:
    from apiforge.install import service

    monkeypatch.setattr(
        service,
        "status",
        lambda *, scope, root: {
            "status": "healthy",
            "drift": {"ok": 3},
            "ledger_entries": 3,
        },
    )
    (tmp_path / ".mcp.json").write_text(
        '{"mcpServers": {"apiforge": {"command": "apiforge-mcp"}}}',
        encoding="utf-8",
    )
    state = hosts.host_state("devin", root=tmp_path, which=_devin_which(), runner=_devin_runner())
    assert state["state"] == "READY"
    assert state["integration"]["mcp"]["state"] == "present"
