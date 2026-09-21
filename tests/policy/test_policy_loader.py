from pathlib import Path

import pytest

from apiforge.policy.loader import PolicyLoadError, load_policy

FIXTURES = Path("tests/fixtures/policy")


def test_default_policy_denies_irreversible() -> None:
    policy = load_policy(None)
    assert policy.defaults["irreversible"] == "deny"
    assert policy.defaults["destructive"] == "gate"
    assert policy.defaults["read_only"] == "allow"


def test_unknown_top_key_is_named(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text("version: 1\nsurprise: true\n", encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_gate_requirements_are_closed() -> None:
    policy = load_policy(FIXTURES / "full.yaml")
    assert policy.gates["destructive"] == (
        "exact_target",
        "impact",
        "dry_run_or_reason",
        "rollback",
        "confirmation",
    )


def test_missing_class_in_defaults_is_named(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text("version: 1\ndefaults: {read_only: allow}\n", encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_unknown_decision_is_named(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text(
        "version: 1\ndefaults: {read_only: maybe, local_reversible: allow,"
        " sensitive: gate, external_mutation: gate, destructive: gate,"
        " irreversible: deny}\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_wrong_version_is_named(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text("version: 2\ndefaults: {}\n", encoding="utf-8")
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_unknown_gate_requirement_is_named(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text(
        "version: 1\n"
        "defaults: {read_only: allow, local_reversible: allow, sensitive: gate,"
        " external_mutation: gate, destructive: gate, irreversible: deny}\n"
        "gates: {destructive: [magic_word]}\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_duplicate_rule_name_is_named(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text(
        (FIXTURES / "full.yaml").read_text(encoding="utf-8")
        + "  - name: no-force-push\n    match: {verb: other}\n    decision: deny\n",
        encoding="utf-8",
    )
    with pytest.raises(PolicyLoadError, match="AF-POLICY-SCHEMA"):
        load_policy(path)


def test_candidate_file_takes_precedence(tmp_path: Path, monkeypatch) -> None:
    content = (FIXTURES / "full.yaml").read_text(encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    candidate = tmp_path / "apiforge.policy.yaml"
    candidate.write_text(content, encoding="utf-8")
    policy = load_policy(None)
    assert any(r.name == "plan-approve-gate" for r in policy.rules)
