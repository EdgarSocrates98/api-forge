import os
from pathlib import Path

import pytest

from apiforge.security.source_paths import (
    OUTSIDE_ROOT,
    AllowedRoots,
    SourcePathError,
    resolve_allowed_source,
)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "src" / "pkg").mkdir(parents=True)
    (root / "src" / "pkg" / "service.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("token\n", encoding="utf-8")
    return root


def _refused(candidate: str, root: Path, roots: AllowedRoots | None = None) -> SourcePathError:
    with pytest.raises(SourcePathError) as err:
        resolve_allowed_source(candidate, roots or AllowedRoots.for_project(root), base=root)
    assert err.value.code == OUTSIDE_ROOT
    assert err.value.field == "path"
    assert err.value.unlock
    return err.value


def test_parent_traversal_is_refused(project: Path) -> None:
    _refused("../secret.txt", project)
    _refused("src/../../secret.txt", project)
    _refused("src\\..\\..\\secret.txt", project)


def test_absolute_paths_outside_roots_are_refused(project: Path) -> None:
    _refused(str(project.parent / "secret.txt"), project)
    _refused("/etc/passwd", project)


def test_windows_drive_and_unc_paths_are_refused(project: Path) -> None:
    _refused("\\\\host\\share\\credentials", project)
    _refused("//host/share/credentials", project)
    if os.name != "nt":
        _refused("C:\\Users\\someone\\credentials", project)
    else:
        _refused("C:\\Windows\\System32\\drivers\\etc\\hosts", project)


def test_symlink_escaping_the_project_is_refused(project: Path) -> None:
    link = project / "src" / "leak"
    try:
        link.symlink_to(project.parent, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not permitted on this host")
    _refused("src/leak/secret.txt", project)


def test_nested_file_inside_the_project_is_allowed(project: Path) -> None:
    resolved = resolve_allowed_source(
        "src/pkg/service.py", AllowedRoots.for_project(project), base=project
    )
    assert resolved == (project / "src" / "pkg" / "service.py").resolve()


def test_declared_workspace_repository_is_allowed_and_undeclared_is_refused(
    tmp_path: Path, project: Path
) -> None:
    declared = tmp_path / "orders-repo"
    undeclared = tmp_path / "other-repo"
    for repo in (declared, undeclared):
        repo.mkdir()
        (repo / "api.py").write_text("y = 2\n", encoding="utf-8")
    (project / ".apiforge").mkdir()
    (project / ".apiforge" / "workspace.yaml").write_text(
        f"repositories:\n  - root: {declared.as_posix()}\n", encoding="utf-8"
    )
    roots = AllowedRoots.for_project(project)
    assert resolve_allowed_source(str(declared / "api.py"), roots, base=project).is_file()
    _refused(str(undeclared / "api.py"), project, roots)


def test_empty_and_nul_paths_are_refused(project: Path) -> None:
    _refused("", project)
    _refused("src/\x00x.py", project)
