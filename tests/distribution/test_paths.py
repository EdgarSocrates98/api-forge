from pathlib import Path

from apiforge.distribution.paths import resolve_paths


def test_paths_honor_user_selected_environment_roots(tmp_path: Path) -> None:
    paths = resolve_paths(
        cwd=tmp_path,
        package_root=tmp_path / "package",
        env={"APIFORGE_HOME": "runtime", "APIFORGE_CACHE": "cache"},
    )
    assert paths.state_root == (tmp_path / "runtime").resolve()
    assert paths.cache_root == (tmp_path / "cache").resolve()
    assert paths.package_root == (tmp_path / "package").resolve()


def test_cache_switch_value_is_not_a_cache_directory(tmp_path: Path) -> None:
    paths = resolve_paths(
        cwd=tmp_path,
        package_root=tmp_path / "package",
        env={"APIFORGE_HOME": "runtime", "APIFORGE_CACHE": "off"},
    )
    assert paths.cache_root == (tmp_path / "runtime" / "cache").resolve()
