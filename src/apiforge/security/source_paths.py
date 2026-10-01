"""One containment check for every path that comes from case, fact or graph data.

A case, a fact's ``source.path`` or a graph node's ``props.path`` is data, not
authority: a tampered value such as ``../.env``, ``/etc/passwd``,
``C:\\Users\\...`` or ``\\\\host\\share`` must never be opened or copied into
``ctx://``. ``resolve_allowed_source`` accepts a path only when, after symlinks
are followed, it lies inside the project root or a repository declared in the
project's ``WorkspaceManifest``. Callers refuse the single ref (reporting
``AF-PATH-OUTSIDE-ROOT`` as unresolved) and keep serving the rest.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath

from apiforge.contracts.base import ContractError

OUTSIDE_ROOT = "AF-PATH-OUTSIDE-ROOT"
_UNLOCK = "keep sources inside the project or declare the repository in .apiforge/workspace.yaml"


class SourcePathError(ContractError):
    def __init__(self, candidate: str, reason: str) -> None:
        super().__init__(OUTSIDE_ROOT, f"{candidate!r}: {reason}")
        self.candidate = candidate
        self.reason = reason
        self.field = "path"
        self.unlock = _UNLOCK

    def note(self) -> str:
        """Unresolved entry for callers that refuse one ref and continue."""
        return f"{OUTSIDE_ROOT}:{self.candidate} ({self.reason}); field=path; unlock={_UNLOCK}"


@dataclass(frozen=True)
class AllowedRoots:
    paths: tuple[Path, ...]

    @classmethod
    def for_project(cls, root: Path) -> AllowedRoots:
        """Project root plus repositories declared in its workspace manifest (declared only)."""
        base = Path(root).resolve()
        roots = [base]
        for manifest in (base / ".apiforge" / "workspace.yaml", base / "workspace.yaml"):
            if not manifest.is_file():
                continue
            try:
                from apiforge.workspace.manifests import load_workspace_manifest

                workspace = load_workspace_manifest(manifest)
            except (ContractError, OSError, ValueError):
                break
            roots.extend(Path(repository.root).resolve() for repository in workspace.repositories)
            break
        return cls(tuple(dict.fromkeys(roots)))


def _is_unc(raw: str) -> bool:
    return raw.startswith(("\\\\", "//")) or bool(PureWindowsPath(raw).drive.startswith("\\\\"))


def resolve_allowed_source(candidate: object, roots: AllowedRoots, *, base: Path) -> Path:
    """Return the resolved path inside an allowed root, or raise ``SourcePathError``."""
    raw = str(candidate or "").strip()
    if not raw:
        raise SourcePathError(raw, "empty path")
    if "\x00" in raw:
        raise SourcePathError(raw, "NUL byte in path")
    if _is_unc(raw):
        raise SourcePathError(raw, "UNC path")
    if ".." in PurePosixPath(raw.replace("\\", "/")).parts:
        raise SourcePathError(raw, "parent traversal")
    native = Path(raw)
    if PureWindowsPath(raw).drive and not native.is_absolute():
        raise SourcePathError(raw, "foreign drive-qualified path")
    target = (native if native.is_absolute() else Path(base) / native).resolve(strict=False)
    for root in roots.paths:
        try:
            target.relative_to(root)
        except ValueError:
            continue
        return target
    raise SourcePathError(raw, "outside allowed roots (symlinks are followed)")


def confine_dir(root: Path, value: object, *, field: str = "case_dir") -> Path:
    """Caller-supplied directories (``--case-dir``, ``--case``) obey the same trust boundary.

    Agents and MCP hosts pass these paths too; outside the allowed roots the
    command is refused (a case is required input, so there is nothing to serve).
    """
    try:
        return resolve_allowed_source(value, AllowedRoots.for_project(root), base=Path(root))
    except SourcePathError as exc:
        exc.field = field
        raise


__all__ = [
    "OUTSIDE_ROOT",
    "AllowedRoots",
    "SourcePathError",
    "confine_dir",
    "resolve_allowed_source",
]
