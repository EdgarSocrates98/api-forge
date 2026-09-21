import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()
CONTRACT = Path("tests/fixtures/openapi/orders-v1.yaml")


def _project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    (proj / "src" / "main" / "java").mkdir(parents=True)
    (proj / "pom.xml").write_text("<project/>\n", encoding="utf-8")
    return proj


def test_build_endpoint_cli(tmp_path: Path) -> None:
    proj = _project(tmp_path)
    diff_file = tmp_path / "change.diff"
    result = runner.invoke(
        app,
        [
            "build",
            "endpoint",
            "--contract",
            str(CONTRACT),
            "--operation-id",
            "createOrder",
            "--project",
            str(proj),
            "--write-diff",
            str(diff_file),
        ],
    )
    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    assert report["applied"] is True
    assert report["sandbox"]["delta"]["resolved"]
    assert diff_file.is_file()
    assert "CreateOrderController.java" in diff_file.read_text()
    assert not (proj / "src/main/java/com/apiforge").exists()


def test_build_endpoint_missing_op_exits_4(tmp_path: Path) -> None:
    proj = _project(tmp_path)
    result = runner.invoke(
        app,
        [
            "build",
            "endpoint",
            "--contract",
            str(CONTRACT),
            "--operation-id",
            "nope",
            "--project",
            str(proj),
        ],
    )
    assert result.exit_code == 4
    assert "AF-BUILD-OP-MISSING" in result.stdout


def test_promotion_without_approve_is_gated(tmp_path: Path) -> None:
    proj = _project(tmp_path)
    _git(proj)
    result = runner.invoke(
        app,
        [
            "build",
            "endpoint",
            "--contract",
            str(CONTRACT),
            "--operation-id",
            "createOrder",
            "--project",
            str(proj),
            "--into-worktree",
            "feat-orders",
        ],
    )
    assert result.exit_code == 4
    report = json.loads(result.stdout)
    promo = report["promotion"]
    assert promo["applied"] is False
    assert promo["decision"]["outcome"] == "gate"


def test_promotion_with_approve_writes_only_worktree(tmp_path: Path) -> None:
    proj = _project(tmp_path)
    _git(proj)
    result = runner.invoke(
        app,
        [
            "build",
            "endpoint",
            "--contract",
            str(CONTRACT),
            "--operation-id",
            "createOrder",
            "--project",
            str(proj),
            "--into-worktree",
            "feat-orders",
            "--approve",
        ],
    )
    assert result.exit_code == 0, result.stdout
    report = json.loads(result.stdout)
    promo = report["promotion"]
    assert promo["applied"] is True
    wt = Path(promo["worktree"]["path"])
    assert (wt / "src/main/java/com/apiforge/generated/CreateOrderController.java").is_file()
    assert not (proj / "src/main/java/com/apiforge").exists()


def _git(root: Path) -> None:
    for args in (
        ("init",),
        ("config", "user.email", "t@t"),
        ("config", "user.name", "t"),
        ("add", "-A"),
        ("commit", "-m", "init"),
    ):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)
