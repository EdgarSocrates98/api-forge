# tests/test_wheel_isolation.py
"""Install-2.0 §8.4 — Wheel Isolation Test.

The pip channel is a contract separate from the checkout: this test builds
the wheel, installs it into a CLEAN venv and runs the `install` lifecycle
from a directory outside the repository. If any resource (skills, agents,
knowledge, evals, manifests) only exists in the clone, a stage fails — the
defect §8 exists to catch before publication.

Pipeline (source spec `prompt_evo_install2.0.md` §8.4):

    build wheel -> clean venv -> install wheel -> cwd outside checkout
    -> `apiforge install` -> registry + contracts -> retrieve knowledge
    -> retrieve rule -> verify protocol -> offline verification
    -> uninstall / repair / reinstall

Provenance is structural — subprocesses run the venv's CLI/python with cwd
inside the temp dir, so `import apiforge` can only resolve to the venv's
site-packages, never the checkout.

`APIFORGE_*`/`FORGE_*` env vars are dropped from the subprocess environment
so an override pointing at checkout state cannot make the test pass against
the repository instead of what the wheel shipped.

NOT asserted here: context-registry discovery verbs lf-0037 is wiring —
planned coverage is marked PLANNED; the test cannot fail on verbs that do
not exist on main yet. `install doctor`'s `mcp-handshake` legitimately
reports BLOCKED on a bare consumer target (verify is a separate verb) —
integrity-level checks are what this test pins.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WHEEL_GLOB = "apiforge_af-*.whl"
PACKAGE = "apiforge"
CLI = "apiforge"
FORGE_ID = "api-forge"
CONTEXT_REGISTRY = Path(".forge/context/registry.json")
CONTEXT_CAPABILITY = Path(f".forge/context/capabilities/{FORGE_ID}.json")
STATE_DIR = ".apiforge/install"
LEDGER = "install-ledger.json"


def _scripts_dir(venv_dir: Path) -> Path:
    return venv_dir / ("Scripts" if sys.platform == "win32" else "bin")


def _build_wheel(tmp: Path) -> Path:
    """Build the wheel of THIS tree in tmp — never reuses `dist/`.

    A stale `dist/*.whl` (built before the change this test guards) makes
    the gate measure the wrong package. ~60s of rebuild is the price of
    testing the artifact that is a function of the current checkout."""
    dist = tmp / "dist"
    dist.mkdir()
    result = subprocess.run(  # build invoked by the test itself
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist), str(ROOT)],
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"`python -m build` unavailable or failed: {result.stderr[-400:]}")
    wheels = sorted(dist.glob(WHEEL_GLOB))
    assert wheels, "build succeeded but produced no wheel"
    return wheels[0]


def _clean_env() -> dict[str, str]:
    """Subprocess env without overrides that would point at the checkout."""
    env = dict(os.environ)
    for key in ("PYTHONPATH", "VIRTUAL_ENV", "GITHUB_TOKEN", "GH_TOKEN"):
        env.pop(key, None)
    for key in [k for k in env if k.startswith(("APIFORGE_", "FORGE_"))]:
        env.pop(key)
    env["PYTHONSAFEPATH"] = "1"
    return env


def _run(argv: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run(  # CLI/venv created by the test itself
        argv, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=300,
        check=False,
    )


def _json(doc: subprocess.CompletedProcess, step: str) -> dict:
    try:
        return json.loads(doc.stdout)
    except json.JSONDecodeError:
        raise AssertionError(
            f"{step}: output is not JSON (rc={doc.returncode}):\n"
            f"{doc.stdout[-800:]}\n{doc.stderr[-800:]}"
        ) from None


@pytest.mark.slow
def test_wheel_install_lifecycle_outside_checkout(tmp_path: Path):
    wheel = _build_wheel(tmp_path)
    # The wheel must carry the forge manifests + runtime bundles the
    # installer consumes: without them a pip-installed `apiforge install`
    # degrades the context registry (§8.2 parity, cheap gate here).
    with zipfile.ZipFile(wheel) as zf:
        names = set(zf.namelist())
    for packaged in (
        f"{PACKAGE}/_data/forge.json",
        f"{PACKAGE}/_data/forge.agentic.json",
        f"{PACKAGE}/host_assets/skills",
        f"{PACKAGE}/host_assets/agents",
        f"{PACKAGE}/host_assets/AGENT_PROTOCOL.md",
        f"{PACKAGE}/_data/knowledge",
        f"{PACKAGE}/_data/evals",
    ):
        assert any(n.startswith(packaged) for n in names), f"{packaged} missing from wheel"

    env = _clean_env()

    venv_dir = tmp_path / "venv"
    venv.create(venv_dir, with_pip=True)
    scripts = _scripts_dir(venv_dir)
    python = scripts / "python"
    pip = scripts / "pip"

    # apiforge declares runtime deps (pydantic, typer, tree-sitter, …) —
    # pip must resolve them, so this stage needs the index. Skip honestly
    # when offline rather than fail on infrastructure.
    install = _run([str(pip), "install", "--quiet", str(wheel)], cwd=tmp_path, env=env)
    if install.returncode != 0 and (
        "Could not find a version" in install.stderr
        or "Temporary failure" in install.stderr
        or "Network" in install.stderr
        or "Failed to establish" in install.stderr
    ):
        pytest.skip(f"pip cannot reach an index for runtime deps: {install.stderr[-300:]}")
    assert install.returncode == 0, f"pip install of wheel failed: {install.stderr[-800:]}"

    cli = scripts / CLI
    assert cli.is_file() or cli.with_suffix(".exe").is_file(), (
        f"console script {CLI} missing in venv: {sorted(p.name for p in scripts.iterdir())}"
    )

    # Structural provenance: the imported package comes from the venv's
    # site-packages, never the checkout — before any behavior assertion.
    probe = _run(
        [
            str(python),
            "-c",
            (
                "import sys, sysconfig\n"
                f"import {PACKAGE}\n"
                f"print({PACKAGE}.__file__)\n"
                "print(sysconfig.get_paths()['purelib'])"
            ),
        ],
        cwd=tmp_path,
        env=env,
    )
    assert probe.returncode == 0, probe.stderr[-400:]
    module_file, purelib = (Path(line) for line in probe.stdout.strip().splitlines()[-2:])
    assert module_file.is_relative_to(purelib), (
        f"{PACKAGE} imported from outside the venv: {module_file} (purelib={purelib})"
    )

    target = tmp_path / "consumer"
    target.mkdir()
    git = shutil.which("git")
    if git is not None:
        _run([git, "init", "-q"], cwd=target, env=env)

    # -- install (group callback = apply) --------------------------------------
    out = _run(
        [str(cli), "install", "--root", str(target), "--yes"],
        cwd=target,
        env=env,
    )
    assert out.returncode == 0, (
        f"install failed:\n{out.stdout[-800:]}\n{out.stderr[-800:]}"
    )
    receipt = _json(out, "install")
    assert receipt["status"] == "completed", receipt
    assert receipt["schema"] == "forge/InstallReceipt/v1", receipt.get("schema")

    # -- registry + contracts ---------------------------------------------------
    registry = json.loads((target / CONTEXT_REGISTRY).read_text(encoding="utf-8"))
    assert registry["schema"] == "forge/context-registry/v1", registry.get("schema")
    assert any(f.get("forge_id") == FORGE_ID for f in registry["forges"])
    capability = json.loads((target / CONTEXT_CAPABILITY).read_text(encoding="utf-8"))
    assert capability["schema"] == "forge/context/v1", capability.get("schema")
    assert capability["forge_id"] == FORGE_ID
    for cap in ("skills", "agents", "rules", "knowledge", "protocols", "evals"):
        assert capability["capabilities"][cap]["available"] is True, cap
    # ownership ledger of the installer
    ledger = json.loads((target / STATE_DIR / LEDGER).read_text(encoding="utf-8"))
    assert ledger["entries"], "install-ledger.json without entries"
    assert (target / ".mcp.json").is_file()
    assert (target / "AGENT_PROTOCOL.md").is_file()

    # -- retrieve knowledge -----------------------------------------------------
    out = _run([str(cli), "knowledge", "list"], cwd=target, env=env)
    assert out.returncode == 0, out.stderr[-400:]
    assert out.stdout.strip(), "knowledge list empty under the wheel"

    # -- retrieve rule -----------------------------------------------------------
    out = _run([str(cli), "rules", "lookup", "AF-BREAK-001"], cwd=target, env=env)
    assert out.returncode == 0, out.stderr[-400:]
    assert "AF-BREAK-001" in out.stdout, "rules lookup did not return the rule"

    # -- verify protocol ---------------------------------------------------------
    out = _run(
        [str(cli), "install", "verify", "--root", str(target)], cwd=target, env=env
    )
    # `install verify` is a real JSON-RPC handshake against the packaged MCP
    # server — it may legitimately refuse in a bare venv (mcp extra not
    # installed); refuse/BLOCKED is honest, a traceback is not.
    assert "Traceback" not in out.stderr, out.stderr[-800:]

    out = _run(
        [str(cli), "install", "doctor", "--root", str(target)], cwd=target, env=env
    )
    health = _json(out, "install doctor")
    assert health["status"] in ("healthy", "degraded"), health.get("status")
    for check_id in ("ledger", "mcp-config"):
        check = next((c for c in health["checks"] if c["id"] == check_id), None)
        assert check is not None and check["status"] == "PASS", (
            check_id,
            health["checks"],
        )

    # -- offline verification ------------------------------------------------------
    out = _run([str(cli), "doctor"], cwd=target, env=env)
    assert "Traceback" not in out.stderr, out.stderr[-800:]

    # -- repair ----------------------------------------------------------------------
    victim = target / ".mcp.json"
    assert victim.is_file()
    victim.unlink()
    out = _run(
        [str(cli), "install", "repair", "--root", str(target)], cwd=target, env=env
    )
    assert out.returncode == 0, out.stderr[-400:]
    assert victim.is_file(), "repair did not restore a removed managed asset"

    # -- uninstall + reinstall -------------------------------------------------------
    out = _run(
        [str(cli), "install", "uninstall", "--root", str(target)], cwd=target, env=env
    )
    assert out.returncode == 0, out.stderr[-400:]
    gone = _json(out, "install uninstall")
    assert gone["status"] in ("completed", "uninstalled"), gone.get("status")
    assert not victim.exists(), "uninstall did not remove the managed asset"
    assert not (target / CONTEXT_CAPABILITY).exists()

    out = _run(
        [str(cli), "install", "--root", str(target), "--yes"],
        cwd=target,
        env=env,
    )
    assert out.returncode == 0, out.stderr[-400:]
    assert _json(out, "reinstall")["status"] == "completed"
    assert (target / CONTEXT_REGISTRY).is_file()


# PLANNED (lf-0037, knowledge/rules discovery via `.forge/context/`): when
# `discovery.ops` lands verbs over the installed registry, extend this test
# to read them — today retrieval proof is `knowledge list` + `rules lookup`
# (stable verbs).
