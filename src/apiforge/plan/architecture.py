"""Architecture Decision Engine — WorkloadProfile -> ranked recommendation.

Every trait in ``CANDIDATES`` is *declared data* about the AWS primitive
(published service limits and model), never measured. The engine only
eliminates on hard constraints the profile declares; scoring ranks the
survivors. Nothing recommends EKS for power, Lambda for serverless-ness,
or EC2 for control — each winner names the profile fields that chose it,
and every rejection names the field that caused it.

Cost is never a number here: ``cost_to_validate`` names what a later
measurement must answer.
"""

from __future__ import annotations

from typing import Any

from apiforge.contracts.stubs import WorkloadProfile

# role groups — an architecture is a composition, not one winner
_CANDIDATES: dict[str, dict[str, Any]] = {
    # edge
    "api-gateway-rest": {
        "role": "edge",
        "ops": 1,
        "traits": {"protocols": ["https"], "payload_limit_bytes": 10_485_760},
        "disqualify": {"exposure_private": "REST/HTTP APIs are public edge; use privateLink/internal ALB"},
    },
    "api-gateway-http": {
        "role": "edge",
        "ops": 1,
        "traits": {"protocols": ["https"], "payload_limit_bytes": 10_485_760},
        "disqualify": {"exposure_private": "public edge only"},
    },
    "api-gateway-websocket": {
        "role": "edge",
        "ops": 2,
        "traits": {"protocols": ["websocket"]},
        "disqualify": {},
    },
    "alb": {
        "role": "edge",
        "ops": 2,
        "traits": {"protocols": ["https"], "internal": True},
        "disqualify": {},
    },
    "cloudfront": {
        "role": "edge",
        "ops": 1,
        "traits": {"global": True},
        "disqualify": {"exposure_private": "CloudFront is a public edge"},
    },
    # compute
    "lambda": {
        "role": "compute",
        "ops": 1,
        "traits": {"cold_start": True, "max_duration_s": 900, "serverless": True},
        "disqualify": {
            "duration": "request exceeds the 900s execution limit",
            "os_control": "no OS access",
            "kubernetes": "not a Kubernetes primitive",
        },
    },
    "ecs-fargate": {
        "role": "compute",
        "ops": 2,
        "traits": {"serverless": True, "containers": True},
        "disqualify": {
            "os_control": "no host OS access",
            "kubernetes": "not a Kubernetes primitive",
        },
    },
    "ecs-ec2": {
        "role": "compute",
        "ops": 3,
        "traits": {"containers": True, "os_control": True},
        "disqualify": {"kubernetes": "not a Kubernetes primitive"},
    },
    "eks": {
        "role": "compute",
        "ops": 4,
        "traits": {"containers": True, "kubernetes": True},
        "disqualify": {},
    },
    "ec2": {
        "role": "compute",
        "ops": 4,
        "traits": {"os_control": True},
        "disqualify": {"kubernetes": "not a Kubernetes primitive"},
    },
    # async
    "sqs": {
        "role": "async",
        "ops": 1,
        "traits": {"pattern": "queue", "serverless": True},
        "disqualify": {},
    },
    "sns": {
        "role": "async",
        "ops": 1,
        "traits": {"pattern": "pubsub", "serverless": True},
        "disqualify": {},
    },
    "eventbridge": {
        "role": "async",
        "ops": 1,
        "traits": {"pattern": "eventbus", "serverless": True},
        "disqualify": {},
    },
    "step-functions": {
        "role": "async",
        "ops": 2,
        "traits": {"pattern": "orchestration", "serverless": True},
        "disqualify": {},
    },
    "msk": {
        "role": "async",
        "ops": 4,
        "traits": {"pattern": "streaming", "kafka": True},
        "disqualify": {},
    },
    # data
    "dynamodb": {
        "role": "data",
        "ops": 1,
        "traits": {"models": ["key-value", "document"], "serverless": True},
        "disqualify": {},
    },
    "documentdb": {
        "role": "data",
        "ops": 3,
        "traits": {"models": ["document"]},
        "disqualify": {},
    },
    "neptune": {
        "role": "data",
        "ops": 3,
        "traits": {"models": ["graph"]},
        "disqualify": {},
    },
    "elasticache": {
        "role": "data",
        "ops": 2,
        "traits": {"models": ["cache", "key-value"]},
        "disqualify": {},
    },
}

_ROLES_FOR_PROFILE: dict[str, str] = {
    "edge": "exposure or timing declared",
    "compute": "always evaluated",
    "async": "timing asynchronous, event_driven, batch or streaming",
    "data": "data_model declared",
}


def _disqualifies(name: str, profile: WorkloadProfile) -> str | None:
    meta = _CANDIDATES[name]
    disq: dict[str, str] = meta["disqualify"]
    if "exposure_private" in disq and profile.exposure == "private":
        return disq["exposure_private"]
    if "duration" in disq and (
        profile.max_request_duration_s is not None
        and profile.max_request_duration_s > meta["traits"].get("max_duration_s", float("inf"))
    ):
        return disq["duration"]
    if "os_control" in disq and profile.needs_os_control:
        return disq["os_control"]
    if "kubernetes" in disq and profile.needs_kubernetes:
        return disq["kubernetes"]
    if name == "api-gateway-websocket" and not profile.streaming:
        return "no streaming/websocket need declared"
    if (
        meta["role"] == "data"
        and profile.data_model is not None
        and profile.data_model not in meta["traits"].get("models", ())
    ):
        return f"declared data_model {profile.data_model!r} not served"
    return None


