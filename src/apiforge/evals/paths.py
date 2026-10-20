"""Resolve evals data paths across source checkout and installed wheel layouts.

The CLI keeps ``Path("evals/...")`` defaults so the repo layout stays the
readable one. When that path does not exist — an installed wheel running in an
empty workspace, or a case root that has no ``evals/`` tree — the packaged copy
under ``apiforge/_data/`` (force-included by ``pyproject.toml``) answers
instead. Paths that already exist are returned untouched: a user workspace's
own corpus always wins, and only paths anchored at an ``evals`` segment are
eligible for the fallback — anything else is the caller's data, not ours.
"""

from __future__ import annotations

from pathlib import Path


def resolve_evals_path(path: Path | str) -> Path:
    """Map an ``evals/``-anchored path to the packaged copy when needed.

    Only relative paths are eligible for fallback: they are the CLI defaults
    and workspace-relative references. A nonexistent *absolute* path is the
    caller's explicit data — remapping it to packaged corpora would mask
    typos with a false success, so it is returned untouched (the caller
    then reports the honest ENOENT/refusal).
    """

    value = Path(path)
    if value.exists() or value.is_absolute():
        return value
    parts = value.parts
    # Anchor at the FIRST segment only: `evals/...` is the CLI default shape,
    # while `mydata/evals/x` is a workspace path that merely contains an
    # `evals` segment — remapping it would mask a typo with packaged data.
    if not parts or parts[0] != "evals":
        return value
    from apiforge.distribution.assets import package_root

    packaged = package_root() / "_data" / value
    if packaged.exists():
        return packaged
    repo = package_root().parent.parent
    if (repo / "pyproject.toml").is_file():
        checkout = repo / value
        if checkout.exists():
            return checkout
    return value


def resolve_task_resource(ref: Path | str, repo_root: Path | str) -> Path:
    """Resolve a case file reference against repo_root, then packaged data.

    Eval cases reference fixtures as repo-relative paths (``tests/fixtures/…``).
    In a wheel-only install the checkout tree is absent, so refs anchored at
    ``tests/`` fall back to the packaged copy under ``_data/tests``. Any other
    ref — or a missing packaged copy — is returned untouched so the caller
    reports the honest ENOENT instead of a masked false success.
    """

    value = Path(ref)
    base = Path(repo_root)
    if value.is_absolute() or (base / value).exists():
        return base / value
    if value.parts and value.parts[0] == "tests":
        from apiforge.distribution.assets import package_root

        packaged = package_root() / "_data" / value
        if packaged.exists():
            return packaged
        repo = package_root().parent.parent
        if (repo / "pyproject.toml").is_file():
            checkout = repo / value
            if checkout.exists():
                return checkout
    return base / value


__all__ = ["resolve_evals_path", "resolve_task_resource"]
