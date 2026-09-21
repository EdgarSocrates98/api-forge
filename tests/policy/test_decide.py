from pathlib import Path

import pytest
from pydantic import ValidationError

from apiforge.policy.decide import ActionRequest, decide
from apiforge.policy.loader import DEFAULT_POLICY, load_policy

FIXTURES = Path("tests/fixtures/policy")
FULL = load_policy(FIXTURES / "full.yaml")


def test_unknown_class_is_denied_by_name() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="x", autonomy_class="bogus"))
    assert d.outcome == "deny"
    assert d.reason_code == "AF-POLICY-CLASS-UNKNOWN"


def test_destructive_lists_missing_requirements() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="fs.delete", autonomy_class="destructive"))
    assert d.outcome == "gate"
    assert "exact_target" in d.missing_requirements
    assert "confirmation" in d.missing_requirements


def test_deny_rule_beats_default_allow() -> None:
    d = decide(
        DEFAULT_POLICY,
        ActionRequest(verb="git.push", autonomy_class="local_reversible", args=("--force",)),
    )
    assert d.outcome == "deny"
    assert d.rule == "no-force-push"


def test_read_only_is_allowed() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="fs.read", autonomy_class="read_only"))
    assert d.outcome == "allow"


def test_gate_satisfied_by_detail_fields() -> None:
    d = decide(
        DEFAULT_POLICY,
        ActionRequest(
            verb="fs.delete",
            autonomy_class="destructive",
            detail={
                "exact_target": "x",
                "impact": "y",
                "dry_run_or_reason": "z",
                "rollback": "w",
                "confirmation": "yes",
            },
        ),
    )
    assert d.outcome == "allow"
    assert d.satisfied_by == (
        "exact_target",
        "impact",
        "dry_run_or_reason",
        "rollback",
        "confirmation",
    )


def test_first_matching_rule_wins() -> None:
    d = decide(FULL, ActionRequest(verb="release.deploy", autonomy_class="external_mutation"))
    assert d.rule == "plan-approve-gate"
    assert d.outcome == "gate"


def test_rule_arg_glob_does_not_match_other_args() -> None:
    d = decide(
        DEFAULT_POLICY,
        ActionRequest(verb="git.push", autonomy_class="local_reversible", args=("--tags",)),
    )
    assert d.outcome == "allow"


def test_missing_class_defaults_to_deny() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="x"))
    assert d.outcome == "deny"
    assert d.reason_code == "AF-POLICY-CLASS-UNKNOWN"


def test_decision_is_frozen() -> None:
    d = decide(DEFAULT_POLICY, ActionRequest(verb="fs.read", autonomy_class="read_only"))
    assert d.subject == "fs.read"
    with pytest.raises(ValidationError):
        d.outcome = "deny"  # type: ignore[misc]
