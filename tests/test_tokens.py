"""economy tokens: transcript counts, estimate labeled, cost needs basis."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apiforge.economy.tokens import (
    TokenError,
    cost,
    estimate_tokens,
    read_transcript,
)


def _transcript(tmp_path: Path) -> Path:
    path = tmp_path / "t.jsonl"
    lines = [
        {"type": "assistant", "message": {"model": "m-a", "usage": {
            "input_tokens": 100, "output_tokens": 50,
            "cache_read_input_tokens": 10}}},
        {"type": "assistant", "message": {"model": "m-a", "usage": {
            "input_tokens": 200, "output_tokens": 60}}},
        {"type": "assistant", "message": {"model": "m-b", "usage": {
            "input_tokens": 5, "output_tokens": 7}}},
        {"type": "human", "message": {"role": "user"}},
        "not json",
        {"type": "assistant", "message": {"usage": {"input_tokens": 1}}},
    ]
    path.write_text("\n".join(json.dumps(line) if not isinstance(line, str) else line
                             for line in lines), encoding="utf-8")
    return path


def test_transcript_sums_per_model(tmp_path: Path) -> None:
    result = read_transcript(_transcript(tmp_path))
    assert result["counted"] is True
    assert result["models"]["m-a"]["input_tokens"] == 300
    assert result["models"]["m-a"]["output_tokens"] == 110
    assert result["models"]["m-a"]["cache_read_input_tokens"] == 10
    assert result["models"]["m-b"]["output_tokens"] == 7
    assert result["models"]["unknown"]["input_tokens"] == 1
    assert result["unparsed_lines"] == 1


def test_missing_transcript_named(tmp_path: Path) -> None:
    with pytest.raises(TokenError, match="AF-ECONOMY-TRANSCRIPT-MISSING"):
        read_transcript(tmp_path / "absent.jsonl")


def test_estimate_is_labeled() -> None:
    result = estimate_tokens(1000)
    assert result["estimated_tokens"] == 250
    assert result["counted"] is False
    assert "4" in result["estimation_method"]


def test_cost_prices_known_models_names_missing(tmp_path: Path) -> None:
    basis = tmp_path / "basis.yaml"
    basis.write_text(
        "m-a:\n  input_per_mtok: 3.0\n  output_per_mtok: 15.0\n",
        encoding="utf-8",
    )
    transcript = read_transcript(_transcript(tmp_path))
    result = cost(transcript, basis)
    # m-a: 300*3 + 110*15 = 900+1650 = 2550 µUSD = 0.00255
    assert result["per_model"]["m-a"]["usd"] == pytest.approx(0.00255)
    assert sorted(result["cost_basis_missing"]) == ["m-b", "unknown"]
    assert result["total_usd"] == pytest.approx(0.00255)


def test_missing_basis_named(tmp_path: Path) -> None:
    transcript = read_transcript(_transcript(tmp_path))
    with pytest.raises(TokenError, match="AF-ECONOMY-COST-BASIS-MISSING"):
        cost(transcript, tmp_path / "none.yaml")


def test_cli_report_with_transcript(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    from apiforge.cli import app

    runner = CliRunner()
    root = tmp_path / "case"
    (root / ".apiforge").mkdir(parents=True)
    (root / ".apiforge" / "economy.jsonl").write_text(
        json.dumps({"verb": "rules list", "detail_level": "normal",
                    "payload_bytes": 400}) + "\n",
        encoding="utf-8",
    )
    transcript = _transcript(tmp_path)
    result = runner.invoke(
        app, ["economy", "report", "--root", str(root),
              "--transcript", str(transcript), "--estimate"]
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["tokens_unresolved"] is False
    assert payload["tokens"]["models"]["m-a"]["input_tokens"] == 300
    assert payload["token_estimate"]["counted"] is False


def test_cli_cost_basis_without_transcript_refused(tmp_path: Path) -> None:
    from typer.testing import CliRunner

    from apiforge.cli import app

    result = CliRunner().invoke(
        app, ["economy", "report", "--root", str(tmp_path),
              "--cost-basis", str(tmp_path / "b.yaml")]
    )
    assert result.exit_code != 0
    assert "AF-ECONOMY-TRANSCRIPT-MISSING" in result.output
