"""Host-neutral adapters for Claude, GPT/Codex, Devin and Copilot."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HostAdapter:
    name: str
    instruction_file: str
    skill_directory: str
    supports_subagents: bool
    supports_mcp: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "instruction_file": self.instruction_file,
            "skill_directory": self.skill_directory,
            "supports_subagents": self.supports_subagents,
            "supports_mcp": self.supports_mcp,
        }


HOSTS = (
    HostAdapter("claude", "CLAUDE.md", ".claude/skills", True, True),
    HostAdapter("gpt-codex", "AGENTS.md", ".agents/skills", True, True),
    HostAdapter("devin", "AGENTS.md", ".agents/skills", True, True),
    HostAdapter("copilot", "AGENTS.md", ".github/skills", False, False),
)


def list_hosts() -> list[dict[str, object]]:
    return [host.to_dict() for host in HOSTS]
