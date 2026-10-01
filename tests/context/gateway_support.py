"""Shared materialization of analyzed fixture roots for Context Gateway tests."""

from __future__ import annotations

import shutil
from pathlib import Path

from apiforge.application.analyze import analyze_project

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
PAYMENTS = FIXTURES / "economy_payments"


def analyzed_root(tmp_path: Path, stack: str = "fastapi") -> Path:
    root = tmp_path / f"root-{stack}"
    shutil.copytree(
        PAYMENTS / stack, root / "proj", ignore=shutil.ignore_patterns(".apiforge", "__pycache__")
    )
    shutil.copyfile(PAYMENTS / "openapi.yaml", root / "openapi.yaml")
    analyze_project(root / "openapi.yaml", root / "proj", None, root / ".apiforge" / "case")
    return root
