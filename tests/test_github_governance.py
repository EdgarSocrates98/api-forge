"""GitHub governance: CODEOWNERS materializes the ruleset; the ruleset plan never mutates."""

from __future__ import annotations

import ast
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "github_ruleset_plan.py"
FIXTURE = ROOT / "tests" / "fixtures" / "github" / "ruleset_protect.json"


def _plan_module():
    spec = spec_from_file_location("github_ruleset_plan_under_test", SCRIPT)
    assert spec and spec.loader
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_codeowners_exists_and_every_rule_has_an_owner() -> None:
    path = ROOT / ".github" / "CODEOWNERS"
    rules = [
        line.split()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert rules and rules[0][0] == "*"
    for pattern, *owners in rules:
        assert owners and all(owner.startswith("@") for owner in owners), pattern
        if "*" not in pattern:
            assert (ROOT / pattern.lstrip("/")).exists(), pattern
    assert any(pattern == "/.github/CODEOWNERS" for pattern, *_ in rules)


def test_plan_targets_default_branch_and_requires_ci_checks() -> None:
    module = _plan_module()
    ruleset = json.loads(FIXTURE.read_text(encoding="utf-8"))
    result = module.plan(ruleset, repository="EdgarSocrates98/api-forge")
    payload = result["payload"]
    assert result["applies"] is False
    assert payload["conditions"]["ref_name"]["include"] == ["~DEFAULT_BRANCH"]
    checks = next(rule for rule in payload["rules"] if rule["type"] == "required_status_checks")
    contexts = [item["context"] for item in checks["parameters"]["required_status_checks"]]
    assert contexts == ["Validate project", "Validate API/Git/CI replay control plane"]
    assert checks["parameters"]["strict_required_status_checks_policy"] is True
    before = {rule["type"] for rule in ruleset["rules"]}
    assert {rule["type"] for rule in payload["rules"]} == before
    assert any(item.startswith("update:") for item in result["warnings"])
    assert any("targets no branch" in item for item in result["warnings"])
    assert set(payload) <= {"name", "target", "enforcement", "conditions", "rules", "bypass_actors"}
    assert result["command"].startswith("gh api -X PUT repos/EdgarSocrates98/api-forge/rulesets/")


def test_plan_is_idempotent() -> None:
    module = _plan_module()
    ruleset = json.loads(FIXTURE.read_text(encoding="utf-8"))
    first = module.plan(ruleset, repository="o/r")
    again = module.plan({**ruleset, **first["payload"]}, repository="o/r")
    assert again["payload"] == first["payload"]
    assert again["plan_sha256"] == first["plan_sha256"]


def test_bypass_and_drop_rule_options() -> None:
    module = _plan_module()
    ruleset = json.loads(FIXTURE.read_text(encoding="utf-8"))
    bypassed = module.plan(ruleset, repository="o/r", bypass_owner=True)
    assert module.ADMIN_BYPASS in bypassed["payload"]["bypass_actors"]
    assert not any(item.startswith("update:") for item in bypassed["warnings"])
    assert any(item.startswith("bypass:") for item in bypassed["warnings"])
    dropped = module.plan(ruleset, repository="o/r", drop_rules=("update", "creation"))
    assert not {"update", "creation"} & {rule["type"] for rule in dropped["payload"]["rules"]}


@pytest.mark.parametrize("bad", [[], {"id": 1, "name": "x", "rules": "no"}, {"rules": []}])
def test_malformed_ruleset_is_refused(bad: object) -> None:
    module = _plan_module()
    with pytest.raises(module.RulesetError) as err:
        module.plan(bad, repository="o/r")
    assert "AF-GITHUB-RULESET-INVALID" in str(err.value)


def test_plan_script_cannot_mutate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
    } | {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not imported & {"subprocess", "socket", "urllib", "http", "requests", "httpx", "os"}
    module = _plan_module()
    (tmp_path / "ruleset.json").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert module.main(["--input", "ruleset.json", "--payload-out", "plan-payload.json"]) == 0
    assert json.loads((tmp_path / "plan-payload.json").read_text(encoding="utf-8"))["rules"]
    assert module.main(["--input", "../outside.json"]) == 2
    assert module.main(["--input", "ruleset.json", "--payload-out", "../x.json"]) == 2
    assert not (tmp_path.parent / "x.json").exists()