def _score(name: str, profile: WorkloadProfile) -> tuple[int, list[str]]:
    """Higher is better; every point names the profile field that earned it."""
    meta = _CANDIDATES[name]
    score, reasons = 0, []
    ops = int(meta["ops"])
    maturity_penalty = {"low": 2, "medium": 1, "high": 0}.get(
        profile.team_maturity or "medium", 1
    )
    ops_delta = -ops * maturity_penalty
    if ops_delta:
        score += ops_delta
        reasons.append(f"ops complexity {ops} x maturity {profile.team_maturity or 'medium'}")
    traits = meta["traits"]
    if profile.latency_sensitive and traits.get("cold_start"):
        score -= 3
        reasons.append("latency-sensitive vs cold start")
    if profile.needs_kubernetes and traits.get("kubernetes"):
        score += 5
        reasons.append("needs_kubernetes")
    if profile.needs_os_control and traits.get("os_control"):
        score += 5
        reasons.append("needs_os_control")
    if profile.scope == "global" and traits.get("global"):
        score += 3
        reasons.append("global scope")
    if profile.streaming and meta["traits"].get("pattern") == "streaming":
        score += 5
        reasons.append("streaming workload")
    if profile.event_driven and meta["role"] == "async":
        score += 3
        reasons.append("event_driven")
    if profile.batch and traits.get("pattern") == "orchestration":
        score += 3
        reasons.append("batch orchestration")
    if profile.throughput_sensitive and traits.get("serverless"):
        score += 2
        reasons.append("serverless absorbs variable throughput")
    return score, reasons


def recommend(profile: WorkloadProfile) -> dict[str, Any]:
    """Rank candidates per role; every output field names its evidence."""
    envelope = {"id", "produced_by", "unresolved", "attributes", "version", "subject"}
    declared = {
        k: v
        for k, v in profile.model_dump(mode="json").items()
        if v is not None and k not in envelope
    }
    chosen: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    change_conditions: list[str] = []

    for role in ("edge", "compute", "async", "data"):
        if role == "async" and not (
            profile.timing == "asynchronous"
            or profile.event_driven
            or profile.batch
            or profile.streaming
        ):
            continue
        if role == "data" and profile.data_model is None:
            rejected.append(
                {
                    "role": "data",
                    "candidate": "(all)",
                    "reason": "data_model not declared — no datastore recommended on absence",
                }
            )
            continue
        survivors: list[tuple[int, str, list[str]]] = []
        for name, meta in _CANDIDATES.items():
            if meta["role"] != role:
                continue
            reason = _disqualifies(name, profile)
            if reason:
                rejected.append({"role": role, "candidate": name, "reason": reason})
                if name == "lambda" and "duration" in meta["disqualify"]:
                    change_conditions.append(
                        "lambda becomes eligible if max_request_duration_s <= 900"
                    )
            else:
                score, reasons = _score(name, profile)
                survivors.append((score, name, reasons))
        if not survivors:
            rejected.append(
                {"role": role, "candidate": "(all)", "reason": "every candidate disqualified"}
            )
            continue
        survivors.sort(key=lambda s: (-s[0], s[1]))
        top_score, top_name, top_reasons = survivors[0]
        chosen.append(
            {
                "role": role,
                "candidate": top_name,
                "score": top_score,
                "decided_by": top_reasons,
            }
        )
        for score, name, _reasons in survivors[1:]:
            rejected.append(
                {
                    "role": role,
                    "candidate": name,
                    "reason": f"outscored by {top_name} ({top_score} vs {score})",
                }
            )

    adjuncts: list[dict[str, str]] = []
    if profile.exposure == "public":
        adjuncts.append(
            {
                "candidate": "waf",
                "role": "edge-attachment",
                "reason": "public exposure — attach to the chosen edge; never a standalone layer",
            }
        )

    premises = sorted(declared)
    return {
        "workload_subject": profile.subject or None,
        "chosen": chosen,
        "adjuncts": adjuncts,
        "rejected": rejected,
        "premises": premises,
        "trade_offs": [
            f"{c['candidate']}: {', '.join(c['decided_by']) or 'default ranking'}"
            for c in chosen
        ],
        "risks": [
            "traits are declared service data, not measured — validate against the account's limits",
            "cost was never measured; see cost_to_validate",
        ],
        "cost_to_validate": [
            f"{c['candidate']}: price the declared workload shape, not a generic tier"
            for c in chosen
        ],
        "evidence": {"declared_profile_fields": premises},
        "change_conditions": sorted(set(change_conditions))
        or ["any newly declared profile field can reorder survivors"],
        "roles_evaluated": [c["role"] for c in chosen],
    }
