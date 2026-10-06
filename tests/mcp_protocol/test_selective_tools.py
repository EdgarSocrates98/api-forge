import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.debate.service import open_debate, submit
from apiforge.mcp import tools

runner = CliRunner()
REPO = Path(__file__).resolve().parents[2]


def _cli(*args: str) -> dict[str, object]:
    result = runner.invoke(app, list(args))
    assert result.exit_code == 0, result.output
    return json.loads(result.output)


def test_knowledge_select_parity() -> None:
    intent = "check BOLA on GET /customers/{customer_id}"
    cli = _cli("knowledge", "select", "--intent", intent, "--capability", "api-security-review")
    assert cli == tools.knowledge_select(intent, capability="api-security-review")
    assert [item["pack_id"] for item in cli["selected"]] == ["owasp-api-2023"]


def test_debate_submit_deltas_and_packet_parity(tmp_path: Path) -> None:
    debate = open_debate(tmp_path, "nullable?", ("a", "b"), "2026-09-28T00:00:00Z")
    _cli(
        "debate",
        "submit",
        "--case",
        str(tmp_path),
        "--debate",
        debate.debate_id,
        "--side",
        "a",
        "--position",
        "compatible",
        "--evidence",
        "fact:x",
        "--disagree",
        "sdk impact=java non-null",
        "--risk",
        "npe",
        "--confidence",
        "0.6",
    )
    submit(tmp_path, debate.debate_id, "b", "breaking", ("fact:y",))
    cli = _cli("debate", "packet", "--case", str(tmp_path), "--debate", debate.debate_id)
    assert cli == tools.debate_packet(str(tmp_path), debate.debate_id)
    assert cli["disagreements"] == ["sdk impact"]
    assert cli["evidence"] == ["fact:x", "fact:y"]


def test_bad_disagreement_refuses_with_code(tmp_path: Path) -> None:
    debate = open_debate(tmp_path, "q", ("a", "b"), "2026-09-28T00:00:00Z")
    result = runner.invoke(
        app,
        [
            "debate",
            "submit",
            "--case",
            str(tmp_path),
            "--debate",
            debate.debate_id,
            "--side",
            "a",
            "--position",
            "p",
            "--evidence",
            "fact:x",
            "--disagree",
            "no-equals",
        ],
    )
    assert result.exit_code == 2
    assert "AF-DEBATE-DELTA-INVALID" in result.output


def test_agents_audit_parity() -> None:
    cli = _cli("agents", "audit", "--root", str(REPO))
    assert cli == tools.agents_audit(root=str(REPO))
    assert cli["agents"] == len(cli["rows"])
