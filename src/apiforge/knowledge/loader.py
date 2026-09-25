"""Knowledge packs — `knowledge/<domain>/` directories under a closed schema.

A pack is data, not prose: `pack.yaml` (identity, rule areas, the catalog
rules it backs), `source_authority.yaml` (every normative claim's source,
authority class and verification date — sources are cited, never copied),
optional `matrix.yaml` (runtime version guard) and `evals.yaml` (declared
adversarial probes; the project never calls a model, so evals are data for
external runners). `knowledge check` validates all of it deterministically.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apiforge.contracts.base import ContractError
from apiforge.contracts.evidence import EvidenceLevel
from apiforge.contracts.knowledge import PackFreshness
from apiforge.core.yaml import StrictYamlError, load_yaml_mapping

_AUTHORITIES = frozenset(
    {
        "ietf-rfc",
        "owasp",
        "aws-docs",
        "openapi-spec",
        "w3c",
        "vendor-docs",
        "project-docs",
    }
)
_EVAL_KINDS = frozenset({"rule", "fact-kind", "refusal"})

# The v1 eval vocabulary — closed; anything outside is a named refusal.
EVAL_TYPES = frozenset(
    {
        "unit",
        "golden",
        "integration",
        "adversarial",
        "holdout",
        "regression",
        "economy",
        "security",
        "compatibility",
        "performance",
        "end-to-end",
    }
)
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class KnowledgeError(ContractError):
    pass


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    authority: str
    verified: str


@dataclass(frozen=True)
class Pack:
    domain: str
    version: int
    areas: tuple[str, ...]
    rule_ids: tuple[str, ...]
    summary: str
    sources: tuple[Source, ...]
    verified: str | None
    matrix: tuple[dict[str, Any], ...] = field(default=())
    evals: tuple[dict[str, Any], ...] = field(default=())
    freshness: PackFreshness | None = None
    evidence_level: EvidenceLevel = "unknown"


def _err(code: str, detail: str) -> KnowledgeError:
    return KnowledgeError(code, detail)


def _mapping(data: Any, name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise _err("AF-KNOW-SCHEMA", f"{name}: expected a mapping")
    return data


def _require(data: dict[str, Any], key: str, name: str) -> Any:
    value = data.get(key)
    if value is None or value == "":
        raise _err("AF-KNOW-SCHEMA", f"{name}: missing required field {key!r}")
    return value


def _load_yaml(path: Path, name: str) -> dict[str, Any]:
    if not path.is_file():
        raise _err("AF-KNOW-SCHEMA", f"{name}: file missing in pack")
    try:
        data = load_yaml_mapping(path.read_text(encoding="utf-8"), source=f"{name}")
    except (OSError, StrictYamlError, ValueError) as exc:
        raise _err("AF-KNOW-SCHEMA", f"{name}: unreadable YAML ({exc})") from exc
    return _mapping(data, name)


def _sources(path: Path) -> tuple[Source, ...]:
    if not path.is_file():
        raise _err("AF-KNOW-NO-AUTHORITY", "pack lacks source_authority.yaml")
    data = _load_yaml(path, "source_authority.yaml")
    raw = data.get("sources")
    if not isinstance(raw, list) or not raw:
        raise _err("AF-KNOW-NO-AUTHORITY", "source_authority.yaml lists no sources")
    out: list[Source] = []
    for i, entry in enumerate(raw):
        e = _mapping(entry, f"sources[{i}]")
        authority = str(_require(e, "authority", f"sources[{i}]"))
        if authority not in _AUTHORITIES:
            raise _err(
                "AF-KNOW-AUTHORITY",
                f"sources[{i}].authority {authority!r} not in {sorted(_AUTHORITIES)}",
            )
        verified = str(_require(e, "verified", f"sources[{i}]"))
        if not _DATE.match(verified):
            raise _err(
                "AF-KNOW-SCHEMA",
                f"sources[{i}].verified {verified!r} is not YYYY-MM-DD",
            )
        out.append(
            Source(
                name=str(_require(e, "name", f"sources[{i}]")),
                url=str(_require(e, "url", f"sources[{i}]")),
                authority=authority,
                verified=verified,
            )
        )
    return tuple(out)


def _matrix(path: Path) -> tuple[dict[str, Any], ...]:
    if not path.is_file():
        return ()
    data = _load_yaml(path, "matrix.yaml")
    raw = data.get("constraints")
    if not isinstance(raw, list):
        raise _err("AF-KNOW-SCHEMA", "matrix.yaml: 'constraints' must be a list")
    for i, c in enumerate(raw):
        m = _mapping(c, f"constraints[{i}]")
        _require(m, "component", f"constraints[{i}]")
        if not any(k in m for k in ("min", "max", "range", "set")):
            raise _err(
                "AF-KNOW-SCHEMA",
                f"constraints[{i}] needs one of min/max/range/set",
            )
    return tuple(raw)


def _evals(path: Path) -> tuple[dict[str, Any], ...]:
    if not path.is_file():
        return ()
    data = _load_yaml(path, "evals.yaml")
    raw = data.get("evals")
    if not isinstance(raw, list):
        raise _err("AF-KNOW-SCHEMA", "evals.yaml: 'evals' must be a list")
    for i, e in enumerate(raw):
        m = _mapping(e, f"evals[{i}]")
        _require(m, "id", f"evals[{i}]")
        _require(m, "prompt", f"evals[{i}]")
        etype = str(_require(m, "type", f"evals[{i}]"))
        if etype not in EVAL_TYPES:
            raise _err(
                "AF-KNOW-EVAL-TYPE",
                f"evals[{i}].type {etype!r} not in {sorted(EVAL_TYPES)}",
            )
        expect = _mapping(_require(m, "expect", f"evals[{i}]"), f"evals[{i}].expect")
        kind = str(_require(expect, "kind", f"evals[{i}].expect"))
        if kind not in _EVAL_KINDS:
            raise _err(
                "AF-KNOW-EVAL",
                f"evals[{i}].expect.kind {kind!r} not in {sorted(_EVAL_KINDS)}",
            )
    return tuple(raw)


def load_pack(domain_dir: Path) -> Pack:
    """Load and validate one pack directory against the closed schema."""
    domain_dir = Path(domain_dir)
    data = _load_yaml(domain_dir / "pack.yaml", "pack.yaml")
    domain = str(_require(data, "domain", "pack.yaml"))
    if domain != domain_dir.name:
        raise _err(
            "AF-KNOW-DOMAIN",
            f"pack.yaml domain {domain!r} != directory {domain_dir.name!r}",
        )
    version = _require(data, "version", "pack.yaml")
    if not isinstance(version, int):
        raise _err("AF-KNOW-SCHEMA", "pack.yaml: version must be an integer")
    areas = data.get("areas", [])
    rule_ids = data.get("rule_ids", [])
    if not isinstance(areas, list) or not isinstance(rule_ids, list):
        raise _err("AF-KNOW-SCHEMA", "pack.yaml: areas/rule_ids must be lists")
    verified = data.get("verified")
    if verified is not None and not _DATE.match(str(verified)):
        raise _err("AF-KNOW-SCHEMA", "pack.yaml: verified must be YYYY-MM-DD")
    freshness_raw = data.get("freshness")
    freshness: PackFreshness | None = None
    if freshness_raw is not None:
        if not isinstance(freshness_raw, dict):
            raise _err("AF-KNOW-SCHEMA", "pack.yaml: freshness must be a mapping")
        try:
            freshness = PackFreshness.model_validate(freshness_raw)
        except ValueError as exc:
            raise _err("AF-KNOW-SCHEMA", f"pack.yaml: invalid freshness ({exc})") from exc
    evidence_level = str(data.get("evidence_level", "unknown"))
    if evidence_level not in {
        "observed",
        "declared",
        "inferred",
        "heuristic",
        "verified",
        "unknown",
    }:
        raise _err("AF-KNOW-SCHEMA", "pack.yaml: invalid evidence_level")
    return Pack(
        domain=domain,
        version=version,
        areas=tuple(str(a) for a in areas),
        rule_ids=tuple(str(r) for r in rule_ids),
        summary=str(data.get("summary", "")),
        sources=_sources(domain_dir / "source_authority.yaml"),
        verified=str(verified) if verified is not None else None,
        matrix=_matrix(domain_dir / "matrix.yaml"),
        evals=_evals(domain_dir / "evals.yaml"),
        freshness=freshness,
        evidence_level=evidence_level,  # type: ignore[arg-type]
    )


def load_packs(root: Path) -> dict[str, Pack]:
    """Every subdirectory of ``root`` is a pack; all must validate."""
    root = Path(root)
    if not root.is_dir():
        raise _err("AF-KNOW-ROOT", f"knowledge root {root} is not a directory")
    packs: dict[str, Pack] = {}
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith(("_", ".")):
            packs[child.name] = load_pack(child)
    return packs


def load_packaged_packs() -> dict[str, Pack]:
    """Load packaged knowledge when available, without consulting the cwd."""

    from apiforge.distribution.assets import package_root

    packaged = package_root() / "knowledge"
    if packaged.is_dir():
        return load_packs(packaged)
    raise _err("AF-KNOW-PACKAGED-MISSING", f"installed package has no knowledge assets: {packaged}")


_REQUIRED_DOCS = (
    "index.md",
    "quick-reference.md",
    "concepts.md",
    "patterns.md",
    "anti-patterns.md",
    "recipes.md",
    "troubleshooting.md",
    "evals.yaml",
)


def check_packs(root: Path) -> dict[str, Any]:
    """Validate all packs and cross-check rule ids against the catalog."""
    from apiforge.rules.catalog import load_areas, load_catalog

    packs = load_packs(root)
    catalog = load_catalog()
    areas = set(load_areas())
    problems: list[str] = []
    for name, pack in packs.items():
        for area in pack.areas:
            if area not in areas:
                problems.append(f"{name}: unknown rule area {area!r}")
        for rid in pack.rule_ids:
            if rid not in catalog:
                problems.append(f"{name}: rule_id {rid} not in catalog")
        pack_dir = root / name
        for doc in _REQUIRED_DOCS:
            if not (pack_dir / doc).is_file():
                problems.append(f"{name}: required doc {doc} missing")
        if pack.rule_ids and not pack.evals:
            problems.append(f"{name}: has rules but evals.yaml declares no probes")
    return {
        "packs": sorted(packs),
        "count": len(packs),
        "problems": problems,
        "ok": not problems,
    }
