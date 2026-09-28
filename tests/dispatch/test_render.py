import tomllib
from pathlib import Path

import yaml

from apiforge.dispatch.mirrors import mirror_drift, sync_mirrors
from apiforge.dispatch.render import render_all
from tests.dispatch.agent_support import write_agent


def _front(text: str) -> dict[str, str]:
    return yaml.safe_load(text.split("---\n")[1])


def test_read_only_agent_renders_per_host(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    sync_mirrors(tmp_path)
    claude = (tmp_path / ".claude/agents/api-contract-architect.md").read_text(encoding="utf-8")
    devin = (tmp_path / ".agents/agents/api-contract-architect.md").read_text(encoding="utf-8")
    codex = tomllib.loads(
        (tmp_path / ".codex/agents/api-contract-architect.toml").read_text(encoding="utf-8")
    )
    assert _front(claude) == {
        "name": "api-contract-architect",
        "description": _front(devin)["description"],
        "tools": "Read, Grep, Glob, Bash",
        "model": "opus",
    }
    assert set(_front(devin)) == {"name", "description"}
    assert codex["sandbox_mode"] == "read-only"
    assert codex["model_reasoning_effort"] == "high"
    assert codex["developer_instructions"].startswith("Follow `AGENT_PROTOCOL.md`.")
    assert "## Done when" in claude and "## Done when" in devin
    assert "rule_areas" not in claude and "apiforge_tools" not in devin


def test_writer_projects_write_tools_and_sandbox(tmp_path: Path) -> None:
    write_agent(
        tmp_path, "api-planner", access="writer", write_scope="docs/plans/", model_tier="fast"
    )
    rendered = render_all(tmp_path)
    claude = _front(rendered[".claude/agents/api-planner.md"].decode())
    codex = tomllib.loads(rendered[".codex/agents/api-planner.toml"].decode())
    assert claude["tools"].endswith("Edit, Write") and claude["model"] == "sonnet"
    assert codex["sandbox_mode"] == "workspace-write"
    assert codex["model_reasoning_effort"] == "medium"


def test_drift_orphan_and_non_agent_files(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    sync_mirrors(tmp_path)
    assert mirror_drift(tmp_path) == []
    codex = tmp_path / ".codex/agents/api-contract-architect.toml"
    codex.write_text(codex.read_text(encoding="utf-8") + "# hand edit\n", encoding="utf-8")
    (tmp_path / ".codex/agents/old-agent.toml").write_text('name = "old-agent"\n', encoding="utf-8")
    (tmp_path / ".claude/agents/README.md").write_text("# notes\n", encoding="utf-8")
    assert mirror_drift(tmp_path) == [
        ".claude/agents/README.md (non-agent file)",
        ".codex/agents/api-contract-architect.toml",
        ".codex/agents/old-agent.toml (orphan)",
    ]
    result = sync_mirrors(tmp_path)
    assert "-.codex/agents/old-agent.toml" in result["written"]
    assert (tmp_path / ".claude/agents/README.md").is_file()
    assert mirror_drift(tmp_path) == [".claude/agents/README.md (non-agent file)"]


def test_render_is_idempotent(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    write_agent(tmp_path, "api-planner", access="writer", write_scope="plans/")
    first = sync_mirrors(tmp_path)
    second = sync_mirrors(tmp_path)
    assert first["written"] and second["written"] == []
    assert render_all(tmp_path) == render_all(tmp_path)


def test_legacy_source_keeps_verbatim_markdown(tmp_path: Path) -> None:
    folder = tmp_path / "agents"
    folder.mkdir()
    source = "---\nname: legacy\ndescription: Old style.\n---\n\nSiga `AGENT_PROTOCOL.md`.\n"
    (folder / "legacy.md").write_bytes(source.encode("utf-8"))
    rendered = render_all(tmp_path)
    assert rendered[".claude/agents/legacy.md"].decode() == source
    assert rendered[".agents/agents/legacy.md"].decode() == source
    codex = tomllib.loads(rendered[".codex/agents/legacy.toml"].decode())
    assert "sandbox_mode" not in codex


def test_repository_mirrors_have_no_agent_drift() -> None:
    root = Path(__file__).resolve().parents[2]
    drift = [item for item in mirror_drift(root) if not item.endswith("(non-agent file)")]
    assert drift == []
