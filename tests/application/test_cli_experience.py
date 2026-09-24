import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app
from tests.runtime.test_runtime import make_task


def test_modular_experience_status_matches_legacy_payload(tmp_path: Path) -> None:
    make_task(tmp_path)
    runner = CliRunner()
    legacy = runner.invoke(app, ["status", "evolve-orders-api", "--root", str(tmp_path)])
    modular = runner.invoke(
        app,
        ["experience", "status", "evolve-orders-api", "--root", str(tmp_path)],
    )
    assert legacy.exit_code == modular.exit_code == 0, (legacy.stdout, modular.stdout)
    assert json.loads(legacy.stdout) == json.loads(modular.stdout)
