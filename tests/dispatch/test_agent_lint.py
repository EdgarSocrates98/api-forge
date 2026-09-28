from pathlib import Path

from apiforge.dispatch.agent_source import lint, load_roster
from tests.dispatch.agent_support import body, write_agent


def _codes(root: Path) -> set[tuple[str, str]]:
    return {(item.code, item.field) for item in lint(root).findings}


def test_valid_agent_passes(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    report = lint(tmp_path)
    assert report.ok and report.passing == 1


def test_missing_section_short_body_and_portuguese(tmp_path: Path) -> None:
    write_agent(
        tmp_path,
        "api-a",
        text="Siga `AGENT_PROTOCOL.md`. Quando você entra, não use para nada.\n\n## Inputs\n\nx",
    )
    codes = _codes(tmp_path)
    assert ("AF-AGENT-CONTRACT-SECTIONS", "body") in codes
    assert ("AF-AGENT-CONTRACT-WORDS", "body") in codes
    assert ("AF-AGENT-CONTRACT-LANGUAGE", "body") in codes


def test_long_body_and_bad_description(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-b", text=body(80), description="Contract helper.")
    codes = _codes(tmp_path)
    assert ("AF-AGENT-CONTRACT-WORDS", "body") in codes
    assert ("AF-AGENT-CONTRACT-DESCRIPTION", "description") in codes


def test_writer_needs_scope_and_access_is_required(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-c", access="writer")
    write_agent(tmp_path, "api-d", access=None, tools=("perf verdict",))
    codes = _codes(tmp_path)
    assert ("AF-AGENT-CONTRACT-ACCESS", "write_scope") in codes
    assert ("AF-AGENT-CONTRACT-ACCESS", "access") in codes


def test_tool_owned_twice_and_name_mismatch(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-e", tools=("perf verdict",))
    write_agent(tmp_path, "api-f", tools=("perf verdict",))
    path = write_agent(tmp_path, "api-g", tools=("grpc codegen",))
    path.rename(path.with_name("api-other.md"))
    findings = lint(tmp_path).findings
    owners = {item.agent for item in findings if item.code == "AF-AGENT-CONTRACT-TOOL-OWNER"}
    assert owners == {"api-e", "api-f"}
    assert any(item.code == "AF-AGENT-CONTRACT-NAME" for item in findings)
    assert all(item.unlock for item in findings)


def test_legacy_tools_key_is_read_as_apiforge_tools(tmp_path: Path) -> None:
    folder = tmp_path / "agents"
    folder.mkdir()
    (folder / "old.md").write_text("---\nname: old\ntools: [perf verdict]\n---\nbody\n")
    assert load_roster(tmp_path)[0].apiforge_tools == ("perf verdict",)
