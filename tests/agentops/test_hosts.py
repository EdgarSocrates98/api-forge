from pathlib import Path

from apiforge.agentops.hosts import list_hosts


def test_host_declarations_include_packaged_asset_provenance() -> None:
    hosts = list_hosts()

    assert {item["name"] for item in hosts} == {"claude", "gpt-codex", "devin", "copilot"}
    assert all(item["asset_source"] == "package:apiforge.host_assets" for item in hosts)
    assert all(isinstance(item["asset_sha256"], str) for item in hosts)


def test_asset_provenance_is_independent_of_current_directory(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    host = next(item for item in list_hosts() if item["name"] == "claude")

    assert host["asset_sha256"]
