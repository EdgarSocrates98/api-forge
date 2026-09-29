import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.contracts.field import FieldRun
from apiforge.field.errors import EXPORT_LEAK, FieldError
from apiforge.field.export import export
from apiforge.field.store import save_run
from apiforge.mcp import tools
from tests.field.support import (
    ENDED,
    EXECUTOR,
    HUMAN,
    OWN,
    STARTED,
    VERIFIER,
    corpus,
    field_run,
    runtime_run,
    task,
    verified,
)

runner = CliRunner()


def _verified(task_id: str, repo_ref: str) -> FieldRun:
    return verified(
        field_run(
            task_id,
            repo_ref=repo_ref,
            run_ids=("r1",),
            task_completed=True,
            exit_reason="graph_gap",
        )
    )


def test_export_writes_anonymized_cases(tmp_path: Path) -> None:
    corpus(tmp_path, tasks=[task("T1", repo_ref=OWN)])
    (tmp_path / "docs" / "field" / "repos.local.yaml").write_text(
        f"'{OWN}':\n  name: acme-payments\n  path: E:/work/acme-payments\n", encoding="utf-8"
    )
    save_run(tmp_path, _verified("T1", OWN))
    out = export(tmp_path)
    assert out["exported"] == 1
    case = json.loads((tmp_path / "evals" / "corpus" / "field" / "T1.json").read_text())
    assert case["repo_ref"] == OWN
    assert case["expected"] == {"task_completed": True, "exit_reason": "graph_gap"}
    assert "acme" not in json.dumps(case)


def test_export_refuses_private_markers(tmp_path: Path) -> None:
    leaky = task("T1", repo_ref=OWN)
    leaky["prompt"] = "fix acme-payments checkout bug"
    corpus(tmp_path, tasks=[leaky])
    (tmp_path / "docs" / "field" / "repos.local.yaml").write_text(
        f"'{OWN}':\n  name: acme-payments\n", encoding="utf-8"
    )
    save_run(tmp_path, _verified("T1", OWN))
    with pytest.raises(FieldError) as exc:
        export(tmp_path)
    assert exc.value.code == EXPORT_LEAK
    assert exc.value.field == "prompt"
    assert "acme" not in str(exc.value)
    assert not (tmp_path / "evals").exists()


def test_export_refuses_absolute_paths(tmp_path: Path) -> None:
    leaky = task("T1")
    leaky["ground_truth"]["ref"] = "C:\\Users\\me\\repo\\fix.patch"
    corpus(tmp_path, tasks=[leaky])
    save_run(tmp_path, _verified("T1", leaky["repo_ref"]))
    with pytest.raises(FieldError) as exc:
        export(tmp_path)
    assert exc.value.field == "ground_truth.ref"


@pytest.mark.parametrize(
    ("cli_args", "mcp_call", "code", "field"),
    [
        (
            [
                "field",
                "record",
                "--task",
                "T999",
                "--run",
                "run-1",
                "--started",
                STARTED,
                "--ended",
                ENDED,
                "--executor",
                EXECUTOR,
            ],
            lambda root: tools.field_record("T999", ["run-1"], STARTED, ENDED, EXECUTOR, root=root),
            "AF-FIELD-TASK-UNREGISTERED",
            "task",
        ),
        (
            ["field", "annotate", "--task", "T001", "--exit-reason", "vibes"],
            lambda root: tools.field_annotate("T001", exit_reason="vibes", root=root),
            "AF-FIELD-ENUM",
            "exit_reason",
        ),
        (
            ["field", "verify", "--task", "T001", "--verdict", "maybe", "--verifier", VERIFIER],
            lambda root: tools.field_verify("T001", "maybe", VERIFIER, root=root),
            "AF-FIELD-ENUM",
            "verdict",
        ),
        (
            ["field", "verify", "--task", "T001", "--verdict", "agree", "--verifier", EXECUTOR],
            lambda root: tools.field_verify("T001", "agree", EXECUTOR, root=root),
            "AF-FIELD-VERIFIER-NOT-INDEPENDENT",
            "verifier",
        ),
        (
            [
                "field",
                "verify",
                "--task",
                "T001",
                "--verdict",
                "agree",
                "--verifier",
                "human:operator-name",
            ],
            lambda root: tools.field_verify("T001", "agree", "human:operator-name", root=root),
            "AF-FIELD-ACTOR-INVALID",
            "verifier",
        ),
        (
            [
                "field",
                "record",
                "--task",
                "T001",
                "--run",
                "run-1",
                "--phase",
                "later",
                "--started",
                STARTED,
                "--ended",
                ENDED,
                "--executor",
                EXECUTOR,
            ],
            lambda root: tools.field_record(
                "T001", ["run-1"], STARTED, ENDED, EXECUTOR, phase="later", root=root
            ),
            "AF-FIELD-ENUM",
            "phase",
        ),
    ],
)
def test_cli_and_mcp_refusals_match(
    tmp_path: Path, monkeypatch, cli_args, mcp_call, code: str, field: str
) -> None:
    monkeypatch.chdir(tmp_path)
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    tools.field_record("T001", ["run-1"], STARTED, ENDED, EXECUTOR, root=str(tmp_path))
    result = runner.invoke(app, [*cli_args, "--root", str(tmp_path)])
    assert result.exit_code == 2, result.output
    assert code in result.output
    assert f"field={field}" in result.output and "unlock=" in result.output
    with pytest.raises(FieldError) as exc:
        mcp_call(str(tmp_path))
    assert (exc.value.code, exc.value.field) == (code, field)
    assert f"unlock={exc.value.unlock}" in " ".join(result.output.split())


def test_cli_and_mcp_report_payloads_match(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    corpus(tmp_path)
    runtime_run(tmp_path, "run-1")
    recorded = tools.field_record("T001", ["run-1"], STARTED, ENDED, EXECUTOR, root=str(tmp_path))
    assert recorded["schema"] == "apiforge/field-run/v2"
    tools.field_verify("T001", "agree", HUMAN, root=str(tmp_path))
    cli = runner.invoke(app, ["field", "report", "--root", str(tmp_path)])
    assert cli.exit_code == 0, cli.output
    assert json.loads(cli.output) == tools.field_report(root=str(tmp_path))
