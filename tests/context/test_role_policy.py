"""RoleContext v2 policy: yaml loading, deny-first filtering, required delivery."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from apiforge.context.role_policy import (
    ORIGIN_RANK,
    check_tool,
    filter_refs,
    order_required_first,
    parse_policies,
    policy_for,
    required_missing,
    visibility_for,
)
from apiforge.contracts.base import ContractError
from apiforge.contracts.context import ContextRef
from apiforge.runtime.role_context import load_role_policy


def _uri(seed: str) -> str:
    return f"ctx://sha256/{hashlib.sha256(seed.encode()).hexdigest()}"


def _ref(seed: str, *, kind: str = "code", origin: str = "code") -> ContextRef:
    return ContextRef(
        uri=_uri(seed),
        kind=kind,
        label=seed,
        source=f"{seed}.py",  # type: ignore[arg-type]
        size_bytes=10,
        provenance="test",
        origin=origin,  # type: ignore[arg-type]
    )


def test_shipped_yaml_loads_v2_policies() -> None:
    policy = load_role_policy()
    assert set(policy["roles"]) == {"specialist", "reviewer", "critic", "referee"}
    assert policy["policies"]["referee"].required_evidence is True
    assert "code" in policy["policies"]["critic"].denied_kinds


def test_v1_yaml_without_policies_stays_permissive(tmp_path: Path) -> None:
    path = tmp_path / "role_context.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "schema": "apiforge/role-context/v1",
                "classes": {
                    "focused": {"kinds": ["contract", "code"], "share": 0.5},
                    "rest": {"kinds": [], "share": 0.5},
                },
                "roles": {
                    "specialist": "focused",
                    "reviewer": "rest",
                    "critic": "rest",
                    "referee": "rest",
                },
            }
        ),
        encoding="utf-8",
    )
    loaded = load_role_policy(path)
    assert loaded["policies"] == {}
    default = policy_for(loaded["policies"], "reviewer")
    kept, trimmed, notes = filter_refs(default, [_ref("a", kind="contract", origin="contract")])
    assert kept and not trimmed and not notes


def test_policy_naming_unknown_role_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "role_context.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "schema": "apiforge/role-context/v2",
                "classes": {
                    "focused": {"kinds": ["code"], "share": 1.0},
                },
                "roles": {
                    "specialist": "focused",
                    "reviewer": "focused",
                    "critic": "focused",
                    "referee": "focused",
                },
                "policies": {"ghost": {"denied_kinds": ["code"]}},
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ContractError, match="AF-ROLE-CONTEXT-POLICY"):
        load_role_policy(path)


def test_denied_kinds_trim_with_refusal_note() -> None:
    policy = policy_for({}, "reviewer").model_copy(update={"denied_kinds": ("code",)})
    refs = [_ref("contract", kind="contract", origin="contract"), _ref("code")]
    kept, trimmed, notes = filter_refs(policy, refs)
    assert [ref.kind for ref in kept] == ["contract"]
    assert trimmed == [refs[1].uri]
    assert any("AF-ROLE-CONTEXT-DENIED" in note and "kind" in note for note in notes)


def test_minimum_origin_rank_trims_below_floor() -> None:
    policy = policy_for({}, "critic").model_copy(update={"minimum_origin_rank": "contract"})
    refs = [
        _ref("low", origin="filesystem"),
        _ref("high", kind="contract", origin="contract"),
    ]
    kept, _trimmed, notes = filter_refs(policy, refs)
    assert [ref.uri for ref in kept] == [refs[1].uri]
    assert any("AF-ROLE-CONTEXT-TRUST" in note for note in notes)


def test_required_kinds_are_delivered_first() -> None:
    policy = policy_for({}, "reviewer").model_copy(update={"required_kinds": ("policy",)})
    refs = [
        _ref("code", kind="code"),
        _ref("policy", kind="policy", origin="contract"),
    ]
    ordered = order_required_first(policy, refs)
    assert ordered[0].kind == "policy"


def test_required_missing_only_when_present_but_undelivered() -> None:
    policy = policy_for({}, "reviewer").model_copy(update={"required_kinds": ("policy",)})
    policy_ref = _ref("policy", kind="policy", origin="contract")
    code_ref = _ref("code")
    # policy kind never existed -> not a violation (requirements conjure nothing)
    assert required_missing(policy, [code_ref], [code_ref]) == []
    # existed but trimmed -> violation
    assert required_missing(policy, [policy_ref], [code_ref]) == ["policy"]


def test_tool_visibility_allowlist_denies_unlisted() -> None:
    policy = policy_for({}, "specialist").model_copy(
        update={"tool_visibility": ("context capsule",)}
    )
    check_tool(policy, "context capsule")
    with pytest.raises(ContractError, match="AF-ROLE-CONTEXT-TOOL"):
        check_tool(policy, "shell write")


def test_visibility_levels_default_hidden_for_unknown_plane() -> None:
    policy = policy_for({}, "referee")
    assert visibility_for(policy, "memory") in ("full", "summary", "none")
    assert visibility_for(policy, "alien-plane") == "none"


def test_parse_policies_wraps_bad_shape() -> None:
    with pytest.raises(ContractError, match="AF-ROLE-CONTEXT-POLICY"):
        parse_policies({"reviewer": "not-a-mapping"}, path="x.yaml")
    with pytest.raises(ContractError, match="AF-ROLE-CONTEXT-POLICY"):
        parse_policies(
            {"reviewer": {"denied_kinds": ["code"], "required_kinds": ["code"]}}, path="x.yaml"
        )


def test_origin_rank_is_deterministic() -> None:
    assert ORIGIN_RANK["filesystem"] < ORIGIN_RANK["contract"]
    assert set(ORIGIN_RANK) == {"filesystem", "knowledge", "code", "graph", "contract"}
