from __future__ import annotations

from apiforge.contracts.agentic import AgentCapabilityProfile
from apiforge.contracts.routing import RoutingRequest
from apiforge.knowledge.loader import Pack, Source
from apiforge.runtime.registry import Capability
from apiforge.runtime.routing import assess_candidates


def _profiles() -> dict[str, AgentCapabilityProfile]:
    return {
        "contract-v1": AgentCapabilityProfile(
            profile_id="contract-v1",
            agent="contract-agent",
            capabilities=("api-contract-review",),
            required_evidence=("task_spec",),
            accepted_risks=("read_only",),
            expertise_packs=("openapi",),
        ),
        "contract-v2": AgentCapabilityProfile(
            profile_id="contract-v2",
            agent="contract-agent-v2",
            capabilities=("api-contract-review",),
            required_evidence=("task_spec",),
            accepted_risks=("read_only",),
            expertise_packs=("openapi",),
        ),
    }


def _capabilities() -> dict[str, Capability]:
    return {
        "contract-v1": Capability(
            "contract-v1",
            "contract-agent",
            "specialist",
            "read_only",
            family="api-contract-review",
            implementation="v1",
            expertise_packs=("openapi",),
        ),
        "contract-v2": Capability(
            "contract-v2",
            "contract-agent-v2",
            "specialist",
            "read_only",
            family="api-contract-review",
            implementation="v2",
            expertise_packs=("openapi",),
        ),
    }


def _request(*, available_expertise: tuple[str, ...] = ()) -> RoutingRequest:
    return RoutingRequest(
        task_id="expertise-task",
        revision=1,
        risk="read_only",
        requested_capabilities=("api-contract-review",),
        required_evidence=("task_spec",),
        available_evidence=("task_spec",),
        available_expertise=available_expertise,
        policy_id="routing/v1",
    )


def test_family_request_exposes_all_eligible_implementations() -> None:
    assessments = assess_candidates(
        _capabilities(), _profiles(), _request(available_expertise=("openapi",))
    )

    assert [item.capability for item in assessments] == ["contract-v1", "contract-v2"]
    assert all(item.eligible for item in assessments)
    assert {item.implementation for item in assessments} == {"v1", "v2"}


def test_missing_expertise_is_an_actionable_eligibility_refusal() -> None:
    assessments = assess_candidates(_capabilities(), _profiles(), _request())

    assert all(not item.eligible for item in assessments)
    assert all(item.rejection is not None for item in assessments)
    assert all(
        item.rejection["field"] == "capability.expertise_packs"
        for item in assessments
        if item.rejection
    )


def test_validated_pack_projects_to_routing_metadata() -> None:
    pack = Pack(
        domain="openapi",
        version=3,
        areas=("api",),
        rule_ids=("api-contract",),
        summary="OpenAPI expertise",
        sources=(Source("spec", "https://example.test/spec", "openapi-spec", "2026-09-24"),),
        verified="2026-09-24",
    )

    contract = pack.as_expertise_pack(freshness="fresh", source_refs=("receipt:openapi",))

    assert contract.pack_id == "openapi"
    assert contract.pack_version == 3
    assert contract.freshness == "fresh"
