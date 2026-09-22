from pathlib import Path

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
