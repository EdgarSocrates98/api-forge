from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from apiforge.agentops.agent_audit import audit_agents
from apiforge.debate.packet import referee_packet
from apiforge.debate.service import DebateError, open_debate, submit
from apiforge.knowledge.selector import referenced_packs, select_expertise
from apiforge.runtime.role_context import load_role_policy, plan_roles, task_target
from apiforge.runtime.shadow import decide, sample_rate, sampled
from tests.context.gateway_support import analyzed_root

REPO = Path(__file__).resolve().parents[2]
ROLES = (
    ("api-contract-review", "specialist"),
    ("task-review", "reviewer"),
    ("adversarial-critic", "critic"),
    ("debate-referee", "referee"),
)


def test_selector_loads_only_triggered_packs() -> None:
    picked = select_expertise("make PaymentRequest.description nullable in OpenAPI")
    assert [item.pack_id for item in picked.selected] == [
        "api-lifecycle",
        "json-schema",
        "openapi-31",
    ]
    assert picked.loaded_bytes < picked.catalog_bytes / 10
    assert all(item.reasons for item in picked.selected)
    nothing = select_expertise("hello there")
    assert nothing.selected == () and nothing.unresolved == ("no-expertise-trigger",)


def test_capability_and_framework_add_only_their_packs() -> None:
    picked = select_expertise(
        "hello", capability="api-security-review", frameworks=("spring", "unknown")
    )
    assert [item.pack_id for item in picked.selected] == ["owasp-api-2023", "spring-boot"]


def test_every_trigger_names_an_existing_pack() -> None:
    packs = {path.name for path in (REPO / "knowledge").iterdir() if path.is_dir()}
    assert referenced_packs() <= packs


def test_role_policy_shares_fit_the_envelope() -> None:
    policy = load_role_policy()
    assert sum(float(row["share"]) for row in policy["classes"].values()) <= 1.0
    assert policy["roles"]["referee"] == "disagreements_only"


def test_task_target_reads_target_or_graph_target() -> None:
    assert task_target(SimpleNamespace(inputs=("target=POST /x", "case=c"))) == ("POST /x", "c")
    graph = SimpleNamespace(inputs=("graph_target=operation:GET /y",))
    assert task_target(graph) == ("GET /y", None)


def test_roles_get_subsets_of_one_capsule(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path, "fastapi")
    spec = SimpleNamespace(
        inputs=("target=POST /payments",), outcome="make POST /payments idempotent"
    )
    plan = plan_roles(root, spec, ROLES, context_bytes=32000, run_id="run-roles")
    rows = {row.role: row for row in plan.roles}
    assert plan.capsule_id and not plan.unresolved
    assert rows["specialist"].bytes >= rows["reviewer"].bytes >= rows["critic"].bytes
    assert rows["referee"].refs == () and rows["referee"].bytes == 0
    assert set(rows["reviewer"].refs) <= set(rows["specialist"].refs) | set(rows["critic"].refs) | {
        ref for row in plan.roles for ref in row.refs
    }
    assert plan.total_bytes <= 0.6 * plan.naive_bytes
    assert "idempotency" in rows["specialist"].expertise


def test_tight_budget_trims_and_says_so(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path, "fastapi")
    spec = SimpleNamespace(inputs=("target=POST /payments",), outcome="x")
    plan = plan_roles(root, spec, ROLES[:1], context_bytes=2000, run_id="run-tight")
    assert plan.roles[0].trimmed
    assert any(item.startswith("AF-ROLE-CONTEXT-BUDGET") for item in plan.unresolved)


def test_no_target_means_no_capsule_refs(tmp_path: Path) -> None:
    spec = SimpleNamespace(inputs=("project=p",), outcome="review")
    plan = plan_roles(tmp_path, spec, ROLES, context_bytes=32000, run_id="run-none")
    assert plan.capsule_id is None
    assert plan.unresolved == ("capsule-unavailable:no-target",)
    assert all(row.refs == () for row in plan.roles)


