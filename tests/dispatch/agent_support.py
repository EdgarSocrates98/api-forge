from pathlib import Path

from apiforge.contracts.agents import REQUIRED_SECTIONS

FILLER = (
    "Cite the evidence path and line for every claim, prefer unresolved over guessing, "
    "and hand the result to the independent verifier before anyone calls the work done. "
)


def body(words_per_section: int = 32) -> str:
    parts = ["Follow `AGENT_PROTOCOL.md`."]
    for title in REQUIRED_SECTIONS:
        sentence = FILLER * (words_per_section // len(FILLER.split()) + 1)
        text = " ".join(sentence.split()[:words_per_section])
        parts.append(f"## {title}\n\n{text}")
    return "\n\n".join(parts)


def write_agent(
    root: Path,
    name: str,
    *,
    access: str | None = "read-only",
    write_scope: str | None = None,
    model_tier: str | None = "deep",
    tools: tuple[str, ...] = ("contract show",),
    description: str | None = None,
    text: str | None = None,
) -> Path:
    folder = root / "agents"
    folder.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        f"name: {name}",
        "description: "
        + (
            description
            or "Use when an OpenAPI contract needs review before code serves it. "
            "Not for published breaking changes (-> api-governance-reviewer)."
        ),
    ]
    if access:
        lines.append(f"access: {access}")
    if write_scope:
        lines.append(f"write_scope: {write_scope}")
    if model_tier:
        lines.append(f"model_tier: {model_tier}")
    lines.append("rule_areas: [CONTRACT]")
    lines.append("executors: [af-inventory, af-judge]")
    lines.append(f"apiforge_tools: [{', '.join(tools)}]")
    lines.append("---")
    path = folder / f"{name}.md"
    path.write_text("\n".join(lines) + "\n\n" + (text or body()) + "\n", encoding="utf-8")
    return path
