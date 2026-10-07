import json
from pathlib import Path

from typer.testing import CliRunner

from apiforge.cli import app
from apiforge.mcp.tools import grpc_analyze


def test_cli_and_mcp_analysis_payloads_are_semantically_equivalent() -> None:
    source = str(Path("tests/fixtures/grpc/orders.proto"))
    cli_result = CliRunner().invoke(app, ["grpc", "analyze", source])
    assert cli_result.exit_code == 0
    cli_payload = json.loads(cli_result.stdout)
    mcp_payload = grpc_analyze(source)
    assert cli_payload == mcp_payload
