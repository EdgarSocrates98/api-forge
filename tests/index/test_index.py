"""TokenSave: content-hash cache + canonical index files."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.adapters.inventory import CodeInventory
from apiforge.application.analyze import analyze_project
from apiforge.contracts.base import ContractError
from apiforge.index.build import build_index, index_status
from apiforge.index.cache import extract_cached
from apiforge.index.treehash import source_digest

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures"
PROJECT = FIXTURES / "fastapi_orders"


def test_cache_hit_returns_identical_inventory(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    first, meta1 = extract_cached(PROJECT, "fastapi", extract_fastapi, cache)
    second, meta2 = extract_cached(PROJECT, "fastapi", extract_fastapi, cache)
    assert meta1["hit"] is False
    assert meta2["hit"] is True
    assert meta1["key"] == meta2["key"]
    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_cache_key_changes_when_source_changes(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "app.py").write_text("x = 1\n", encoding="utf-8")
    cache = tmp_path / "cache"
    _, meta1 = extract_cached(project, "fastapi", extract_fastapi, cache)
    (project / "app.py").write_text("x = 2\n", encoding="utf-8")
    _, meta2 = extract_cached(project, "fastapi", extract_fastapi, cache)
    assert meta1["key"] != meta2["key"]


def test_corrupt_cache_self_heals(tmp_path: Path) -> None:
    cache = tmp_path / "cache"
    extract_cached(PROJECT, "fastapi", extract_fastapi, cache)
    path = next(cache.glob("*.json"))
    path.write_text("{corrupt", encoding="utf-8")
    inv, meta2 = extract_cached(PROJECT, "fastapi", extract_fastapi, cache)
    assert meta2["hit"] is False
    assert isinstance(inv, CodeInventory)
    # rewritten cache now validates
    _, meta3 = extract_cached(PROJECT, "fastapi", extract_fastapi, cache)
    assert meta3["hit"] is True


def test_cache_disabled_without_dir() -> None:
    inv, meta = extract_cached(PROJECT, "fastapi", extract_fastapi, None)
    assert meta["enabled"] is False
    assert isinstance(inv, CodeInventory)


def test_analyze_records_cache_meta(tmp_path: Path) -> None:
    out = tmp_path / "case"
    cache = tmp_path / "cache"
    r1 = analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml", PROJECT, None, out,
        cache_dir=cache, ledger_root=tmp_path,
    )
    out2 = tmp_path / "case2"
    r2 = analyze_project(
        FIXTURES / "openapi" / "orders-v1.yaml", PROJECT, None, out2,
        cache_dir=cache, ledger_root=tmp_path,
    )
    assert r1.cache["enabled"] is True and r1.cache["hit"] is False
    assert r2.cache["hit"] is True
    ledger = tmp_path / ".apiforge" / "economy.jsonl"
    entries = [json.loads(l) for l in ledger.read_text().splitlines() if l.strip()]
    hits = [e for e in entries if e["verb"] == "cache:extract:fastapi"]
    assert any(e["detail_level"] == "hit" for e in hits)
    assert any(e["detail_level"] == "miss" for e in hits)


def test_index_build_writes_four_files(tmp_path: Path) -> None:
    manifest = build_index(PROJECT, tmp_path)
    index = tmp_path / ".apiforge" / "index"
    for name in ("files", "symbols", "routes", "facts"):
        assert (index / f"{name}.jsonl").is_file()
    assert manifest["counts"]["routes"] > 0
    assert manifest["unresolved"]["note"]
    rows = [
        json.loads(l)
        for l in (index / "routes.jsonl").read_text().splitlines()
        if l.strip()
    ]
    assert all(r["method"] and r["path"] for r in rows)


def test_index_status_names_drift(tmp_path: Path) -> None:
    project = tmp_path / "proj"
    project.mkdir()
    (project / "app.py").write_text("x = 1\n", encoding="utf-8")
    (project / "gone.py").write_text("y = 1\n", encoding="utf-8")
    build_index(project, tmp_path, framework="fastapi")
    (project / "app.py").write_text("x = 2\n", encoding="utf-8")
    (project / "gone.py").unlink()
    (project / "new.py").write_text("z = 1\n", encoding="utf-8")
    status = index_status(project, tmp_path)
    assert status["stale"] is True
    assert status["changed"] == ["app.py"]
    assert status["removed"] == ["gone.py"]
    assert status["added"] == ["new.py"]


def test_index_status_clean(tmp_path: Path) -> None:
    build_index(PROJECT, tmp_path)
    status = index_status(PROJECT, tmp_path)
    assert status["stale"] is False
    assert status["added"] == status["removed"] == status["changed"] == []


def test_index_status_refuses_without_build(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match="AF-INDEX-NOT-BUILT"):
        index_status(PROJECT, tmp_path)


def test_source_digest_is_deterministic() -> None:
    d1, rows1 = source_digest(PROJECT)
    d2, rows2 = source_digest(PROJECT)
    assert d1 == d2
    assert rows1 == rows2
    assert all(r["sha256"] for r in rows1)
