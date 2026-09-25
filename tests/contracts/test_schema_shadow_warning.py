"""Regression coverage for the public ``schema`` contract field."""

from __future__ import annotations

import subprocess
import sys


def test_schema_contract_imports_are_warning_free() -> None:
    """Keep the intentional wire field without leaking Pydantic shadow warnings."""

    code = """
import apiforge.contracts.context
import apiforge.contracts.distribution
import apiforge.contracts.workspace
"""
    result = subprocess.run(
        [sys.executable, "-W", "error::UserWarning", "-c", code],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
