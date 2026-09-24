from pathlib import Path

from apiforge.contracts.agentic import AgenticRun, AgenticState
from apiforge.runtime.store import RunStore


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
