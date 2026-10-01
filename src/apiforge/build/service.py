"""Orchestrate a build: decide -> synthesize -> sandbox -> (optional) promote."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from apiforge.adapters.spring.extractor import extract_spring
from apiforge.api_ir.builder import build_api_model
from apiforge.build.diff import sources_to_diff
from apiforge.build.java import BuildError, operation_to_sources
from apiforge.openapi.loader import load_openapi
from apiforge.openapi.models import OpenApiDocument
from apiforge.policy.decide import ActionRequest, decide
from apiforge.policy.loader import DEFAULT_POLICY
from apiforge.policy.models import Policy
from apiforge.rules.judge import judge_api_model
from apiforge.sandbox.service import Analyze, sandbox_apply
from apiforge.sandbox.worktree import WorktreeError, worktree_create


def _judge_side(document: OpenApiDocument) -> Analyze:
    def analyze(root: Path) -> list[dict[str, Any]]:
        inventory = extract_spring(root)
        model = build_api_model(document, inventory)
        return [f.model_dump(mode="json") for f in judge_api_model(model)]

    return analyze


def _refusal(code: str, detail: str) -> dict[str, Any]:
    return {
        "applied": False,
        "refused": [{"code": code, "detail": detail}],
        "files": [],
        "sandbox": None,
        "decision": None,
        "promotion": None,
        "receipt": None,
    }


def _receipt(
    contract_sha: str, diff_sha: str, sandbox_id: Any, decision: Any, promote: Any
) -> dict[str, Any]:
    return {
        "contract_sha256": contract_sha,
        "diff_sha256": diff_sha,
        "sandbox_id": sandbox_id,
        "policy": decision,
        "promotion": promote,
    }


def build_endpoint(
    contract: Path,
    project: Path,
    operation_id: str,
    *,
    policy: Policy = DEFAULT_POLICY,
    promote: str | None = None,
    approve: bool = False,
) -> dict[str, Any]:
    """Build one endpoint skeleton; the main tree is never touched."""
    project = Path(project)
    decision = decide(
        policy,
        ActionRequest(
            verb="build.endpoint",
            autonomy_class="local_reversible",
            target=str(project),
        ),
    )
    if decision.outcome != "allow":
        report = _refusal(
            decision.reason_code or "AF-POLICY-GATE",
            f"build.endpoint {decision.outcome}: {decision.missing_requirements}",
        )
        report["decision"] = decision.model_dump(mode="json")
        return report

    document = load_openapi(contract)
    try:
        sources = operation_to_sources(document, operation_id)
    except BuildError as exc:
        return _refusal(exc.code, exc.detail)

    collisions = [p for p in sources if (project / p).exists()]
    if collisions:
        return _refusal(
            "AF-BUILD-TARGET-EXISTS",
            f"generated paths already present: {sorted(collisions)}",
        )

    diff_text = sources_to_diff(sources)
    diff_sha = hashlib.sha256(diff_text.encode("utf-8")).hexdigest()
    sandbox = sandbox_apply(project, diff_text, _judge_side(document))

    promotion: dict[str, Any] | None = None
    if promote is not None:
        promotion = _promote(project, promote, sources, approve, sandbox.get("id"), policy)

    return {
        "applied": bool(sandbox.get("applied")),
        "refused": sandbox.get("refused", []),
        "files": sorted(sources),
        "sandbox": {
            "id": sandbox.get("id"),
            "delta": {
                "new": sandbox.get("new", []),
                "resolved": sandbox.get("resolved", []),
                "kept_count": sandbox.get("kept_count", 0),
            },
        },
        "decision": decision.model_dump(mode="json"),
        "promotion": promotion,
        "receipt": _receipt(
            document.sha256,
            diff_sha,
            sandbox.get("id"),
            decision.model_dump(mode="json"),
            promotion,
        ),
    }


def _promote(
    project: Path,
    name: str,
    sources: dict[str, str],
    approve: bool,
    sandbox_id: Any,
    policy: Policy,
) -> dict[str, Any]:
    detail = {"evidence": str(sandbox_id or "")}
    if approve:
        detail["approval"] = "cli:--approve"
    decision = decide(
        policy,
        ActionRequest(
            verb="worktree.apply",
            autonomy_class="sensitive",
            target=name,
            detail=detail,
        ),
    )
    if decision.outcome != "allow":
        return {
            "applied": False,
            "decision": decision.model_dump(mode="json"),
            "refused": [
                {
                    "code": decision.reason_code or "AF-POLICY-GATE",
                    "detail": f"worktree.apply gated; missing {decision.missing_requirements}",
                    "unlock": "pass --approve to record approval evidence",
                }
            ],
        }
    try:
        worktree = worktree_create(project, name)
    except WorktreeError as exc:
        return {
            "applied": False,
            "decision": decision.model_dump(mode="json"),
            "refused": [{"code": exc.code, "detail": exc.detail}],
        }
    wt_root = Path(worktree["path"])
    written: list[str] = []
    for rel, content in sorted(sources.items()):
        dest = wt_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        written.append(rel)
    return {
        "applied": True,
        "decision": decision.model_dump(mode="json"),
        "worktree": worktree,
        "files_written": written,
    }
