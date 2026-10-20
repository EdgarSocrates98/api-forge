"""Wheel-vs-source resolution contract for ``resolve_evals_path``.

Precedence under test:
1. an existing path always wins untouched;
2. a missing relative ``evals/`` path falls back to ``apiforge/_data``;
3. a missing relative path falls back to a checkout marked by
   ``pyproject.toml`` when there is no packaged copy;
4. a missing *absolute* path is returned untouched — never remapped;
5. non-``evals`` paths are never eligible for fallback.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apiforge.evals.paths import resolve_evals_path


@pytest.fixture
def layouts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Path]:
    """Simulate an editable-style layout: package root lives inside the repo
    (``repo/src/apiforge``) so ``package_root().parent.parent`` is the repo,
    plus a packaged ``_data`` copy for the wheel path."""
    repo = tmp_path / "checkout"
    pkg = repo / "src" / "apiforge"
    data = pkg / "_data" / "evals" / "corpus" / "suite-x"
    data.mkdir(parents=True)
    (data / "cases.json").write_text("[]")
    from apiforge.distribution import assets

    monkeypatch.setattr(assets, "package_root", lambda: pkg)
    return {"pkg": pkg, "data": data, "repo": repo}


def test_existing_path_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    local = tmp_path / "evals" / "x.yaml"
    local.parent.mkdir(parents=True)
    local.write_text("y")
    monkeypatch.chdir(tmp_path)
    assert resolve_evals_path(Path("evals/x.yaml")) == Path("evals/x.yaml")


def test_missing_relative_falls_back_to_packaged(layouts: dict[str, Path]) -> None:
    out = resolve_evals_path(Path("evals/corpus/suite-x/cases.json"))
    assert out == layouts["pkg"] / "_data" / "evals" / "corpus" / "suite-x" / "cases.json"


def test_missing_relative_falls_back_to_checkout(layouts: dict[str, Path]) -> None:
    repo = layouts["repo"]
    (repo / "evals" / "corpus" / "other").mkdir(parents=True)
    (repo / "evals" / "corpus" / "other" / "cases.json").write_text("[]")
    (repo / "pyproject.toml").write_text("[project]")
    out = resolve_evals_path(Path("evals/corpus/other/cases.json"))
    assert out == repo / "evals" / "corpus" / "other" / "cases.json"


def test_checkout_without_marker_is_ignored(layouts: dict[str, Path]) -> None:
    repo = layouts["repo"]
    (repo / "evals" / "corpus" / "other").mkdir(parents=True)
    (repo / "evals" / "corpus" / "other" / "cases.json").write_text("[]")
    out = resolve_evals_path(Path("evals/corpus/other/cases.json"))
    assert out == Path("evals/corpus/other/cases.json")


def test_absolute_missing_path_is_not_remapped(layouts: dict[str, Path]) -> None:
    missing = Path("/nonexistent-xyz/evals/corpus/suite-x/cases.json")
    assert resolve_evals_path(missing) == missing


def test_non_evals_path_is_not_remapped(layouts: dict[str, Path]) -> None:
    missing = Path("corpus/suite-x/cases.json")
    assert resolve_evals_path(missing) == missing


def test_midpath_evals_segment_is_not_remapped(layouts: dict[str, Path]) -> None:
    """`mydata/evals/x` merely contains an `evals` segment — not a CLI
    default shape — so a missing workspace path must stay missing."""
    missing = Path("mydata/evals/corpus/suite-x/cases.json")
    assert resolve_evals_path(missing) == missing


def test_run_knowledge_drift_uses_packaged_fallback(monkeypatch, tmp_path):
    """Wheel-only: corpus relativo inexistente cai no _data packaged."""
    from apiforge.evals import knowledge_drift

    monkeypatch.chdir(tmp_path)
    out = knowledge_drift.run_knowledge_drift(Path("evals/corpus/knowledge-drift"))
    assert out["totals"]["cases"] > 0


def test_run_knowledge_drift_empty_corpus_refuses(tmp_path):
    import pytest

    from apiforge.contracts.base import ContractError
    from apiforge.evals import knowledge_drift

    with pytest.raises(ContractError, match="AF-EVALS-INVALID"):
        knowledge_drift.run_knowledge_drift(tmp_path)


def test_run_graph_quality_uses_packaged_fallback(monkeypatch, tmp_path):
    from apiforge.evals import graph_quality

    monkeypatch.chdir(tmp_path)
    out = graph_quality.run_graph_quality(Path("evals/corpus/graph-quality"))
    assert out["cases"] > 0


def test_run_matrix_uses_packaged_fallback(monkeypatch, tmp_path):
    from apiforge.evals import matrix

    monkeypatch.chdir(tmp_path)
    report = matrix.run_matrix(Path("evals/corpus/economy-matrix"), tmp_path)
    assert report.tasks > 0


def test_resolve_task_resource_workspace_wins(tmp_path):
    from apiforge.evals.paths import resolve_task_resource

    f = tmp_path / "tests" / "fixtures" / "x.proto"
    f.parent.mkdir(parents=True)
    f.write_text("x")
    assert resolve_task_resource("tests/fixtures/x.proto", tmp_path) == f


def test_resolve_task_resource_packaged_fallback(tmp_path):
    from apiforge.evals.paths import resolve_task_resource

    out = resolve_task_resource("tests/fixtures/grpc/orders.proto", tmp_path)
    if "_data" in str(out):
        assert out.is_file()
    else:  # checkout dev — repo_root e o proprio repo
        assert out.as_posix().endswith("tests/fixtures/grpc/orders.proto")


def test_resolve_task_resource_non_tests_ref_untouched(tmp_path):
    from apiforge.evals.paths import resolve_task_resource

    out = resolve_task_resource("data/foo.yaml", tmp_path)
    assert out == tmp_path / "data" / "foo.yaml"


def test_dotdot_never_remaps(tmp_path, monkeypatch):
    """evals/../x nao escapa a raiz do corpus para site-packages."""
    from apiforge.evals.paths import resolve_evals_path, resolve_task_resource

    monkeypatch.chdir(tmp_path)
    out = resolve_evals_path(Path("evals/../../otherpkg/file"))
    assert out == Path("evals/../../otherpkg/file")
    out2 = resolve_task_resource("tests/../secret.yaml", tmp_path)
    assert out2 == tmp_path / "tests" / ".." / "secret.yaml"
