"""``apiforge-mcp`` missing-extra refusal contract.

The entry point must answer the missing-``mcp`` case with a named refusal
(``AF-MCP-UNAVAILABLE`` + unlock command, exit 2) — never a raw traceback —
and must not mislabel unrelated ``RuntimeError``s from ``build_server``.
"""

from __future__ import annotations

import pytest

from apiforge.mcp import main as mcp_main
from apiforge.mcp.server import MCP_OPTIONAL_UNAVAILABLE


def _stub_build_server(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    import apiforge.mcp.server as server_mod

    def fake(*_a: object, **_k: object) -> object:
        raise exc

    monkeypatch.setattr(server_mod, "build_server", fake)


def test_missing_extra_prints_named_refusal_and_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_build_server(
        monkeypatch,
        RuntimeError(f"{MCP_OPTIONAL_UNAVAILABLE}: install the 'mcp' extra"),
    )
    code = mcp_main.main([])
    err = capsys.readouterr().err
    assert code == 2
    assert "AF-MCP-UNAVAILABLE" in err
    assert "apiforge-af[mcp]" in err


def test_missing_extra_via_importerror_also_exits_2(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _stub_build_server(monkeypatch, ImportError("No module named 'mcp'", name="mcp"))
    assert mcp_main.main([]) == 2
    assert "apiforge-af[mcp]" in capsys.readouterr().err


def test_unrelated_importerror_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_build_server(monkeypatch, ImportError("No module named 'yaml'", name="yaml"))
    with pytest.raises(ImportError, match="yaml"):
        mcp_main.main([])


def test_unrelated_runtimeerror_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_build_server(monkeypatch, RuntimeError("boom: real config bug"))
    with pytest.raises(RuntimeError, match="boom"):
        mcp_main.main([])
