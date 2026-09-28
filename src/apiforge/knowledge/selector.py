"""Lazy expertise selection (§26–27): intent → declared triggers → only the named packs.

Selection is deterministic and offline: keywords from the intent, the
frameworks observed in the case and the capability being served each map to
pack domains through ``rules/expertise_triggers.yaml``. Nothing matched means
nothing loaded, reported as ``no-expertise-trigger`` — the selector never
falls back to the whole catalog.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from apiforge.contracts.base import ContractError
from apiforge.contracts.selective import ExpertisePick, ExpertiseSelection
from apiforge.knowledge.loader import Pack, load_packs

TRIGGERS_FILE = Path(__file__).resolve().parents[1] / "rules" / "expertise_triggers.yaml"


class SelectorError(ContractError):
    def __init__(self, code: str, detail: str, *, field: str, unlock: str) -> None:
        super().__init__(code, detail)
        self.field = field
        self.unlock = unlock


def _invalid(detail: str) -> SelectorError:
    return SelectorError(
        "AF-EXPERTISE-TRIGGERS-INVALID",
        detail,
        field="expertise_triggers.yaml",
        unlock="restore rules/expertise_triggers.yaml or name only existing pack domains",
    )


@lru_cache(maxsize=4)
def load_triggers(path: Path = TRIGGERS_FILE) -> dict[str, Any]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise _invalid(f"{path}: {exc}") from exc
    if not isinstance(raw, dict) or raw.get("schema") != "apiforge/expertise-triggers/v1":
        raise _invalid(f"{path}: expected schema apiforge/expertise-triggers/v1")
    keywords = []
    for row in raw.get("keywords") or []:
        if not isinstance(row, dict) or not row.get("id") or not row.get("packs"):
            raise _invalid(f"{path}: every keyword trigger needs id, match and packs")
        keywords.append(
            {
                "id": str(row["id"]),
                "match": tuple(str(item).lower() for item in row.get("match") or ()),
                "packs": tuple(str(item) for item in row["packs"]),
            }
        )
    return {
        "keywords": tuple(keywords),
        "frameworks": {
            str(k): tuple(str(i) for i in v) for k, v in (raw.get("frameworks") or {}).items()
        },
        "capabilities": {
            str(k): tuple(str(i) for i in v) for k, v in (raw.get("capabilities") or {}).items()
        },
    }


def referenced_packs(triggers: dict[str, Any] | None = None) -> set[str]:
    table = triggers or load_triggers()
    names = {pack for row in table["keywords"] for pack in row["packs"]}
    for mapping in (table["frameworks"], table["capabilities"]):
        for packs in mapping.values():
            names.update(packs)
    return names


def default_root(root: Path | None = None) -> Path:
    if root is not None:
        return Path(root)
    local = Path("knowledge")
    if local.is_dir():
        return local
    from apiforge.distribution.assets import package_root

    return package_root() / "knowledge"


@lru_cache(maxsize=8)
def _catalog(root: str) -> tuple[dict[str, Pack], dict[str, int]]:
    packs = load_packs(Path(root))
    sizes = {
        name: sum(item.stat().st_size for item in (Path(root) / name).rglob("*") if item.is_file())
        for name in packs
    }
    return packs, sizes


def _matches(text: str, needle: str) -> bool:
    if needle.startswith(" ") or needle.endswith(" "):
        return needle in f" {text} "
    return re.search(r"(?<![\w])" + re.escape(needle), text) is not None


def select_expertise(
    intent: str,
    *,
    capability: str | None = None,
    frameworks: Iterable[str] = (),
    root: Path | None = None,
) -> ExpertiseSelection:
    table = load_triggers()
    packs, sizes = _catalog(str(default_root(root).resolve()))
    missing = sorted(referenced_packs(table) - set(packs))
    if missing:
        raise _invalid(f"triggers name packs that do not exist: {missing}")
    text = " ".join(intent.lower().split())
    reasons: dict[str, list[str]] = {}
    for row in table["keywords"]:
        hit = next((needle for needle in row["match"] if _matches(text, needle)), None)
        if hit is not None:
            for pack in row["packs"]:
                reasons.setdefault(pack, []).append(f"keyword:{row['id']}:{hit.strip()}")
    framework_list = tuple(sorted({item.lower() for item in frameworks if item}))
    for framework in framework_list:
        for pack in table["frameworks"].get(framework, ()):
            reasons.setdefault(pack, []).append(f"framework:{framework}")
    if capability:
        for pack in table["capabilities"].get(capability, ()):
            reasons.setdefault(pack, []).append(f"capability:{capability}")
    selected = tuple(
        ExpertisePick(
            pack_id=name,
            pack_version=packs[name].version,
            reasons=tuple(sorted(set(why))),
            bytes=sizes[name],
        )
        for name, why in sorted(reasons.items())
    )
    return ExpertiseSelection(
        intent=intent,
        capability=capability,
        frameworks=framework_list,
        selected=selected,
        loaded_bytes=sum(item.bytes for item in selected),
        catalog_bytes=sum(sizes.values()),
        catalog_packs=len(packs),
        unresolved=() if selected else ("no-expertise-trigger",),
    )


__all__ = [
    "TRIGGERS_FILE",
    "SelectorError",
    "default_root",
    "load_triggers",
    "referenced_packs",
    "select_expertise",
]
