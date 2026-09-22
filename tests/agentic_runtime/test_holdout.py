from pathlib import Path

from apiforge.verification.holdout import run_holdouts


def test_declared_mutations_are_detected(
    tmp_path: Path, orders_paths: dict[str, Path]
) -> None:
    records = run_holdouts(
        tmp_path,
        orders_paths["project"],
        orders_paths["contract"],
        orders_paths["manifest"],
    )
    assert len(records) == 3
    assert all(record.detected for record in records)
