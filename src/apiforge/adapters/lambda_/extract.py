"""Lambda dump extractor: offline dump directory -> CodeInventory.

Reads what `collect lambda` wrote — never AWS. Env var **names** are
extracted; values are never read. Missing/malformed files are named
diagnostics, and an absent `policy.json` is data (no resource policy),
not a defect.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef

_DUMP_FILES = ("function.json", "policy.json")


def _diag(code: str, message: str, rel: str, digest: str | None) -> Diagnostic:
    source = (
        SourceRef(path=rel, sha256=digest, line=None, extractor="lambda-dump")
        if digest is not None
        else None
    )
    return Diagnostic(code=code, status=FindingStatus.UNRESOLVED, message=message, source=source)


def _load(
    dump: Path, name: str, input_hashes: dict[str, str], diagnostics: list[Diagnostic]
) -> Any | None:
    path = dump / name
    if not path.is_file():
        return None
    raw = path.read_bytes()
    input_hashes[name] = hashlib.sha256(raw).hexdigest()
    try:
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        diagnostics.append(
            _diag(
                "AF-LAM-DUMP-INVALID", f"{name}: not valid JSON ({exc})", name, input_hashes[name]
            )
        )
        return None


def _fact(
    kind: str, source_file: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]
) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": source_file, **measures}),
        kind=kind,
        source=SourceRef(path=source_file, sha256=digest, line=None, extractor="lambda-dump"),
        measures=measures,
        attrs=attrs,
    )


def extract_lambda(dump_dir: Path) -> CodeInventory:
    """Read a `collect lambda` dump directory into facts, offline."""
    dump = Path(dump_dir)
    diagnostics: list[Diagnostic] = []
    input_hashes: dict[str, str] = {}
    facts: list[Fact] = []

    function_path = dump / "function.json"
    if not function_path.is_file():
        diagnostics.append(
            _diag(
                "AF-LAM-DUMP-MISSING",
                f"function.json: dump file missing from {dump}",
                "function.json",
                None,
            )
        )

    for name in _DUMP_FILES:
        loaded = _load(dump, name, input_hashes, diagnostics)
        digest = input_hashes.get(name, "")
        if name == "function.json" and isinstance(loaded, dict):
            env = loaded.get("Environment")
            variables = env.get("Variables", {}) if isinstance(env, dict) else {}
            facts.append(
                _fact(
                    "aws.lambda.function",
                    name,
                    digest,
                    {"function_name": loaded.get("FunctionName", "")},
                    {
                        "runtime": loaded.get("Runtime"),
                        "memory_mb": loaded.get("MemorySize"),
                        "timeout_s": loaded.get("Timeout"),
                        "handler": loaded.get("Handler"),
                        "package_type": loaded.get("PackageType"),
                        "layers": len(loaded.get("Layers") or []),
                        "env_keys": sorted(variables.keys()) if isinstance(variables, dict) else [],
                        "tracing_mode": (loaded.get("TracingConfig") or {}).get("Mode"),
                        "reserved_concurrency": loaded.get("ReservedConcurrentExecutions"),
                    },
                )
            )
        elif name == "policy.json" and loaded is not None:
            facts.append(
                _fact(
                    "aws.lambda.policy",
                    name,
                    digest,
                    {"function_name": ""},
                    {"has_resource_policy": True},
                )
            )

    return CodeInventory(
        framework="lambda-dump",
        root=str(dump),
        facts=tuple(facts),
        diagnostics=tuple(diagnostics),
        input_hashes=input_hashes,
    )
