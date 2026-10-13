from pathlib import Path

from apiforge.contracts.agentic import AgenticRun, AgenticState, TrajectoryEvent
from apiforge.governance.loop import strategy_fingerprint
from apiforge.runtime.store import RunStore
from apiforge.runtime.supervisor import _record_strategy


def test_replay_normalizes_volatile_fields(tmp_path: Path) -> None:
    store = RunStore(tmp_path, "task", "run:abc")
    store.event(
        type(
            "Event",
            (),
            {
                "model_dump": lambda self, mode: {
                    "event_id": "e",
                    "created_at": "now",
                    "run_id": "run:abc",
                    "event": "created",
                    "actor": "test",
                }
            },
        )()
    )
    replay = store.replay()
    assert replay["events"][0]["event"] == "created"
    assert "created_at" not in replay["events"][0]


def test_store_reuses_typed_run_projection(tmp_path: Path) -> None:
    store = RunStore(tmp_path, "task", "run:typed")
    run = AgenticRun(
        run_id="run:typed",
        task_id="task",
        revision=1,
        state=AgenticState.RUNNING,
        policy_id="local-ci-safe",
        started_at="2026-09-23T00:00:00Z",
    )
    store.save_run(run)
    assert store.load_run() == run


def test_runtime_records_strategy_history_and_blocks_before_work(tmp_path: Path) -> None:
    store = RunStore(tmp_path, "task", "run:loop")
    strategy_a = {"primary": "a", "fallbacks": (), "execution_mode": "sequential", "parallel": 1}
    strategy_b = {"primary": "b", "fallbacks": (), "execution_mode": "sequential", "parallel": 1}

    first = _record_strategy(store, "run:loop", strategy_a, "2026-10-05T12:00:00Z")
    second = _record_strategy(store, "run:loop", strategy_b, "2026-10-05T12:00:01Z")
    third = _record_strategy(store, "run:loop", strategy_a, "2026-10-05T12:00:02Z")
    blocked = _record_strategy(store, "run:loop", strategy_a, "2026-10-05T12:00:03Z")

    assert not first.blocked
    assert not second.blocked
    assert not third.blocked
    assert blocked.blocked
    assert blocked.code == "AF-GOV-LOOP-DETECTED"
    assert store.strategy_history() == (
        strategy_fingerprint(strategy_a),
        strategy_fingerprint(strategy_b),
        strategy_fingerprint(strategy_a),
        strategy_fingerprint(strategy_a),
    )


def test_strategy_history_rejects_malformed_strategy_event(tmp_path: Path) -> None:
    store = RunStore(tmp_path, "task", "run:bad-loop")
    store.event(
        TrajectoryEvent(
            event_id="event:bad",
            run_id="run:bad-loop",
            event="strategy_selected",
            actor="test",
            payload={"strategy": {}},
            created_at="2026-10-05T12:00:00Z",
        )
    )

    try:
        store.strategy_history()
    except ValueError as exc:
        assert str(exc).startswith("AF-RUNTIME-LOOP-HISTORY")
    else:
        raise AssertionError("malformed strategy history must fail closed")
