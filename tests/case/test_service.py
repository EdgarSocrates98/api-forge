import json
import os
from pathlib import Path

import pytest

from apiforge.case.models import CasePayload
from apiforge.case.service import (
    CaseIntegrityError,
    CaseStorageError,
    load_case,
    save_case,
)


def test_case_manifest_links_all_artifacts(tmp_path: Path, case_payload: CasePayload) -> None:
    manifest = save_case(tmp_path / "case", case_payload)
    out = tmp_path / "case"
    assert (out / "case.json").exists()
    assert (out / "api-ir.json").exists()
    assert (out / "facts.json").exists()
    assert (out / "findings.json").exists()
    assert manifest.artifacts["api_ir"].sha256
    assert load_case(out) == manifest


def test_case_is_byte_reproducible(tmp_path: Path, case_payload: CasePayload) -> None:
    first = save_case(tmp_path / "one", case_payload)
    second = save_case(tmp_path / "two", case_payload)
    assert first.case_id == second.case_id
    for name in ("api-ir.json", "facts.json", "findings.json", "case.json"):
        assert (tmp_path / "one" / name).read_bytes() == (tmp_path / "two" / name).read_bytes()


def test_changes_json_written_only_when_changes_exist(
    tmp_path: Path, case_payload: CasePayload
) -> None:
    manifest = save_case(tmp_path / "nochg", case_payload)
    assert "changes" not in manifest.artifacts
    assert not (tmp_path / "nochg" / "changes.json").exists()


def test_manifest_counts(tmp_path: Path, case_payload: CasePayload) -> None:
    manifest = save_case(tmp_path / "counts", case_payload)
    assert manifest.diagnostics_count == 1
    assert manifest.finding_counts["status:confirmed"] == 1
    assert manifest.finding_counts["severity:high"] == 1


def test_tampered_artifact_fails_load(tmp_path: Path, case_payload: CasePayload) -> None:
    save_case(tmp_path / "tampered", case_payload)
    target = tmp_path / "tampered" / "findings.json"
    target.write_text(json.dumps({"findings": []}), encoding="utf-8")
    with pytest.raises(CaseIntegrityError, match="AF-CASE-HASH-MISMATCH"):
        load_case(tmp_path / "tampered")


def test_missing_artifact_fails_load(tmp_path: Path, case_payload: CasePayload) -> None:
    save_case(tmp_path / "missing", case_payload)
    (tmp_path / "missing" / "facts.json").unlink()
    with pytest.raises(CaseIntegrityError):
        load_case(tmp_path / "missing")


def test_out_dir_traversal_refused(case_payload: CasePayload) -> None:
    with pytest.raises(CaseStorageError, match="AF-CASE-PATH-TRAVERSAL"):
        save_case(Path("..") / "escape", case_payload)


def test_out_dir_symlink_refused(tmp_path: Path, case_payload: CasePayload) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    try:
        os.symlink(real, link)
    except OSError:
        pytest.skip("symlinks unavailable")
    with pytest.raises(CaseStorageError, match="AF-CASE-SYMLINK"):
        save_case(link, case_payload)


def test_out_dir_inside_input_project_refused(tmp_path: Path, case_payload: CasePayload) -> None:
    nested = Path(case_payload.project_path) / ".apiforge"
    with pytest.raises(CaseStorageError, match="AF-CASE-INPUT-OUTPUT-OVERLAP"):
        save_case(nested, case_payload)


def test_out_dir_containing_input_refused(tmp_path: Path, case_payload: CasePayload) -> None:
    parent = Path(case_payload.project_path).parent
    with pytest.raises(CaseStorageError, match="AF-CASE-INPUT-OUTPUT-OVERLAP"):
        save_case(parent, case_payload)
