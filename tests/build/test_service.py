import shutil
import subprocess
from pathlib import Path

import pytest

from apiforge.build.service import build_endpoint

CONTRACT = Path("tests/fixtures/openapi/orders-v1.yaml")


@pytest.fixture
def empty_project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    (proj / "src" / "main" / "java").mkdir(parents=True)
    (proj / "pom.xml").write_text("<project/>\n", encoding="utf-8")
    return proj


def test_build_runs_sandbox_and_resolves(empty_project: Path) -> None:
    report = build_endpoint(CONTRACT, empty_project, "createOrder")
    assert report["applied"] is True
    assert report["refused"] == []
    assert report["files"] == [
        "src/main/java/com/apiforge/generated/CreateOrderController.java",
        "src/main/java/com/apiforge/generated/dto/Order.java",
    ]
    delta = report["sandbox"]["delta"]
    # before: both contract ops unimplemented; after: createOrder covered
    assert delta["resolved"]
    assert report["decision"]["outcome"] == "allow"
    assert report["receipt"]["diff_sha256"]
    # main tree untouched: no generated files on disk
    assert not (empty_project / "src/main/java/com/apiforge").exists()


def test_existing_target_refused(empty_project: Path) -> None:
    dest = empty_project / "src/main/java/com/apiforge/generated"
    dest.mkdir(parents=True)
    (dest / "CreateOrderController.java").write_text("x", encoding="utf-8")
    report = build_endpoint(CONTRACT, empty_project, "createOrder")
    assert report["applied"] is False
    assert report["refused"][0]["code"] == "AF-BUILD-TARGET-EXISTS"


def test_missing_operation_refused(empty_project: Path) -> None:
    report = build_endpoint(CONTRACT, empty_project, "nope")
    assert report["applied"] is False
    assert report["refused"][0]["code"] == "AF-BUILD-OP-MISSING"


def test_promotion_gated_without_approval(tmp_path: Path, empty_project: Path) -> None:
    _git_init(empty_project)
    report = build_endpoint(CONTRACT, empty_project, "createOrder", promote="feat-x", approve=False)
    promo = report["promotion"]
    assert promo is not None and promo["applied"] is False
    assert promo["decision"]["outcome"] == "gate"
    assert "approval" in promo["decision"]["missing_requirements"]


def test_promotion_with_approval_lands_in_worktree_only(
    tmp_path: Path, empty_project: Path
) -> None:
    _git_init(empty_project)
    report = build_endpoint(CONTRACT, empty_project, "createOrder", promote="feat-x", approve=True)
    promo = report["promotion"]
    assert promo is not None and promo["applied"] is True
    wt = Path(promo["worktree"]["path"])
    assert (wt / "src/main/java/com/apiforge/generated/CreateOrderController.java").is_file()
    # main tree still clean of generated code
    assert not (empty_project / "src/main/java/com/apiforge").exists()
    shutil.rmtree(wt, ignore_errors=True)


def _git_init(root: Path) -> None:
    def run(*args: str) -> None:
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)

    run("init")
    run("config", "user.email", "test@example.com")
    run("config", "user.name", "Test")
    run("add", "-A")
    run("commit", "-m", "init")
