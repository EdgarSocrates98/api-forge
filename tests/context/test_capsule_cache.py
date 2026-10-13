from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from apiforge.cache.errors import CacheError
from apiforge.context.delta import build_delta
from apiforge.context.gateway.canonical import dumps
from apiforge.context.gateway.capsule import build_capsule, emit
from apiforge.context.gateway.levels import graph_key
from apiforge.contracts.cache import CacheDecision
from tests.context.gateway_support import analyzed_root

TARGET = "GET /customers/{customer_id}"
OTHER = "POST /payments"


def _build(root: Path, target: str, **kwargs: object) -> tuple[bytes, CacheDecision | None]:
    seen: list[CacheDecision] = []
    capsule = build_capsule(root, target, on_decision=seen.append, **kwargs)  # type: ignore[arg-type]
    return dumps(emit(capsule)), (seen[0] if seen else None)


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    return analyzed_root(tmp_path, "fastapi")


def test_warm_rebuild_is_a_hit_with_identical_bytes(root: Path) -> None:
    first, miss = _build(root, TARGET)
    second, hit = _build(root, TARGET)
    uncached, none = _build(root, TARGET, cache=False)
    assert miss is not None and miss.state == "miss"
    assert hit is not None and (hit.state, hit.action) == ("fresh", "reuse")
    assert none is None
    assert first == second == uncached
    rows = [
        json.loads(line)
        for line in (root / ".apiforge" / "economy.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    envelope = [r for r in rows if r.get("source") == "envelope"]
    assert envelope[-2]["cost"].get("cache_hits", 0) >= 1


def test_handler_edit_invalidates_only_its_operation(root: Path) -> None:
    _build(root, TARGET)
    _build(root, OTHER)
    route = root / "proj" / "app" / "routes" / "customers.py"
    route.write_text(
        route.read_text(encoding="utf-8").replace("customer not found", "customer missing"),
        encoding="utf-8",
    )
    changed, decision = _build(root, TARGET)
    assert decision is not None and decision.state == "invalidated"
    assert "customers.py" in decision.reason
    assert changed == _build(root, TARGET, cache=False)[0]
    assert _build(root, OTHER)[1].state == "fresh"  # type: ignore[union-attr]


def test_new_model_definition_elsewhere_invalidates(root: Path) -> None:
    _build(root, TARGET)
    (root / "proj" / "app" / "shadow.py").write_text(
        "class Customer:\n    customer_id: str\n", encoding="utf-8"
    )
    decision = _build(root, TARGET)[1]
    assert decision is not None and decision.state == "invalidated"
    assert "defines Customer" in decision.reason


def test_graph_key_follows_case_content_not_case_id(root: Path) -> None:
    case = root / ".apiforge" / "case"
    before = graph_key(case)
    findings = case / "findings.json"
    findings.write_text(findings.read_text(encoding="utf-8") + " ", encoding="utf-8")
    assert graph_key(case) != before


def test_delta_explicit_maps_route_file_to_operation(root: Path) -> None:
    delta = build_delta(root, changed=["proj/app/routes/customers.py"])
    assert delta.source == "explicit"
    assert delta.impacted_operations == (TARGET,)
    assert delta.capsule_targets == (TARGET,)
    assert delta.changed_nodes
    unmapped = build_delta(root, changed=["README.md"])
    assert unmapped.unresolved == ("unmapped:README.md",)
    assert unmapped.status == "ready"


def test_delta_invalidate_drops_only_dependent_selections(root: Path) -> None:
    _build(root, TARGET)
    _build(root, OTHER)
    delta = build_delta(root, changed=["proj/app/routes/customers.py"], invalidate=True)
    assert [d.subject for d in delta.invalidated] == [TARGET]
    assert _build(root, OTHER)[1].state == "fresh"  # type: ignore[union-attr]


def test_delta_refusals_carry_field_and_unlock(root: Path) -> None:
    with pytest.raises(CacheError) as missing:
        build_delta(root)
    assert missing.value.code == "AF-DELTA-INPUT-MISSING" and missing.value.unlock
    with pytest.raises(CacheError) as nogit:
        build_delta(root, base="HEAD~1")
    assert nogit.value.code in {"AF-DELTA-GIT-UNAVAILABLE", "AF-DELTA-REF-INVALID"}
    assert nogit.value.field


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def test_delta_from_git_classifies_contract_edit(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "add", "openapi.yaml", "proj")
    _git(root, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "base")
    contract = root / "openapi.yaml"
    contract.write_text(
        contract.read_text(encoding="utf-8").replace(
            "operationId: listPayments", "operationId: listPaymentsV2"
        ),
        encoding="utf-8",
    )
    delta = build_delta(root, base="HEAD")
    assert delta.source == "git"
    assert [f.path for f in delta.changed_files] == ["openapi.yaml"]
    assert "GET /payments" in delta.impacted_operations
    assert not any(item.startswith("contract-diff-unavailable") for item in delta.unresolved)
    with pytest.raises(CacheError) as bad:
        build_delta(root, base="no-such-ref")
    assert bad.value.code == "AF-DELTA-REF-INVALID"
