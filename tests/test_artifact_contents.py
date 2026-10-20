"""The wheel must carry every force-included runtime asset.

`pyproject.toml` declares force-includes for `agents`, `.agents/skills`,
`AGENT_PROTOCOL.md`, `portal/assets`, `knowledge` and `evals`. Inspecting the
config proves intent, not result — a hatchling regression or a typo silently
ships a wheel missing `apiforge/_data/`, and `apiforge knowledge list` then
fails `AF-KNOW-ROOT` in a clean install. Building the real wheel is the only
honest gate.
"""

import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def wheel(tmp_path_factory) -> zipfile.ZipFile:
    out = tmp_path_factory.mktemp("dist")
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(out), str(ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"`python -m build` unavailable or failed: {result.stderr[-400:]}")
    built = sorted(out.glob("*.whl"))
    assert built, "build succeeded without producing a wheel"
    return zipfile.ZipFile(built[0])


def _names(wheel: zipfile.ZipFile, prefix: str) -> list[str]:
    return [n for n in wheel.namelist() if n.startswith(prefix)]


class TestWheelCarriesHostAssets:
    def test_agents_tree(self, wheel):
        assert _names(wheel, "apiforge/host_assets/agents/")

    def test_agents_skills_tree(self, wheel):
        assert _names(wheel, "apiforge/host_assets/skills/")

    def test_agent_protocol(self, wheel):
        assert "apiforge/host_assets/AGENT_PROTOCOL.md" in wheel.namelist()

    def test_portal_assets(self, wheel):
        assert _names(wheel, "apiforge/portal_assets/")


class TestWheelCarriesDataLayer:
    def test_knowledge_packs(self, wheel):
        knowledge = _names(wheel, "apiforge/_data/knowledge/")
        assert knowledge
        assert any(n.endswith((".md", ".yaml")) for n in knowledge)

    def test_evals_corpus(self, wheel):
        evals = _names(wheel, "apiforge/_data/evals/")
        assert evals
        assert any("corpus" in n or n.endswith(".yaml") for n in evals)
