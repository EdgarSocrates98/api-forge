from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.migration.matrix import resolve_versions

MATRIX = Path("knowledge/runtime-migration/matrix.yaml")


def test_resolves_non_adjacent_python_versions() -> None:
    result = resolve_versions("python", "3.8", "3.14", MATRIX)
    assert result["intermediate"] == ("3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14")


def test_rejects_unknown_go_version() -> None:
    with pytest.raises(ContractError, match="unsupported go versions"):
        resolve_versions("go", "1.17", "1.24", MATRIX)
