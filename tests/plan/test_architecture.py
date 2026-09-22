"""Architecture Decision Engine — WorkloadProfile -> ranked, evidenced pick."""

from __future__ import annotations

from apiforge.contracts.stubs import WorkloadProfile
from apiforge.plan.architecture import recommend


def _chosen(out: dict, role: str) -> dict:
    return next(c for c in out["chosen"] if c["role"] == role)


def _rejected(out: dict, candidate: str) -> dict | None:
    return next(
        (r for r in out["rejected"] if r["candidate"] == candidate), None
    )


def test_kubernetes_need_picks_eks_and_names_reason() -> None:
    out = recommend(WorkloadProfile(id="w", needs_kubernetes=True, team_maturity="high"))
    assert _chosen(out, "compute")["candidate"] == "eks"
    for name in ("lambda", "ecs-fargate", "ecs-ec2", "ec2"):
        rej = _rejected(out, name)
        assert rej is not None and "Kubernetes" in rej["reason"]


def test_lambda_disqualified_over_900s() -> None:
    out = recommend(WorkloadProfile(id="w", max_request_duration_s=1200))
    rej = _rejected(out, "lambda")
    assert rej is not None and "900s" in rej["reason"]
    assert any("max_request_duration_s" in c for c in out["change_conditions"])


def test_no_eks_for_power_low_maturity_penalizes() -> None:
    out = recommend(WorkloadProfile(id="w", team_maturity="low"))
    # low maturity x ops 4 sinks EKS/EC2 below serverless options
    assert _chosen(out, "compute")["candidate"] == "lambda"


def test_os_control_picks_control_planes() -> None:
    out = recommend(WorkloadProfile(id="w", needs_os_control=True))
    assert _chosen(out, "compute")["candidate"] in {"ecs-ec2", "ec2"}
    rej = _rejected(out, "lambda")
    assert rej is not None and "OS" in rej["reason"]


def test_private_exposure_rejects_public_edge() -> None:
    out = recommend(WorkloadProfile(id="w", exposure="private"))
    for name in ("api-gateway-rest", "api-gateway-http", "cloudfront"):
        assert _rejected(out, name) is not None
    assert _chosen(out, "edge")["candidate"] in {"alb", "api-gateway-websocket"}
    assert not out["adjuncts"]  # WAF only on public


def test_public_exposure_adds_waf_adjunct() -> None:
    out = recommend(WorkloadProfile(id="w", exposure="public"))
    assert out["adjuncts"][0]["candidate"] == "waf"


def test_async_role_skipped_without_signal() -> None:
    out = recommend(WorkloadProfile(id="w", timing="synchronous"))
    assert "async" not in out["roles_evaluated"]


def test_event_driven_evaluates_async() -> None:
    out = recommend(WorkloadProfile(id="w", event_driven=True))
    assert "async" in out["roles_evaluated"]


def test_streaming_favors_msk() -> None:
    out = recommend(WorkloadProfile(id="w", streaming=True, team_maturity="high"))
    assert _chosen(out, "async")["candidate"] == "msk"


def test_no_datastore_without_data_model() -> None:
    out = recommend(WorkloadProfile(id="w"))
    rej = next(
        r for r in out["rejected"] if r["role"] == "data"
    )
    assert rej["candidate"] == "(all)"
    assert "data_model not declared" in rej["reason"]


def test_graph_model_picks_neptune() -> None:
    out = recommend(WorkloadProfile(id="w", data_model="graph"))
    assert _chosen(out, "data")["candidate"] == "neptune"
    assert _rejected(out, "dynamodb") is not None


def test_websocket_needs_streaming_signal() -> None:
    out = recommend(WorkloadProfile(id="w", exposure="public"))
    rej = _rejected(out, "api-gateway-websocket")
    assert rej is not None


def test_premises_list_declared_fields_only() -> None:
    out = recommend(
        WorkloadProfile(id="w", timing="synchronous", exposure="private")
    )
    assert set(out["premises"]) == {"exposure", "timing"}
    assert "cost was never measured" in " ".join(out["risks"])
    assert out["cost_to_validate"]


def test_deterministic_output() -> None:
    profile = WorkloadProfile(id="w", 
        event_driven=True, data_model="key-value", exposure="public"
    )
    assert recommend(profile) == recommend(profile)
