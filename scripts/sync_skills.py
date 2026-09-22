"""Mirror canonical API Forge skills into host-native project directories."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

MIRRORS = (Path(".claude/skills"), Path(".github/skills"), Path(".devin/skills"))


def sync(root: Path) -> dict[str, list[str]]:
    source = root / ".agents/skills"
    if not source.is_dir():
        raise SystemExit(f"canonical skill directory not found: {source}")

    result = {"written": [], "removed": []}
    names = {item.name for item in source.iterdir() if item.is_dir()}
    for mirror_rel in MIRRORS:
        mirror = root / mirror_rel
        mirror.mkdir(parents=True, exist_ok=True)
        for existing in mirror.iterdir():
            if existing.is_dir() and existing.name not in names:
                shutil.rmtree(existing)
                result["removed"].append(str(existing.relative_to(root)))
        for name in sorted(names):
            destination = mirror / name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source / name, destination)
            result["written"].append(str(destination.relative_to(root)))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    result = sync(args.root.resolve())
    print(f"written={len(result['written'])} removed={len(result['removed'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
