"""Deterministic per-host rendering of coordinators from ``agents/*.md``.

Claude Code reads ``.claude/agents/*.md``, Devin reads ``.agents/agents/*.md``
and Codex reads ``.codex/agents/*.toml``. A declared ``access`` projects to
Claude ``tools`` and Codex ``sandbox_mode``; ``model_tier`` projects to Claude
``model`` and Codex ``model_reasoning_effort``. Legacy sources (no ``access``)
keep verbatim markdown mirrors so the roster can migrate incrementally.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from apiforge.contracts.agents import AgentSource
from apiforge.dispatch.agent_source import load_roster

CLAUDE_DIR = ".claude/agents"
DEVIN_DIR = ".agents/agents"
CODEX_DIR = ".codex/agents"
MIRROR_DIRS: tuple[str, ...] = (DEVIN_DIR, CLAUDE_DIR, CODEX_DIR)

CLAUDE_TOOLS = {
    "read-only": "Read, Grep, Glob, Bash",
    "state-writer": "Read, Grep, Glob, Bash",
    "writer": "Read, Grep, Glob, Bash, Edit, Write",
}
CLAUDE_MODEL = {"fast": "sonnet", "deep": "opus"}
CODEX_SANDBOX = {
    "read-only": "read-only",
    "state-writer": "workspace-write",
    "writer": "workspace-write",
}
CODEX_EFFORT = {"fast": "medium", "deep": "high"}


def _frontmatter(fields: dict[str, str]) -> str:
    dumped = yaml.safe_dump(fields, sort_keys=False, allow_unicode=True, width=10_000)
    return f"---\n{dumped}---\n"


def _markdown(agent: AgentSource, fields: dict[str, str]) -> bytes:
    return f"{_frontmatter(fields)}\n{agent.body}\n".encode()


def render_claude(agent: AgentSource) -> bytes:
    if agent.legacy:
        return agent.raw.encode("utf-8")
    assert agent.access is not None
    fields = {
        "name": agent.name,
        "description": agent.description,
        "tools": CLAUDE_TOOLS[agent.access],
    }
    if agent.model_tier:
        fields["model"] = CLAUDE_MODEL[agent.model_tier]
    return _markdown(agent, fields)


def render_devin(agent: AgentSource) -> bytes:
    if agent.legacy:
        return agent.raw.encode("utf-8")
    return _markdown(agent, {"name": agent.name, "description": agent.description})


def _basic(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _multiline(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')
    return f'"""\n{escaped}\n"""'


def render_codex(agent: AgentSource) -> bytes:
    lines = [f"name = {_basic(agent.name)}", f"description = {_basic(agent.description)}"]
    if not agent.legacy:
        assert agent.access is not None
        lines.append(f'sandbox_mode = "{CODEX_SANDBOX[agent.access]}"')
        if agent.model_tier:
            lines.append(f'model_reasoning_effort = "{CODEX_EFFORT[agent.model_tier]}"')
    lines.append(f"developer_instructions = {_multiline(agent.body)}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def render_agent(agent: AgentSource) -> dict[str, bytes]:
    return {
        f"{DEVIN_DIR}/{agent.stem}.md": render_devin(agent),
        f"{CLAUDE_DIR}/{agent.stem}.md": render_claude(agent),
        f"{CODEX_DIR}/{agent.stem}.toml": render_codex(agent),
    }


def render_all(root: Path) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    for agent in load_roster(Path(root)):
        rendered.update(render_agent(agent))
    return dict(sorted(rendered.items()))


__all__ = [
    "CLAUDE_DIR",
    "CODEX_DIR",
    "DEVIN_DIR",
    "MIRROR_DIRS",
    "render_agent",
    "render_all",
    "render_claude",
    "render_codex",
    "render_devin",
]
