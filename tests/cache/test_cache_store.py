from __future__ import annotations

import json
from datetime import UTC, timedelta
from pathlib import Path

import pytest

from apiforge.cache.errors import CacheError
from apiforge.cache.freshness import assess, now_utc
from apiforge.cache.policy import LayerPolicy, load_policies, policy_for
from apiforge.cache.store import CacheStore
from apiforge.contracts.cache import CACHE_LAYERS, CacheDep, CacheEntry

KEY = "a" * 64


class _Probe:
    def __init__(self, files: dict[str, str | None], neighborhood: str | None = None) -> None:
        self.files = files
        self.neighborhood = neighborhood

    def dep_sha(self, dep: CacheDep) -> str | None:
        return self.files.get(dep.path)

    def neighborhood_sha(self, nodes: tuple[str, ...]) -> str | None:
        return self.neighborhood

    def symbol_changed(self, manifest_uri: str, symbols: tuple[str, ...]) -> str | None:
        return None


def _entry(**update: object) -> CacheEntry:
    base = CacheEntry(
        layer="capsule",
        key=KEY,
        object_uri="ctx://sha256/" + "b" * 64,
        created_at="2026-09-01T00:00:00Z",
        expires_at="2026-10-01T00:00:00Z",
        deps_files=(CacheDep(path="app/models.py", sha256="s1"),),
    )
    return base.model_copy(update=update)


def test_policy_table_declares_every_layer_and_disables_model_response() -> None:
    policies = load_policies()
    assert set(policies) == set(CACHE_LAYERS)
    assert policies["model_response"].enabled is False
    assert {name for name, p in policies.items() if p.enabled} == {
        "parse",
        "graph",
        "impact",
        "capsule",
    }


@pytest.mark.parametrize(
    ("layer", "code"),
    [("model_response", "AF-CACHE-LAYER-DISABLED"), ("answers", "AF-CACHE-LAYER-UNKNOWN")],
)
def test_disabled_and_unknown_layers_refuse_with_field_and_unlock(layer: str, code: str) -> None:
    with pytest.raises(CacheError) as caught:
        policy_for(layer)
    assert caught.value.code == code
    assert caught.value.field == "layer"
    assert caught.value.unlock


def test_freshness_states_cover_fresh_invalidated_and_both_stale_policies() -> None:
    from datetime import datetime

    moment = datetime(2026, 9, 15, tzinfo=UTC)
    recompute = LayerPolicy("capsule", True, 60, "recompute", True)
    warn = LayerPolicy("validation", True, 60, "warn", False)
    assert assess(_entry(), recompute, now=moment, probe=_Probe({"app/models.py": "s1"}))[0] == (
        "fresh"
    )
    changed = assess(_entry(), recompute, now=moment, probe=_Probe({"app/models.py": "s2"}))
    assert changed[:2] == ("invalidated", "invalidate")
    removed = assess(_entry(), recompute, now=moment, probe=_Probe({}))
    assert "removed" in removed[2]
    late = moment + timedelta(days=30)
    assert assess(_entry(), recompute, now=late)[:2] == ("stale_critical", "recompute")
    assert assess(_entry(), warn, now=late)[:2] == ("stale_harmless", "reuse_warn")
    moved = _entry(neighborhood_sha="n1")
    probe = _Probe({"app/models.py": "s1"}, neighborhood="n2")
    assert assess(moved, recompute, now=moment, probe=probe)[0] == "invalidated"


def test_store_round_trip_invalidate_and_corrupt_reads_recompute(tmp_path: Path) -> None:
    store = CacheStore(tmp_path, enabled=True)
    store.put("capsule", KEY, '{"v": 1}', subject="POST /payments", deps_nodes=("fact:1",))
    decision, payload = store.lookup("capsule", KEY)
    assert (decision.state, decision.tier, payload) == ("fresh", "local", '{"v": 1}')
    dropped = store.invalidate(nodes={"fact:1"})
    assert [(d.subject, d.state) for d in dropped] == [("POST /payments", "invalidated")]
    assert store.lookup("capsule", KEY)[0].state == "miss"
    store.put("capsule", KEY, '{"v": 2}')
    entry_path = tmp_path / ".apiforge" / "cache" / "entries" / "capsule" / f"{KEY}.json"
    entry_path.write_text("{not json", encoding="utf-8")
    decision, payload = store.lookup("capsule", KEY)
    assert (decision.state, decision.action, payload) == ("corrupt", "recompute", None)


