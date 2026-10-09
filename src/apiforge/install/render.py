"""Project-scope asset rendering: canonical ``agents/`` + ``.agents/skills/``
into the host directories a consumer repository reads.

Fonte canonica: ``agents/*.md`` (frontmatter completo) e ``.agents/skills/``
(espelho canonico — ``scripts/sync_skills.py`` copia dela). Quando o checkout
nao existe, o pacote carrega as mesmas arvores em
``apiforge/host_assets/{agents,skills}`` via wheel ``force-include``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.core.yaml import load_yaml_strict
from apiforge.distribution.assets import package_root

HOSTS: tuple[str, ...] = ("claude", "devin", "codex", "copilot")

_CLAUDE_TOOLS = "Read, Grep, Glob, Bash, Edit, Write"
_COPILOT_TOOLS = (
    "read", "search", "edit", "shell", "web", "agent"
)


def _repo_root() -> Path | None:
    """O checkout que contem ``agents/`` e ``.agents/skills/``, ou None."""
    base = package_root()
    for cand in (base, *base.parents):
        if (cand / "agents").is_dir() and (cand / ".agents" / "skills").is_dir():
            return cand
    return None


def content_dirs() -> tuple[Path, Path] | None:
    """``(agents_dir, skills_dir)`` canonicos, ou None se indisponiveis."""
    repo = _repo_root()
    if repo is not None:
        return repo / "agents", repo / ".agents" / "skills"
    bundled_agents = package_root() / "host_assets" / "agents"
    bundled_skills = package_root() / "host_assets" / "skills"
    if bundled_agents.is_dir() and bundled_skills.is_dir():
        return bundled_agents, bundled_skills
    return None


def _frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """``(meta, corpo)`` de um agente canonico; corpo preservado byte a byte."""
    if not text.startswith("---"):
        return {}, text
    _, _, rest = text.partition("---")
    head, sep, body = rest.partition("\n---")
    if not sep:
        return {}, text
    meta = load_yaml_strict(head, source="agent-frontmatter")
    return (meta if isinstance(meta, dict) else {}), body.lstrip("\n")


def _emit_agent(meta: dict[str, Any], body: str, host: str) -> str:
    """Render por host — o mesmo shape dos espelhos do repo."""
    name = str(meta.get("name", ""))
    description = str(meta.get("description", "")).replace("\n", " ").strip()
    while "  " in description:
        description = description.replace("  ", " ")
    if host == "claude":
        head = (
            f"name: {name}\n"
            f"description: '{description}'\n"
            f"tools: {_CLAUDE_TOOLS}\n"
            f"model: opus\n"
        )
    elif host == "copilot":
        head = f"name: {name}\ndescription: '{description}'\ntools: {_COPILOT_TOOLS}\n"
    else:
        head = f"name: {name}\ndescription: '{description}'\n"
    return f"---\n{head}---\n\n{body}"


def _agent_filename(name: str, host: str) -> str:
    if host == "copilot":
        return f"{name}.agent.md"
    return f"{name}.md"


def _agent_dir(host: str) -> str:
    return {
        "claude": ".claude/agents",
        "devin": ".devin/agents",
        "copilot": ".github/agents",
        "codex": ".agents/agents",
    }[host]


def _skill_dir(host: str) -> str:
    return {
        "claude": ".claude/skills",
        "devin": ".devin/skills",
        "copilot": ".github/skills",
        "codex": ".agents/skills",
    }[host]


def _walk_files(root: Path) -> list[tuple[str, bytes]]:
    out: list[tuple[str, bytes]] = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            out.append((path.relative_to(root).as_posix(), path.read_bytes()))
    return out


def render(hosts: tuple[str, ...], *, skills: bool, agents: bool) -> dict[str, bytes]:
    """``{rel_path: bytes}`` para os hosts pedidos no escopo de projeto.

    `.agents/agents` + `.agents/skills` sao a superficie compartilhada que
    Devin le nativamente e que Codex/Copilot tambem aceitam: geradas uma
    unica vez a partir da fonte canonica, nunca por merge de espelhos."""
    dirs = content_dirs()
    if dirs is None:
        return {}
    agents_src, skills_src = dirs
    out: dict[str, bytes] = {}

    if agents:
        agent_files = sorted(agents_src.glob("*.md"))
        for path in agent_files:
            meta, body = _frontmatter(path.read_text(encoding="utf-8"))
            name = str(meta.get("name") or path.stem)
            for host in hosts:
                if host not in HOSTS:
                    continue
                rel = f"{_agent_dir(host)}/{_agent_filename(name, host)}"
                out[rel] = _emit_agent(meta, body, host).encode("utf-8")
        # superficie compartilhada (devin nativo; codex/copilot tambem leem)
        if any(h in hosts for h in ("devin", "codex", "copilot")):
            for path in agent_files:
                meta, body = _frontmatter(path.read_text(encoding="utf-8"))
                name = str(meta.get("name") or path.stem)
                out[f".agents/agents/{name}.md"] = _emit_agent(
                    meta, body, "devin").encode("utf-8")

    if skills:
        seen: set[str] = set()
        for host in hosts:
            if host not in HOSTS:
                continue
            dest = _skill_dir(host)
            for rel, data in _walk_files(skills_src):
                key = f"{dest}/{rel}"
                if key not in seen:
                    out[key] = data
                    seen.add(key)
        if any(h in hosts for h in ("devin", "codex", "copilot")):
            for rel, data in _walk_files(skills_src):
                key = f".agents/skills/{rel}"
                out.setdefault(key, data)
    return out


__all__ = ["HOSTS", "content_dirs", "render"]
