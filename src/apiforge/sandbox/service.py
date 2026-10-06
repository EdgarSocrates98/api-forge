"""Copy-based sandbox: two copies, one injected analyzer, a named delta."""

from __future__ import annotations

import hashlib
import json
import shutil
from collections.abc import Callable, Mapping
from pathlib import Path, PurePosixPath
from typing import Any

from apiforge.sandbox.diff import Patch, SandboxError, apply_hunks, parse_unified_diff

SKIPPED_DIRS = (".git", ".apiforge", ".venv", "__pycache__", "node_modules", "dist", "build")

Analyze = Callable[[Path], Any]


def _inventory(root: Path) -> tuple[dict[str, str], list[str]]:
    files: dict[str, str] = {}
    skipped: set[str] = set()
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in SKIPPED_DIRS for part in rel.parts):
            skipped.update(part for part in rel.parts if part in SKIPPED_DIRS)
            continue
        if path.is_symlink():
            skipped.add(str(rel))
            continue
        if path.is_file():
            files[rel.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return files, sorted(skipped)


def _safe_relpath(path: str) -> bool:
    p = PurePosixPath(path)
    return not (p.is_absolute() or ".." in p.parts or not p.parts)


def _norm(items: Any) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if hasattr(item, "model_dump"):
            out.append(item.model_dump(mode="json"))
        elif isinstance(item, Mapping):
            out.append(dict(item))
    return out


def _key(item: Mapping[str, Any]) -> str:
    return json.dumps(item, sort_keys=True)


def _path_of(item: Mapping[str, Any]) -> str | None:
    p = item.get("path")
    if isinstance(p, str):
        return p
    src = item.get("source")
    if isinstance(src, Mapping):
        return src.get("path") if isinstance(src.get("path"), str) else None
    return None


def _delta(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    bkeys = {_key(b) for b in before}
    akeys = {_key(a) for a in after}
    cand_new = [a for a in after if _key(a) not in bkeys]
    cand_res = [b for b in before if _key(b) not in akeys]
    moved: list[dict[str, Any]] = []
    for a in list(cand_new):
        match = next(
            (
                b
                for b in cand_res
                if b.get("rule_id") == a.get("rule_id") and _path_of(b) != _path_of(a)
            ),
            None,
        )
        if match is not None:
            moved.append({"rule_id": a.get("rule_id"), "from": _path_of(match), "to": _path_of(a)})
            cand_new.remove(a)
            cand_res.remove(match)
    return {
        "new": cand_new,
        "resolved": cand_res,
        "kept_count": len(after) - len(cand_new) - len(moved),
        "moved_candidates": moved,
    }


def _apply_patch(target: Path, patch: Patch) -> None:
    if patch.old_path is None:
        dest = target / patch.new_path  # type: ignore[operator]
        dest.parent.mkdir(parents=True, exist_ok=True)
        added = [line[1:] for h in patch.hunks for line in h.lines if line.startswith("+")]
        dest.write_text("\n".join(added) + "\n", encoding="utf-8")
        return
    src = target / patch.old_path
    if patch.new_path is None:
        src.unlink()
        return
    raw = src.read_bytes()
    newline = "\r\n" if b"\r\n" in raw else "\n"
    original = raw.decode("utf-8").splitlines()
    patched = apply_hunks(original, patch.hunks)
    src.write_bytes((newline.join(patched) + newline).encode("utf-8"))


def _base_report(applied: bool) -> dict[str, Any]:
    return {
        "applied": applied,
        "main_tree_touched": False,
        "id": None,
        "files_changed": [],
        "new": [],
        "resolved": [],
        "kept_count": 0,
        "moved_candidates": [],
        "scan_refused": {"before": [], "after": []},
        "copy_skipped": [],
        "refused": [],
        "next_steps": [],
    }


def sandbox_apply(root: Path, diff_text: str, analyze: Analyze) -> dict[str, Any]:
    root = Path(root)
    report = _base_report(False)
    inventory, copy_skipped = _inventory(root)
    report["copy_skipped"] = copy_skipped
    try:
        patches = parse_unified_diff(diff_text)
    except SandboxError as exc:
        report["refused"].append({"code": exc.code, "detail": exc.detail})
        return report
    for patch in patches:
        for raw in (patch.old_path, patch.new_path):
            if raw is not None and not _safe_relpath(raw):
                report["refused"].append(
                    {
                        "code": "AF-SANDBOX-PATH-OUTSIDE",
                        "field": "path",
                        "detail": f"{raw} escapes the copied root",
                        "unlock": "keep diff paths relative to the project root",
                    }
                )
        if patch.old_path is not None and patch.old_path not in inventory:
            report["refused"].append(
                {
                    "code": "AF-SANDBOX-TARGET-MISSING",
                    "field": "path",
                    "detail": f"{patch.old_path} not present in the source tree",
                    "unlock": "regenerate the diff against the current tree",
                }
            )
    if report["refused"]:
        return report
    manifest = json.dumps(inventory, sort_keys=True).encode()
    sandbox_id = hashlib.sha256(diff_text.encode("utf-8") + manifest).hexdigest()[:16]
    base = root / ".apiforge" / "sandbox" / sandbox_id
    tmp = base.parent / (sandbox_id + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    before = tmp / "before"
    after = tmp / "after"
    for rel in inventory:
        for side in (before, after):
            dest = side / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel, dest, follow_symlinks=False)
    for patch in patches:
        _apply_patch(after, patch)
    found: dict[str, list[dict[str, Any]]] = {}
    for name, side in (("before", before), ("after", after)):
        try:
            found[name] = _norm(analyze(side))
        except (OSError, ValueError, KeyError, RuntimeError) as exc:
            found[name] = []
            report["scan_refused"][name].append(
                {"code": "AF-SANDBOX-ANALYZE-FAILED", "detail": str(exc)}
            )
    report.update(
        {
            "applied": True,
            "id": sandbox_id,
            "files_changed": [p.new_path or p.old_path for p in patches],
            "next_steps": [
                "run the test suite inside the sandbox copy before promoting",
                "re-run analyze with a baseline contract to surface breaking changes",
            ],
            **_delta(found["before"], found["after"]),
        }
    )
    (tmp / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if base.exists():
        stale = base.parent / (sandbox_id + ".stale")
        shutil.rmtree(stale, ignore_errors=True)
        base.rename(stale)
        tmp.rename(base)
        shutil.rmtree(stale, ignore_errors=True)
    else:
        tmp.rename(base)
    return report


def sandbox_clean(root: Path) -> dict[str, Any]:
    sandbox_dir = Path(root) / ".apiforge" / "sandbox"
    removed = (
        sorted(p.name for p in sandbox_dir.iterdir() if p.is_dir()) if sandbox_dir.is_dir() else []
    )
    shutil.rmtree(sandbox_dir, ignore_errors=True)
    return {"removed": removed, "root": str(root)}
