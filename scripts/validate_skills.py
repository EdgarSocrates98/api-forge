"""Validate API Forge Agent Skills metadata and optional host mirrors."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MIRRORS = (Path(".claude/skills"), Path(".github/skills"), Path(".devin/skills"))


def parse_frontmatter(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    marker = text.find("\n---\n", 4)
    if marker < 0:
        raise ValueError("unterminated YAML frontmatter")
    data = yaml.safe_load(text[4:marker]) or {}
    if not isinstance(data, dict):
        raise TypeError("frontmatter must be a mapping")
    return data, text[marker + 5 :]


def validate(root: Path, check_mirrors: bool) -> list[str]:
    errors: list[str] = []
    source = root / ".agents/skills"
    skills = sorted(source.glob("*/SKILL.md"))
    if not skills:
        errors.append("no canonical skills found")
    for skill_file in skills:
        folder = skill_file.parent.name
        try:
            data, body = parse_frontmatter(skill_file)
            name = data.get("name")
            description = data.get("description")
            if name != folder or not isinstance(name, str) or not NAME_RE.fullmatch(name):
                errors.append(f"{skill_file}: invalid name")
            if (
                not isinstance(description, str)
                or not description.strip()
                or len(description) > 1024
            ):
                errors.append(f"{skill_file}: invalid description")
            if len(body.splitlines()) > 500:
                errors.append(f"{skill_file}: body exceeds 500 lines")
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{skill_file}: {exc}")

    if check_mirrors:
        for mirror_rel in MIRRORS:
            mirror = root / mirror_rel
            for source_file in skills:
                mirrored = mirror / source_file.parent.name / "SKILL.md"
                if not mirrored.exists() or mirrored.read_bytes() != source_file.read_bytes():
                    errors.append(f"mirror drift: {mirrored}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check-mirrors", action="store_true")
    args = parser.parse_args()
    errors = validate(args.root.resolve(), args.check_mirrors)
    if errors:
        print("\n".join(errors))
        return 1
    print("skills: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