def test_shadow_sampling_is_deterministic_and_bounded() -> None:
    assert sampled("run-a", 0.1) == sampled("run-a", 0.1)
    ids = [f"run-{index:05d}" for index in range(10000)]
    assert abs(sample_rate(ids, 0.1) - 0.1) <= 0.02
    assert decide("run-a", 0.0, ("x",), 5).reason.startswith("shadow disabled")
    assert decide("run-a", 0.5, (), 5).reason == "no challenger planned"
    hit = next(item for item in ids if sampled(item, 0.2))
    starved = decide(hit, 0.2, ("x",), 0)
    assert starved.sampled and not starved.executed and "AF-ECONOMY-SHADOW-BUDGET" in starved.reason
    assert decide(hit, 0.2, ("x",), 1).challenger == "x"


def test_position_deltas_and_referee_packet(tmp_path: Path) -> None:
    debate = open_debate(tmp_path, "retry on 409?", ("retry", "no-retry"), "2026-09-28T00:00:00Z")
    submit(
        tmp_path,
        debate.debate_id,
        "retry",
        "retry once",
        ("fact:a",),
        disagreements=(("retry semantics", "409 in flight"),),
        risks=("dup",),
        confidence=0.7,
    )
    submit(tmp_path, debate.debate_id, "no-retry", "surface 409", ("fact:a", "fact:b"))
    submit(tmp_path, debate.debate_id, "retry", "retry after 200ms", ("fact:c",))
    packet = referee_packet(
        tmp_path, debate.debate_id, capsule_id="ctx://sha256/" + "0" * 64, capsule_bytes=10000
    )
    assert [item.side for item in packet.positions] == ["no-retry", "retry"]
    assert packet.positions[1].position == "retry after 200ms"
    assert packet.evidence == ("fact:a", "fact:b", "fact:c")
    assert packet.packet_bytes <= 0.5 * packet.naive_bytes
    with pytest.raises(DebateError) as bad:
        submit(tmp_path, debate.debate_id, "retry", "x", ("fact:a",), confidence=1.5)
    assert bad.value.code == "AF-DEBATE-DELTA-INVALID"


def test_agent_audit_is_deterministic_and_complete() -> None:
    first = audit_agents(REPO)
    assert first == audit_agents(REPO)
    assert first["agents"] == len(first["rows"]) >= 8
    verdicts = {row["agent"]: row for row in first["rows"]}
    assert verdicts["api-debate-referee"]["unique_decision_role"] is True
    assert verdicts["api-debate-referee"]["verdict"] == "keep"
    for row in first["rows"]:
        if row["verdict"] == "merge-candidate":
            assert not any(value for key, value in row.items() if key.startswith("unique_"))


def test_role_context_plan_cannot_exceed_the_envelope() -> None:
    import pytest
    from pydantic import ValidationError

    from apiforge.contracts.selective import RoleContext, RoleContextPlan

    rows = tuple(
        RoleContext(
            role="specialist",
            capability=f"spec-{index}",
            context_class="focused",
            bytes=16000,
            budget_bytes=16000,
        )
        for index in range(2)
    )
    with pytest.raises(ValidationError):
        RoleContextPlan(run_id="r", context_bytes=32000, roles=(*rows, rows[0]), total_bytes=48000)
    with pytest.raises(ValidationError):
        RoleContextPlan(run_id="r", context_bytes=32000, roles=rows, total_bytes=1)


def test_specialists_share_one_class_pool(tmp_path) -> None:
    from apiforge.runtime.role_context import plan_roles
    from tests.context.gateway_support import analyzed_root
    from tests.runtime.test_role_context_supervisor import TASK, _task

    root = analyzed_root(tmp_path, "fastapi")
    _task(root)
    from apiforge.taskspec.store import load

    plan = plan_roles(
        root,
        load(root, TASK),
        (("a", "specialist"), ("b", "specialist"), ("c", "reviewer")),
        context_bytes=32000,
        run_id="run-pool",
    )
    specialists = [row for row in plan.roles if row.role == "specialist"]
    assert sum(row.budget_bytes for row in specialists) <= specialists[0].pool_bytes
    assert plan.total_bytes <= 32000
