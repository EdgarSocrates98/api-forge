"""Cross-host capability audit for Claude, Codex/GPT, Devin and Copilot."""

from __future__ import annotations

from pathlib import Path

_HOST_LAYOUT = {
    "claude": ("CLAUDE.md", ".claude/skills", ".claude/agents"),
    "gpt-codex": ("AGENTS.md", ".agents/skills", ".agents/agents"),
    "devin": ("AGENTS.md", ".devin/skills"),
    "copilot": ("AGENTS.md", ".github/skills"),
}


def audit_host_parity(root: Path) -> dict[str, object]:
    root = Path(root)
    skills = (
        {path.name for path in (root / ".claude" / "skills").iterdir()}
        if (root / ".claude" / "skills").is_dir()
        else set()
    )
    hosts: dict[str, object] = {}
    for name, required in _HOST_LAYOUT.items():
        missing = [item for item in required if not (root / item).exists()]
        host_skills = root / required[-1] if required[-1].endswith("skills") else root / required[1]
        host_skill_names = {
            path.parent.name for path in host_skills.glob("*/SKILL.md")
        } if host_skills.is_dir() else set()
        # A host may add native extensions (for example Devin-only skills).
        # Parity requires every shared canonical skill, not identical counts.
        skill_count = len(host_skill_names & skills)
        hosts[name] = {
            "ready_for_core": not missing and skills <= host_skill_names,
            "missing": missing,
            "skill_count": skill_count,
            "supports_native_caveman_assets": (root / "vendor/caveman/plugins/caveman").is_dir(),
            "limitations": {
                "claude": ("MCP/hooks depend on Claude host installation.",),
                "gpt-codex": ("Native Codex hooks require .codex host configuration.",),
                "devin": ("Subagent and hook support depends on Devin runtime capabilities.",),
                "copilot": ("Copilot does not expose the same subagent/MCP surface.",),
            }[name],
        }
    return {
        "core_cli_declared": True,
        "core_source": "pyproject.toml [project.scripts] apiforge",
        "shared_skill_count": len(skills),
        "hosts": hosts,
        "full_parity": all(item["ready_for_core"] for item in hosts.values()),  # type: ignore[index]
        "honest_scope": "core analysis is shared; host hooks, MCP, subagents and slash commands are host-specific",
    }
