import json
from pathlib import Path

import pytest

from apiforge.core.io import read_json, sha256_file, write_json
from apiforge.core.models import Diagnostic, FindingStatus


def test_write_json_is_byte_stable(tmp_path: Path) -> None:
    target = tmp_path / "value.json"
    write_json(target, {"z": 1, "a": [2, 1]})
    first = target.read_bytes()
    write_json(target, {"a": [2, 1], "z": 1})
    assert target.read_bytes() == first
    assert first.endswith(b"\n")


def test_sha256_changes_with_content(tmp_path: Path) -> None:
    target = tmp_path / "input"
    target.write_text("one", encoding="utf-8")
    first = sha256_file(target)
    target.write_text("two", encoding="utf-8")
    assert sha256_file(target) != first


def test_write_json_serializes_models_and_creates_parents(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "deep" / "diag.json"
    diagnostic = Diagnostic(
        code="AF-TEST",
        status=FindingStatus.UNRESOLVED,
        message="payload",
        details={"b": 2, "a": 1},
    )
    write_json(target, diagnostic)
    assert read_json(target) == {
        "code": "AF-TEST",
        "status": "unresolved",
        "message": "payload",
        "source": None,
        "details": {"a": 1, "b": 2},
    }


def test_write_json_leaves_no_temp_file(tmp_path: Path) -> None:
    target = tmp_path / "out.json"
    write_json(target, {"a": 1})
    assert sorted(p.name for p in tmp_path.iterdir()) == ["out.json"]


def test_read_json_round_trips_utf8(tmp_path: Path) -> None:
    target = tmp_path / "utf8.json"
    write_json(target, {"texto": "análise"})
    assert target.read_bytes().find("análise".encode()) != -1
    assert read_json(target) == {"texto": "análise"}


def test_read_json_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_json(tmp_path / "absent.json")


def test_sha256_streams_large_files(tmp_path: Path) -> None:
    target = tmp_path / "big.bin"
    target.write_bytes(b"x" * (2 * 1024 * 1024 + 7))
    digest = sha256_file(target)
    assert len(digest) == 64
    assert digest == __import__("hashlib").sha256(target.read_bytes()).hexdigest()


def test_read_json_returns_plain_types(tmp_path: Path) -> None:
    target = tmp_path / "plain.json"
    target.write_text(json.dumps({"k": [1, 2]}), encoding="utf-8")
    assert read_json(target) == {"k": [1, 2]}
