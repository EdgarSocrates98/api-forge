import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app

runner = CliRunner()


def test_policy_check_json() -> None:
    result = runner.invoke(
        app,
        ["policy", "check", "--verb", "fs.delete", "--action-class", "destructive"],
    )
    assert result.exit_code == 0
    decision = json.loads(result.stdout)
    assert decision["outcome"] in {"gate", "deny"}
    assert decision["missing_requirements"]


def test_policy_check_read_only_allowed() -> None:
    result = runner.invoke(
        app,
        ["policy", "check", "--verb", "fs.read", "--action-class", "read_only"],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["outcome"] == "allow"


def test_policy_check_ambiguous_class_denied() -> None:
    result = runner.invoke(app, ["policy", "check", "--verb", "fs.read"])
    assert result.exit_code == 3
    assert json.loads(result.stdout)["outcome"] == "deny"


def test_sdd_check_on_fixture_root() -> None:
    result = runner.invoke(app, ["sdd", "check", "--root", "tests/fixtures/sdd_root"])
    report = json.loads(result.stdout)
    assert report["ok"] is False
    assert result.exit_code == 3


def test_sdd_status_lists_features() -> None:
    result = runner.invoke(app, ["sdd", "status", "--root", "tests/fixtures/sdd_root"])
    assert result.exit_code == 0
    assert "GAPPED_FEATURE" in json.loads(result.stdout)["features"]


def test_evidence_emit_and_verify(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    (case / "facts.json").write_text("{}", encoding="utf-8")
    import hashlib

    digest = hashlib.sha256(b"{}").hexdigest()
    manifest = {
        "schema_version": "1",
        "artifacts": {"facts": {"path": "facts.json", "sha256": digest}},
    }
    (case / "case.json").write_text(json.dumps(manifest), encoding="utf-8")
    receipt_path = tmp_path / "receipt.json"
    emit = runner.invoke(
        app,
        ["evidence", "emit", "--case", str(case), "--out", str(receipt_path)],
    )
    assert emit.exit_code == 0
    verify = runner.invoke(app, ["evidence", "verify", "--receipt", str(receipt_path)])
    assert verify.exit_code == 0
    assert json.loads(verify.stdout)["ok"] is True


def test_sandbox_apply_via_cli(tmp_path: Path) -> None:
    import shutil

    project = tmp_path / "project"
    shutil.copytree("tests/fixtures/fastapi_flat", project)
    diff_file = tmp_path / "change.diff"
    from tests.sandbox.diffs import DIFF_ADDING_ROUTE

    diff_file.write_text(DIFF_ADDING_ROUTE, encoding="utf-8")
    result = runner.invoke(
        app,
        [
            "sandbox",
            "apply",
            "--root",
            str(project),
            "--diff",
            str(diff_file),
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["applied"] is True
