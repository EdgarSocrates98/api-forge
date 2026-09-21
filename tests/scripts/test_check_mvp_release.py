from pathlib import Path

from scripts.check_mvp_release import check_repository


def test_release_gate_accepts_complete_repository() -> None:
    failures = check_repository(Path(__file__).resolve().parents[2])
    assert failures == []