def test_tampered_object_is_never_returned(tmp_path: Path) -> None:
    store = CacheStore(tmp_path, enabled=True)
    entry = store.put("impact", KEY, '{"findings": []}')
    assert entry is not None
    obj = tmp_path / ".apiforge" / "cache" / "objects" / entry.object_uri.rsplit("/", 1)[-1]
    obj.write_text('{"findings": ["forged"]}', encoding="utf-8")
    decision, payload = store.lookup("impact", KEY)
    assert decision.state == "corrupt" and payload is None


def test_disabled_store_never_reads_or_writes(tmp_path: Path) -> None:
    store = CacheStore(tmp_path, enabled=False)
    assert store.put("capsule", KEY, "x") is None
    assert store.lookup("capsule", KEY)[0].reason == "cache disabled"
    assert not (tmp_path / ".apiforge" / "cache").exists()


def test_shared_tier_serves_a_second_root_and_copies_locally(tmp_path: Path) -> None:
    home = tmp_path / "home"
    CacheStore(tmp_path / "a", home=home, enabled=True).put("capsule", KEY, "shared payload")
    other = CacheStore(tmp_path / "b", home=home, enabled=True)
    decision, payload = other.lookup("capsule", KEY)
    assert (decision.tier, payload) == ("shared", "shared payload")
    assert other.lookup("capsule", KEY)[0].tier == "local"


def test_gc_reports_by_default_and_deletes_only_with_apply(tmp_path: Path) -> None:
    store = CacheStore(tmp_path, enabled=True)
    store.put("capsule", KEY, "old", now=now_utc() - timedelta(days=30))
    (tmp_path / ".apiforge" / "cache" / "objects").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".apiforge" / "cache" / "objects" / ("c" * 64)).write_text("orphan")
    report = store.gc()
    assert report["applied"] is False and len(report["entries"]) == 1 and report["objects"] == 2
    assert store.stats()["layers"]["capsule"]["expired"] == 1
    applied = store.gc(apply=True)
    assert applied["applied"] is True
    assert store.stats()["layers"] == {}


def test_stats_report_layers_tiers_and_policies(tmp_path: Path) -> None:
    store = CacheStore(tmp_path, enabled=True)
    store.put("capsule", KEY, "payload")
    stats = store.stats()
    assert stats["layers"]["capsule"]["entries"] == 1
    assert stats["policies"]["model_response"]["enabled"] is False
    assert json.loads(json.dumps(stats)) == stats


def test_stale_local_falls_through_to_fresh_shared(tmp_path: Path) -> None:
    home = tmp_path / "home"
    stale = CacheStore(tmp_path / "a", home=home, enabled=True)
    stale.put("capsule", KEY, "old payload", now=now_utc() - timedelta(days=30))
    CacheStore(tmp_path / "b", home=home, enabled=True).put("capsule", KEY, "fresh payload")
    decision, payload = stale.lookup("capsule", KEY)
    assert (decision.tier, payload) == ("shared", "fresh payload")


def test_invalid_timestamp_is_a_corrupt_miss(tmp_path: Path) -> None:
    store = CacheStore(tmp_path, enabled=True)
    store.put("capsule", KEY, "payload")
    entry_path = next((tmp_path / ".apiforge" / "cache" / "entries" / "capsule").glob("*.json"))
    data = json.loads(entry_path.read_text(encoding="utf-8"))
    data["created_at"] = "garbage"
    entry_path.write_text(json.dumps(data), encoding="utf-8")
    decision, payload = store.lookup("capsule", KEY)
    assert payload is None
    assert decision.state == "corrupt" and decision.action == "recompute"
