"""Host-neutral adapters for Claude, GPT/Codex, Devin and Copilot."""

from __future__ import annotations

from dataclasses import dataclass

from apiforge.contracts.base import ContractError
from apiforge.host_assets.loader import load_asset


@dataclass(frozen=True)
class HostAdapter:
    name: str
    instruction_file: str
    skill_directory: str
    supports_subagents: bool
    supports_mcp: bool

    @property
    def asset_source(self) -> str:
        return "package:apiforge.host_assets"

    @property
    def asset_sha256(self) -> str | None:
        template = "CLAUDE.md.tmpl" if self.name == "claude" else "AGENTS.md.tmpl"
        try:
            return load_asset(f"templates/{template}")[1]
        except (ContractError, OSError):
            return None

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "instruction_file": self.instruction_file,
            "skill_directory": self.skill_directory,
            "supports_subagents": self.supports_subagents,
            "supports_mcp": self.supports_mcp,
            "asset_source": self.asset_source,
            "asset_sha256": self.asset_sha256,
        }


HOSTS = (
    HostAdapter("claude", "CLAUDE.md", ".claude/skills", True, True),
    HostAdapter("gpt-codex", "AGENTS.md", ".agents/skills", True, True),
    HostAdapter("devin", "AGENTS.md", ".agents/skills", True, True),
    HostAdapter("copilot", "AGENTS.md", ".github/skills", False, False),
)


def list_hosts() -> list[dict[str, object]]:
    return [host.to_dict() for host in HOSTS]
