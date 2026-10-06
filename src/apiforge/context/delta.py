"""Delta-first context (§22): what changed → what it impacts → which capsules to build.

The change set comes from read-only ``git diff --name-status`` (argument
arrays, never a shell) or from an explicit ``--changed`` list, so the verb
also works hostless. Files are mapped to graph fact nodes and then to the
operations implemented by them; contract edits are classified by comparing
each operation subtree plus every component it reaches through ``$ref``; cached capsule selections whose dependencies hold
a changed file add their target. Nothing is guessed: files that map to no
node are reported as ``unmapped:<path>``.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

from apiforge.cache.errors import CacheError
from apiforge.cache.store import CacheStore
from apiforge.contracts.cache import ChangedFile, DeltaSlice
from apiforge.security.source_paths import (
    AllowedRoots,
    SourcePathError,
    confine_dir,
    resolve_allowed_source,
)

_STATUS = re.compile(r"^([ACDMRTUX])\d*$")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CacheError(
            "AF-DELTA-GIT-UNAVAILABLE",
            f"git could not run under {root}: {exc}",
            field="root",
            unlock="install git or pass --changed <file> ... instead of --base/--head",
        ) from exc


def git_changes(root: Path, base: str, head: str | None) -> list[ChangedFile]:
    inside = _git(root, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        raise CacheError(
            "AF-DELTA-GIT-UNAVAILABLE",
            f"{root} is not inside a git work tree",
            field="root",
            unlock="run inside a git repository or pass --changed <file> ...",
        )
    prefix = _git(root, "rev-parse", "--show-prefix").stdout.strip()
    args = ["diff", "--name-status", "--no-renames", base]
    if head:
        args.append(head)
    result = _git(root, *args, "--", ".")
    if result.returncode != 0:
        raise CacheError(
            "AF-DELTA-REF-INVALID",
            result.stderr.strip() or f"git diff {base} {head or ''} failed",
            field="base" if head is None else "base/head",
            unlock="pass commits or refs that exist in this repository (git rev-parse <ref>)",
        )
    changes: list[ChangedFile] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        match = _STATUS.match(parts[0])
        path = parts[-1]
        if prefix and path.startswith(prefix):
            path = path[len(prefix) :]
        changes.append(ChangedFile(path=path, status=match.group(1) if match else "M"))  # type: ignore[arg-type]
    return sorted(changes, key=lambda item: item.path)


def build_delta(
    root: Path,
    *,
    base: str | None = None,
    head: str | None = None,
    changed: Sequence[str] = (),
    case_dir: Path | None = None,
    invalidate: bool = False,
    cache_home: Path | None = None,
) -> DeltaSlice:
    root = Path(root).resolve()
    refused: list[str] = []
    if changed:
        normalized = {_normalize(root, item, refused) for item in changed}
        files = sorted(
            {ChangedFile(path=path) for path in normalized if path is not None},
            key=lambda item: item.path,
        )
        source = "explicit"
    elif base:
        files = git_changes(root, base, head)
        source = "git"
    else:
        raise CacheError(
            "AF-DELTA-INPUT-MISSING",
            "a delta needs --base [--head] or at least one --changed path",
            field="base",
            unlock="pass --base <ref> [--head <ref>] or --changed <file> ...",
        )
    paths = {item.path for item in files if not item.path.startswith(".apiforge/")}
    case_path = confine_dir(root, case_dir) if case_dir else root / ".apiforge" / "case"
    store = CacheStore(root, home=cache_home)
    impacted: set[str] = set()
    changed_nodes: set[str] = set()
    mapped: set[str] = set()
    # A refused --changed path is never read; its impact cannot be judged, so it blocks.
    unresolved: list[str] = list(refused)

    from apiforge.context.gateway.levels import load_graph, verified_case

    case = verified_case(case_path)
    if case is None:
        unresolved.append("graph-unavailable")
    else:
        inputs = case.get("inputs") or {}
        project_rel = _rel(root / str(inputs.get("project", "")), root)
        contract_rel = _rel(root / str(inputs.get("contract", "")), root)
        nodes, edges, _ = load_graph(root, case_path)
        facts_by_file: dict[str, set[str]] = {}
        for node in nodes:
            if node.kind.value != "fact":
                continue
            source_path = str(node.props.get("path") or "")
            if not source_path:
                continue
            rel = _join(project_rel, source_path)
            facts_by_file.setdefault(rel, set()).add(node.id)
        implemented: dict[str, set[str]] = {}
        for edge in edges:
            if edge.kind.value == "implemented_by":
                implemented.setdefault(edge.to_id, set()).add(edge.from_id)
        for path in sorted(paths):
            for fact_id in facts_by_file.get(path, ()):
                changed_nodes.add(fact_id)
                mapped.add(path)
                for operation in implemented.get(fact_id, ()):
                    impacted.add(operation.removeprefix("operation:"))
        if contract_rel in paths:
            mapped.add(contract_rel)
            operations = _contract_changes(root, contract_rel, base, head, source)
            if operations is None:
                unresolved.append(f"contract-diff-unavailable:{contract_rel}")
                operations = {
                    node.id.removeprefix("operation:")
                    for node in nodes
                    if node.kind.value == "operation"
                }
            impacted |= operations
    for _, _, entry in store.entries(("capsule",)):
        if entry is None:
            continue
        hits = paths & {dep.path for dep in entry.deps_files}
        if not hits:
            hits = {path for path in paths if _mentions(root / path, entry.symbols)}
        if hits:
            mapped |= hits
            impacted.add(entry.subject)
    unresolved.extend(f"unmapped:{path}" for path in sorted(paths - mapped))
    invalidated = (
        tuple(store.invalidate(files=paths, nodes=changed_nodes, layers=("capsule",)))
        if invalidate
        else ()
    )
    runtime_unmapped = [path for path in sorted(paths - mapped) if _runtime_path(path)]
    unresolved.extend(f"{UNMAPPED_SOURCE}:{path}" for path in runtime_unmapped)
    blocking = [
        item
        for item in unresolved
        if not item.startswith("unmapped:") and not item.startswith(UNMAPPED_SOURCE)
    ]
    return DeltaSlice(
        source=source,  # type: ignore[arg-type]
        base=base,
        head=head,
        changed_files=tuple(files),
        changed_nodes=tuple(sorted(changed_nodes)),
        impacted_operations=tuple(sorted(impacted)),
        capsule_targets=tuple(sorted(impacted)),
        invalidated=invalidated,
        unresolved=tuple(sorted(set(unresolved))),
        status="unresolved" if blocking else "degraded" if runtime_unmapped else "ready",
    )


UNMAPPED_SOURCE = "AF-DELTA-UNMAPPED-SOURCE"
_RUNTIME_SUFFIXES = {
    ".py",
    ".java",
    ".kt",
    ".go",
    ".ts",
    ".js",
    ".cs",
    ".rb",
    ".yaml",
    ".yml",
    ".json",
    ".proto",
    ".sql",
    ".graphql",
    ".tf",
}


def _runtime_path(path: str) -> bool:
    """Source, config or contract files: "no mapping" must not read as "no impact"."""
    posix = path.replace("\\", "/").lower()
    if posix.startswith(("docs/", "doc/")) or "/docs/" in posix:
        return False
    return Path(posix).suffix in _RUNTIME_SUFFIXES


def _contract_changes(
    root: Path, contract_rel: str, base: str | None, head: str | None, source: str
) -> set[str] | None:
    """Operations touched by a contract edit, or None when the old version is unavailable."""
    if source != "git" or not base:
        return None
    old = _git(root, "show", f"{base}:./{contract_rel}")
    if old.returncode != 0:
        return None
    if head:
        new = _git(root, "show", f"{head}:./{contract_rel}")
        if new.returncode != 0:
            return None
        new_text = new.stdout
    else:
        try:
            new_text = (root / contract_rel).read_text(encoding="utf-8")
        except OSError:
            return None
    try:
        before = yaml.safe_load(old.stdout) or {}
        after = yaml.safe_load(new_text) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(before, Mapping) or not isinstance(after, Mapping):
        return None
    old_ops, new_ops = _operations(before), _operations(after)
    changed: set[str] = set()
    for key in sorted(old_ops.keys() | new_ops.keys()):
        if _closure(before, old_ops.get(key)) != _closure(after, new_ops.get(key)):
            changed.add(key)
    return changed


_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


def _operations(document: Mapping[str, Any]) -> dict[str, Any]:
    found: dict[str, Any] = {}
    for path, item in (document.get("paths") or {}).items():
        if not isinstance(item, Mapping):
            continue
        shared = {k: v for k, v in item.items() if k not in _METHODS}
        for method in _METHODS:
            if method in item:
                found[f"{method.upper()} {path}"] = {"operation": item[method], "shared": shared}
    return found


def _closure(document: Mapping[str, Any], operation: Any) -> str:
    """Canonical text of an operation plus every component it reaches through $ref."""
    if operation is None:
        return ""
    components = document.get("components") or {}
    seen: dict[str, Any] = {}
    pending = sorted(_refs(operation))
    while pending:
        ref = pending.pop(0)
        if ref in seen:
            continue
        section, _, name = ref.removeprefix("#/components/").partition("/")
        value = (components.get(section) or {}).get(name)
        seen[ref] = value
        pending.extend(sorted(_refs(value) - set(seen)))
    return json.dumps({"op": operation, "refs": seen}, sort_keys=True, default=str)


def _refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        ref = value.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/"):
            refs.add(ref)
        for item in value.values():
            refs |= _refs(item)
    elif isinstance(value, list):
        for item in value:
            refs |= _refs(item)
    return refs


def _mentions(path: Path, symbols: Iterable[str]) -> bool:
    wanted = [symbol for symbol in symbols if symbol]
    if not wanted:
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    pattern = re.compile("|".join(rf"(?<![\w]){re.escape(item)}(?![\w])" for item in wanted))
    return bool(pattern.search(text))


def _normalize(root: Path, item: str, refused: list[str]) -> str | None:
    """Root-relative posix path inside the allowed roots, or ``None`` (reported, never read)."""
    try:
        resolved = resolve_allowed_source(item, AllowedRoots.for_project(root), base=root)
    except SourcePathError as exc:
        refused.append(exc.note())
        return None
    try:
        return resolved.relative_to(root).as_posix()
    except ValueError:
        return resolved.as_posix()


def _join(prefix: str, path: str) -> str:
    if not prefix or prefix == ".":
        return Path(path).as_posix()
    return f"{prefix.rstrip('/')}/{Path(path).as_posix()}"


def _rel(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


__all__ = ["build_delta", "git_changes"]
