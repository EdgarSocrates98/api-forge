"""Chaos scenario catalog: declared data, complete FASE 12 coverage."""

from apiforge.perf.chaos import SCENARIOS, list_scenarios


def test_thirteen_scenarios_cover_the_prompt_list() -> None:
    names = " ".join(s.name for s in SCENARIOS)
    assert len(SCENARIOS) == 13
    for needle in (
        "total dependency outage",
        "gradual dependency latency",
        "extreme dependency latency",
        "random timeouts",
        "intermittent failures",
        "partial traffic loss",
        "queue saturation",
        "database saturation",
        "extreme concurrency",
        "partial event loss",
        "event duplication",
        "out-of-order events",
        "abrupt shutdown mid-operation",
    ):
        assert needle in names, needle


def test_every_scenario_declares_blast_radius_and_evidence() -> None:
    for s in SCENARIOS:
        assert s.id.startswith("CHAOS-")
        assert s.injection and s.expected_signal
        assert s.blast_radius and s.evidence_required


def test_list_scenarios_is_serializable() -> None:
    import json

    out = list_scenarios()
    assert json.dumps(out)  # raises if not serializable
    assert out[0]["id"] == "CHAOS-001"


def test_dispatch_verb(tmp_path) -> None:
    from apiforge.dispatch.runner import DispatchContext, dispatch_step

    step = dispatch_step("perf chaos", DispatchContext(case=tmp_path))
    assert step["status"] == "ran"
