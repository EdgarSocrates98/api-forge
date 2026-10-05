"""Governor decision commands: §23-§27 control-plane primitives.

Every verb is a pure evaluation over declared inputs — nothing here spends
budget, spawns an agent or mutates a run. Ceilings, gain scores, stop and
recovery decisions come back as versioned contracts; unresolved inputs are
named, never guessed.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer

if TYPE_CHECKING:
    from apiforge.contracts.agentic_governance import GainAction


def _payload(value: str) -> dict[str, Any]:
    """JSON string or path to a JSON file."""
    path = Path(value)
    raw = path.read_text(encoding="utf-8") if path.is_file() else value
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"value": data}


def _gain_action(value: str) -> GainAction:
    """Validate an action name against the closed literal — refuses typos."""
    from typing import get_args

    from apiforge.contracts.agentic_governance import GainAction

    allowed = get_args(GainAction)
    if value not in allowed:
        from apiforge.economy.run_ledger import EconomyError

        raise EconomyError(
            "AF-GOV-ACTION-INVALID",
            f"unknown gain action {value!r}; allowed: {sorted(allowed)}",
            field="action",
            unlock="pass one of the §24 action names",
        )
    return value  # type: ignore[return-value]


def register(governor_app: typer.Typer) -> None:
    @governor_app.command("decide")
    def governor_decide(
        inputs: str = typer.Option(..., "--inputs", help="GovernorInputs JSON or file."),
        policy: Path | None = typer.Option(None, "--policy"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§23: profile ceilings adjusted by risk, security and budget."""
        from apiforge.cli import _echo_json, _run
        from apiforge.contracts.agentic_governance import GovernorInputs
        from apiforge.governance.governor import govern, load_governor_policy

        def work() -> dict[str, object]:
            declared = GovernorInputs.model_validate(_payload(inputs))
            rules = load_governor_policy(policy) if policy else None
            return govern(declared, rules).model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @governor_app.command("gain")
    def governor_gain(
        action: str = typer.Option(
            ...,
            "--action",
            help="spawn_agent|call_reviewer|start_debate|expand_context|expensive_retrieval",
        ),
        signals: str = typer.Option(..., "--signals", help="JSON map of §24 signals."),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§24: pre-action expected information gain over declared signals."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.gain import expected_gain

        def work() -> dict[str, object]:
            raw = _payload(signals)
            parsed = {key: None if v is None else float(v) for key, v in raw.items()}
            return expected_gain(action=_gain_action(action), signals=parsed).model_dump(
                mode="json"
            )

        _echo_json(_run(work), detail_level)

    @governor_app.command("stop")
    def governor_stop(
        action: str = typer.Option(..., "--action"),
        signals: str = typer.Option(..., "--signals"),
        mandatory: bool = typer.Option(False, "--mandatory"),
        threshold: float = typer.Option(0.33, "--threshold"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§25: explicit STOP — continue only on gain > threshold or requirement."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.gain import expected_gain
        from apiforge.governance.stop import decide_stop

        def work() -> dict[str, object]:
            raw = _payload(signals)
            parsed = {key: None if v is None else float(v) for key, v in raw.items()}
            gain = expected_gain(action=_gain_action(action), signals=parsed)
            return decide_stop(
                gain, mandatory_requirement=mandatory, threshold=threshold
            ).model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @governor_app.command("recover")
    def governor_recover(
        failure_class: str = typer.Option(..., "--failure-class"),
        attempt: int = typer.Option(0, "--attempt"),
        policy: Path | None = typer.Option(None, "--policy"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§26: governed recovery for a classified failure."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.recovery import decide_recovery, load_recovery_policy

        def work() -> dict[str, object]:
            rules = load_recovery_policy(policy) if policy else None
            return decide_recovery(failure_class, attempt, rules).model_dump(mode="json")

        _echo_json(_run(work), detail_level)

    @governor_app.command("loop-check")
    def governor_loop_check(
        fingerprints: str = typer.Option(
            ..., "--fingerprints", help="JSON list of strategy fingerprints."
        ),
        window: int = typer.Option(5, "--window"),
        max_repeats: int = typer.Option(2, "--max-repeats"),
        detail_level: str = typer.Option("normal", "--detail-level"),
    ) -> None:
        """§27: block a strategy that repeats inside the trailing window."""
        from apiforge.cli import _echo_json, _run
        from apiforge.governance.loop import check_loop

        def work() -> dict[str, object]:
            raw = json.loads(fingerprints)
            items = raw if isinstance(raw, list) else list(_payload(fingerprints).values())
            return check_loop(
                [str(item) for item in items],
                window=window,
                max_repeats=max_repeats,
            ).model_dump(mode="json")

        _echo_json(_run(work), detail_level)


__all__ = ["register"]
