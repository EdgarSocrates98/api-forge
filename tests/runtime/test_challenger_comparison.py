"""Final-convergence phase 9: champion/challenger comparison receipts.

The challenger runs in shadow and never governs; when it executes beside a
healthy champion the run persists a ``ChallengerComparison/v1`` receipt over
the fields that are actually observable (recommendation, confidence, latency,
tokens, structured correctness) — absent champion or unreported metrics stay
``None`` instead of being invented.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from apiforge.contracts.agentic import AgentArtifact, ArtifactKind
from apiforge.contracts.selective import ChallengerComparison
from apiforge.runtime.adapters import AgentResponse, FakeModelAdapter
from apiforge.runtime.control import ControlPlane
from apiforge.runtime.policy import load_policy
from apiforge.runtime.registry import load_capabilities
from apiforge.runtime.shadow import sampled
from apiforge.runtime.store import RunStore, content_hash
from apiforge.runtime.supervisor import _shadow
from tests.runtime.test_runtime import make_task

_CHAMPION_CAP = "api-architecture-review"
_CHALLENGER_CAP = "api-contract-review"


def _sampled_run_id() -> str:
    return next(candidate for i in range(2000) if sampled(candidate := f"run-{i}", 0.5))


def _economy() -> SimpleNamespace:
    return SimpleNamespace(envelope=SimpleNamespace(shadow_share=0.5, context_bytes=32000))


def _champion_artifact(run_id: str) -> AgentArtifact:
    payload = {"facts": ["f1"], "recommendation": "keep", "confidence": 0.9}
    return AgentArtifact(
        artifact_id="art-champion",
        run_id=run_id,
        invocation_id="inv-champion",
        agent="api-architecture-reviewer",
        capability=_CHAMPION_CAP,
        kind=ArtifactKind.SPECIALIST,
        schema_name="AgentArtifact/v1",
        payload=payload,
        evidence=("f1",),
        confidence=0.9,
        content_sha256=content_hash(payload),
    )


def _invoke(
    tmp_path: Path,
    *,
    adapter: FakeModelAdapter,
    artifacts: list[AgentArtifact],
    primary: str | None = _CHAMPION_CAP,
    champion_response: AgentResponse | None = None,
) -> tuple[object, Path]:
    spec = make_task(tmp_path)
    run_id = _sampled_run_id()
    storage = RunStore(tmp_path, spec.id, run_id)
    control = ControlPlane(tmp_path)
    control_run = control.create(spec.id, (("champion-step", ()),))
    decision = asyncio.run(
        _shadow(
            _economy(),
            (_CHALLENGER_CAP,),
            5,
            artifacts,
            primary,
            load_capabilities(),
            adapter,
            spec,
            run_id,
            storage,
            load_policy("local-ci-safe"),
            {},
            control=control,
            control_run_id=control_run.run_id,
            champion_response=champion_response,
        )
    )
    return decision, storage.directory


def test_challenger_executes_shadow_and_persists_comparison(tmp_path: Path) -> None:
    run_id_artifacts: list[AgentArtifact] = []
    adapter = FakeModelAdapter(
        {
            _CHALLENGER_CAP: {
                "facts": ["fc"],
                "recommendation": "keep",
                "confidence": 0.7,
            }
        }
    )
    # champion artifacts use the sampled run id inside _invoke; build after
    # run creation by pre-seeding through a placeholder run id is brittle, so
    # build the artifact with a deterministic run id ourselves.
    run_id = _sampled_run_id()
    champion = _champion_artifact(run_id)
    run_id_artifacts.append(champion)

    spec = make_task(tmp_path)
    storage = RunStore(tmp_path, spec.id, run_id)
    control = ControlPlane(tmp_path)
    control_run = control.create(spec.id, (("champion-step", ()),))
    decision = asyncio.run(
        _shadow(
            _economy(),
            (_CHALLENGER_CAP,),
            5,
            run_id_artifacts,
            _CHAMPION_CAP,
            load_capabilities(),
            adapter,
            spec,
            run_id,
            storage,
            load_policy("local-ci-safe"),
            {},
            control=control,
            control_run_id=control_run.run_id,
            champion_response=AgentResponse(
                output={"recommendation": "keep", "confidence": 0.9},
                adapter="fake",
                input_tokens=40,
                output_tokens=60,
                duration_ms=120,
            ),
        )
    )

    assert decision.executed is True
    assert decision.agreement is True
    assert decision.comparison_ref is not None
    comparison_path = storage.directory / decision.comparison_ref
    assert comparison_path.is_file()
    comparison = ChallengerComparison.model_validate(
        json.loads(comparison_path.read_text(encoding="utf-8"))
    )
    assert comparison.governs is False
    assert comparison.champion.capability == _CHAMPION_CAP
    assert comparison.challenger.capability == _CHALLENGER_CAP
    # challenger never enters the authoritative result set
    assert [item.capability for item in run_id_artifacts] == [_CHAMPION_CAP]
    # observable metrics only: tokens/latency reported by the fake adapter
    assert comparison.quality_delta == round(0.7 - 0.9, 6)
    assert comparison.challenger.input_tokens is not None
    assert comparison.structured_correctness is True
    assert "quality" in comparison.basis
    assert "structured_correctness" in comparison.basis
    # cost is never invented locally
    assert comparison.cost_delta_usd is None


def test_comparison_skips_when_no_champion(tmp_path: Path) -> None:
    decision, directory = _invoke(tmp_path, adapter=FakeModelAdapter(), artifacts=[], primary=None)
    assert decision.executed is True
    assert decision.agreement is None
    assert decision.comparison_ref is None
    assert not list(directory.glob("challenger-comparison-*.json"))


def test_unreported_metrics_stay_unresolved(tmp_path: Path) -> None:
    class BareAdapter(FakeModelAdapter):
        async def invoke(self, request):  # type: ignore[override]
            self.calls.append(request)
            return AgentResponse(
                output={"facts": ["x"], "recommendation": "keep", "confidence": 0.5},
                adapter="bare",
            )

    run_id = _sampled_run_id()
    champion = _champion_artifact(run_id)
    spec = make_task(tmp_path)
    storage = RunStore(tmp_path, spec.id, run_id)
    control = ControlPlane(tmp_path)
    control_run = control.create(spec.id, (("champion-step", ()),))
    decision = asyncio.run(
        _shadow(
            _economy(),
            (_CHALLENGER_CAP,),
            5,
            [champion],
            _CHAMPION_CAP,
            load_capabilities(),
            BareAdapter(),
            spec,
            run_id,
            storage,
            load_policy("local-ci-safe"),
            {},
            control=control,
            control_run_id=control_run.run_id,
            champion_response=None,
        )
    )
    assert decision.comparison_ref is not None
    comparison = json.loads(
        (storage.directory / decision.comparison_ref).read_text(encoding="utf-8")
    )
    assert comparison["latency_delta_ms"] is None
    assert comparison["token_delta"] is None
    assert "latency" not in comparison["basis"]
    assert "tokens" not in comparison["basis"]
