from pathlib import Path

import pytest

from apiforge.contracts.base import ContractError
from apiforge.dispatch.aliases import AliasTable, load_table, parse_table, resolve_agent
from apiforge.dispatch.references import alias_problems, unknown_references
from tests.dispatch.agent_support import write_agent


def _agent_name(*parts: str) -> str:
    """Fictitious names are assembled at runtime so the reference gate never sees them."""
    return "-".join(parts)


FAKE = _agent_name("api", "nonexistent", "reviewer")
X = _agent_name("api", "x", "engineer")
Y = _agent_name("api", "y", "engineer")
A_REV, B_REV, C_REV = (_agent_name(c, "reviewer") for c in "abc")

ACTIVE = AliasTable(
    active=True,
    deprecated_in="roster-v2",
    aliases={"api-grpc-parser-engineer": "api-contract-architect"},
)


def test_active_alias_resolves_with_warning() -> None:
    resolution = resolve_agent("api-grpc-parser-engineer", ACTIVE)
    assert resolution.name == "api-contract-architect"
    assert resolution.warning == (
        "AF-AGENT-ALIAS-DEPRECATED: api-grpc-parser-engineer -> api-contract-architect"
    )
    assert resolve_agent("api-contract-architect", ACTIVE).warning is None


def test_inactive_table_is_a_no_op() -> None:
    inactive = AliasTable(active=False, deprecated_in="", aliases=ACTIVE.aliases)
    assert resolve_agent("api-grpc-parser-engineer", inactive).name == "api-grpc-parser-engineer"


def test_chains_and_self_aliases_are_refused() -> None:
    with pytest.raises(ContractError, match="AF-AGENT-ALIAS-INVALID"):
        parse_table({"aliases": {A_REV: B_REV, B_REV: C_REV}})
    with pytest.raises(ContractError, match="AF-AGENT-ALIAS-INVALID"):
        parse_table({"aliases": {A_REV: A_REV}})


def test_shipped_table_covers_every_absorbed_name() -> None:
    table = load_table()
    assert len(table.aliases) == 33
    assert len(set(table.aliases.values())) == 15


def test_unknown_reference_is_named_with_file_and_line(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    rules = tmp_path / "src" / "apiforge" / "rules"
    rules.mkdir(parents=True)
    (rules / "routing.yaml").write_text(
        f"routes:\n  - recommended_agent: api-contract-architect\n  - recommended_agent: {FAKE}\n",
        encoding="utf-8",
    )
    (rules / "skills.yaml").write_text("skill: api-forge-observability-control-plane\n")
    assert unknown_references(tmp_path, ACTIVE) == [f"src/apiforge/rules/routing.yaml:3: {FAKE}"]


def test_alias_keys_count_only_when_active(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_x.py").write_text('NAME = "api-grpc-parser-engineer"\n', encoding="utf-8")
    assert unknown_references(tmp_path, ACTIVE) == []
    inactive = AliasTable(active=False, deprecated_in="", aliases={})
    assert unknown_references(tmp_path, inactive) == ["tests/test_x.py:1: api-grpc-parser-engineer"]


def test_alias_target_must_be_a_coordinator(tmp_path: Path) -> None:
    write_agent(tmp_path, "api-contract-architect")
    broken = AliasTable(active=True, deprecated_in="", aliases={X: Y})
    assert alias_problems(tmp_path, broken) == [f"alias {X} -> {Y}: target is not a coordinator"]
    stale = AliasTable(
        active=True,
        deprecated_in="",
        aliases={"api-contract-architect": "api-governance-reviewer"},
    )
    write_agent(tmp_path, "api-governance-reviewer", tools=("diff contract",))
    assert alias_problems(tmp_path, stale) == [
        "alias api-contract-architect is still a coordinator file"
    ]


def test_repository_references_are_consistent() -> None:
    root = Path(__file__).resolve().parents[2]
    assert unknown_references(root) == []
    assert alias_problems(root) == []
