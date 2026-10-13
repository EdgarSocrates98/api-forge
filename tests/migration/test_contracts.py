from pathlib import Path

import pytest

from apiforge.migration.contracts import MigrationSpec


def test_spec_identity_is_stable() -> None:
    spec = MigrationSpec(
        project_root=str(Path("tests/fixtures/migrations/go/go121-to-124").resolve()),
        ecosystem="go",
        source_version="1.21",
        target_version="1.24",
    )
    assert "go:1.21->1.24:" in spec.identity()


def test_spec_rejects_external_mutation() -> None:
    with pytest.raises(ValueError, match="read-only"):
        MigrationSpec(
            project_root=".",
            ecosystem="java",
            source_version="11",
            target_version="21",
            read_only=False,
        )
