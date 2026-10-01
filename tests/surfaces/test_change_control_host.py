from __future__ import annotations

from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from apiforge.application.change_control import run_change_control
from apiforge.integrations.replay import ReplayAdapter
from apiforge.surfaces.change_control_host import (
    render_ui_document,
    serve_change_control,
    surface_projection,
)


def test_ide_and_ui_projections_preserve_canonical_result(tmp_path: Path) -> None:
    bundle = ReplayAdapter().load(Path("tests/fixtures/api_git_cicd/change_bundle.json"))
    run_dir = tmp_path / "run"
    run_change_control(bundle, run_dir)
    ide = surface_projection(run_dir, "ide")
    ui = surface_projection(run_dir, "ui")
    assert ide["result"] == ui["result"]
    assert ide["result"]["status"] == "review"
    assert "CapabilityResult/v1" == ide["contract"]
    assert "API Forge change-control" in render_ui_document(run_dir)


def test_remote_host_requires_authentication(tmp_path: Path) -> None:
    bundle = ReplayAdapter().load(Path("tests/fixtures/api_git_cicd/change_bundle.json"))
    run_dir = tmp_path / "run"
    run_change_control(bundle, run_dir)

    thread = Thread(
        target=serve_change_control,
        kwargs={"run_dir": run_dir, "host": "127.0.0.1", "port": 18765, "auth_token": "secret"},
        daemon=True,
    )
    thread.start()
    request = Request("http://127.0.0.1:18765/api/ui")
    try:
        urlopen(request, timeout=2)
    except HTTPError as exc:
        assert exc.code == 401
    else:
        raise AssertionError("unauthenticated remote surface unexpectedly succeeded")
    authorized = Request(
        "http://127.0.0.1:18765/api/ui", headers={"Authorization": "Bearer secret"}
    )
    with urlopen(authorized, timeout=2) as response:
        assert response.status == 200
