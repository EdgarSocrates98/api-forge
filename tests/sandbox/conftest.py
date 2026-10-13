import shutil
from pathlib import Path

import pytest

from apiforge.adapters.fastapi.extractor import extract_fastapi

FIXTURE = Path("tests/fixtures/fastapi_flat")


@pytest.fixture
def sandbox_project(tmp_path: Path) -> Path:
    target = tmp_path / "project"
    shutil.copytree(FIXTURE, target)
    return target


@pytest.fixture
def analyze():
    """Real plan-1 extraction used as the injected analyzer."""

    def run(root: Path):
        return tuple(
            {"rule_id": "route", "path": str(f.measures["path"])}
            for f in extract_fastapi(root).facts
        )

    return run


@pytest.fixture
def analyze_stub():
    def run(root: Path):
        return ()

    return run
