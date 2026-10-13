"""Layer policies loaded from ``rules/cache_policies.yaml``."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml

from apiforge.cache.errors import CacheError
from apiforge.contracts.cache import CACHE_LAYERS

POLICY_FILE = Path(__file__).resolve().parents[1] / "rules" / "cache_policies.yaml"


@dataclass(frozen=True)
class LayerPolicy:
    layer: str
    enabled: bool
    ttl_seconds: int
    on_stale: Literal["warn", "recompute"]
    shared: bool


def _invalid(detail: str) -> CacheError:
    return CacheError(
        "AF-CACHE-POLICY-INVALID",
        detail,
        field="cache_policies.yaml",
        unlock="restore rules/cache_policies.yaml to the shipped schema",
    )


@lru_cache(maxsize=4)
def load_policies(path: Path = POLICY_FILE) -> dict[str, LayerPolicy]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise _invalid(f"{path}: {exc}") from exc
    layers = raw.get("layers") if isinstance(raw, dict) else None
    if raw.get("schema") != "apiforge/cache-policies/v1" or not isinstance(layers, dict):
        raise _invalid(f"{path}: expected schema apiforge/cache-policies/v1 with layers")
    if set(layers) != set(CACHE_LAYERS):
        raise _invalid(f"{path}: layers must be exactly {list(CACHE_LAYERS)}")
    policies: dict[str, LayerPolicy] = {}
    for name in CACHE_LAYERS:
        row = layers[name] or {}
        on_stale = row.get("on_stale")
        ttl = row.get("ttl_seconds")
        if on_stale not in {"warn", "recompute"} or not isinstance(ttl, int) or ttl < 0:
            raise _invalid(f"{path}: layer {name} needs on_stale warn|recompute and ttl >= 0")
        policies[name] = LayerPolicy(
            layer=name,
            enabled=bool(row.get("enabled")),
            ttl_seconds=ttl,
            on_stale=on_stale,
            shared=bool(row.get("shared")),
        )
    return policies


def policy_for(layer: str) -> LayerPolicy:
    if layer not in CACHE_LAYERS:
        raise CacheError(
            "AF-CACHE-LAYER-UNKNOWN",
            f"{layer!r} is not a cache layer",
            field="layer",
            unlock=f"use one of {', '.join(CACHE_LAYERS)}",
        )
    policy = load_policies()[layer]
    if not policy.enabled:
        raise CacheError(
            "AF-CACHE-LAYER-DISABLED",
            f"cache layer {layer} is declared but disabled in cache_policies.yaml",
            field="layer",
            unlock="use an enabled layer (parse|graph|impact|capsule) or enable it with a caller",
        )
    return policy


def policy_sha() -> str:
    return hashlib.sha256(POLICY_FILE.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


__all__ = ["POLICY_FILE", "LayerPolicy", "load_policies", "policy_for", "policy_sha"]
