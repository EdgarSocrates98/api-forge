"""Stable prompt prefix (§81–83): the static part never changes between runs.

The prefix is the canonical JSON of the protocol digest, the capability, its
output contract and the expertise pack versions — no timestamps, run ids or
paths — so provider-side prompt caching can reuse it. Everything
run-specific (capsule id, refs, task) goes in the suffix.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from functools import lru_cache
from pathlib import Path

from apiforge.contracts.economy_extras import PromptEnvelope

OUTPUT_CONTRACT = "AgentArtifact/v1"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


@lru_cache(maxsize=8)
def protocol_digest(root: str) -> str:
    path = Path(root) / "AGENT_PROTOCOL.md"
    if not path.is_file():
        return "unavailable"
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


@lru_cache(maxsize=4)
def _pack_versions() -> dict[str, int]:
    try:
        from apiforge.knowledge.loader import load_packs
        from apiforge.knowledge.selector import default_root

        return {name: pack.version for name, pack in load_packs(default_root()).items()}
    except Exception:  # noqa: BLE001 - versions are best effort; unknown packs stay named
        return {}


def prefix_for(root: Path, capability: str, expertise: Iterable[str] = ()) -> str:
    versions = _pack_versions()
    return _canonical(
        {
            "protocol": protocol_digest(str(Path(root).resolve())),
            "capability": capability,
            "output_contract": OUTPUT_CONTRACT,
            "expertise": sorted(
                f"{name}@{versions.get(name, 'unknown')}" for name in set(expertise)
            ),
        }
    )


def envelope(
    root: Path,
    capability: str,
    *,
    task: str = "",
    expertise: Iterable[str] = (),
    capsule_id: str | None = None,
    refs: Iterable[str] = (),
) -> PromptEnvelope:
    prefix = prefix_for(root, capability, expertise)
    suffix = _canonical({"capsule": capsule_id, "refs": list(refs), "task": task})
    return PromptEnvelope(
        capability=capability,
        prefix=prefix,
        prefix_sha256=hashlib.sha256(prefix.encode("utf-8")).hexdigest(),
        suffix=suffix,
        prefix_bytes=len(prefix.encode("utf-8")),
        suffix_bytes=len(suffix.encode("utf-8")),
    )


__all__ = ["OUTPUT_CONTRACT", "envelope", "prefix_for", "protocol_digest"]
