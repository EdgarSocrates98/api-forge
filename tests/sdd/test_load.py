from pathlib import Path

import pytest
from pydantic import ValidationError

from apiforge.sdd.load import discover_features, load_artifact
from apiforge.sdd.models import PHASES, SddArtifact, load_profiles

ROOT = Path("tests/fixtures/sdd_root")


def test_discovers_only_uppercase_feature_dirs() -> None:
    found = discover_features(ROOT)
    assert "DEMO_FEATURE" in found.features
    assert found.features["DEMO_FEATURE"]["discover"].name == "discover.md"
    assert any(s.name == "templates" for s in found.skipped)
    assert any(s.name == "lowercase_dir" for s in found.skipped)
    assert any(s.name == "stray.txt" for s in found.skipped)


def test_load_artifact_parses_frontmatter() -> None:
    artifact = load_artifact(ROOT / "DEMO_FEATURE" / "discover.md")
    assert artifact.error is None
    assert artifact.meta["phase"] == "discover"
    assert "# Discover" in artifact.body


def test_load_artifact_without_frontmatter_is_named(tmp_path: Path) -> None:
    path = tmp_path / "bare.md"
    path.write_text("# no meta\n", encoding="utf-8")
    artifact = load_artifact(path)
    assert artifact.error == "AF-SDD-FRONTMATTER"


def test_load_artifact_non_mapping_meta_is_named(tmp_path: Path) -> None:
    path = tmp_path / "seq.md"
    path.write_text("---\n- a\n- b\n---\nbody\n", encoding="utf-8")
    artifact = load_artifact(path)
    assert artifact.error == "AF-SDD-FRONTMATTER"


def test_phases_order_is_canonical() -> None:
    assert PHASES == (
        "discover",
        "intent",
        "contract",
        "architecture",
        "plan",
        "build",
        "verify",
        "secure",
        "benchmark",
        "ship",
    )


def test_profiles_cover_all_four() -> None:
    profiles = load_profiles()
    assert set(profiles) == {"quick", "standard", "critical", "migration"}
    assert set(profiles["quick"]) == {"intent", "plan", "build", "verify", "ship"}
    assert "benchmark" not in profiles["standard"]
    assert len(profiles["critical"]) == len(PHASES)


def test_artifact_is_frozen() -> None:
    artifact = load_artifact(ROOT / "DEMO_FEATURE" / "discover.md")
    assert isinstance(artifact, SddArtifact)
    with pytest.raises(ValidationError):
        artifact.body = "mutated"  # type: ignore[misc]
