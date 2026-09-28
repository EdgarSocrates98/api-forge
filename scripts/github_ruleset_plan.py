#!/usr/bin/env python3
"""Read-only plan for the GitHub ``protect`` ruleset (governance, not a mutation).

Input is the ruleset JSON the owner fetched with
``gh api repos/<owner>/<repo>/rulesets/<id>``; this script never calls GitHub
and never runs a process. It emits the payload an owner may apply with
``gh api -X PUT`` after review. ``scripts/github_pr_host.py`` stays the only
GitHub mutation boundary of the project.

The plan:

- targets the default branch when the ruleset targets no branch;
- requires the CI checks ``Validate project`` and
  ``Validate API/Git/CI replay control plane`` (strict policy);
- keeps every other rule, and warns about rules that change how PRs merge
  once the ruleset applies (``update`` blocks merges without a bypass);
- optionally adds the repository admin role as a ``pull_request`` bypass
  actor (``--bypass-owner``) or drops rule types (``--drop-rule``).
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_CHECKS = ("Validate project", "Validate API/Git/CI replay control plane")
ADMIN_BYPASS = {"actor_type": "RepositoryRole", "actor_id": 5, "bypass_mode": "pull_request"}
PUT_KEYS = ("name", "target", "enforcement", "conditions", "rules", "bypass_actors")
RULE_WARNINGS = {
    "update": "restricts updates: once the ruleset targets the default branch, PR merges "
    "are blocked unless a bypass actor merges (use --bypass-owner or --drop-rule update)",
    "creation": "restricts creation of matching refs (harmless for an existing default branch)",
    "required_signatures": "every commit on the branch must be signed; GitHub-made merge "
    "and squash commits are signed, local unsigned pushes are rejected",
}


class RulesetError(ValueError):
    def __init__(self, detail: str, field: str) -> None:
        super().__init__(
            f"AF-GITHUB-RULESET-INVALID: {detail} (field={field}; "
            "unlock=pass the JSON of `gh api repos/<owner>/<repo>/rulesets/<id>`)"
        )


def plan(
    ruleset: dict[str, Any],
    *,
    repository: str,
    bypass_owner: bool = False,
    drop_rules: tuple[str, ...] = (),
) -> dict[str, Any]:
    if not isinstance(ruleset, dict):
        raise RulesetError("ruleset must be a JSON object", "ruleset")
    rules = ruleset.get("rules")
    if not isinstance(rules, list) or not all(
        isinstance(rule, dict) and isinstance(rule.get("type"), str) for rule in rules
    ):
        raise RulesetError("rules must be a list of objects with a type", "rules")
    if not isinstance(ruleset.get("id"), int) or not isinstance(ruleset.get("name"), str):
        raise RulesetError("id (int) and name (str) are required", "id")
    payload: dict[str, Any] = {
        key: copy.deepcopy(ruleset[key]) for key in PUT_KEYS if key in ruleset
    }
    warnings: list[str] = []

    conditions = payload.setdefault("conditions", {})
    ref_name = conditions.setdefault("ref_name", {})
    include = ref_name.setdefault("include", [])
    ref_name.setdefault("exclude", [])
    if not include:
        warnings.append("ruleset targets no branch today; the plan targets ~DEFAULT_BRANCH")
        ref_name["include"] = ["~DEFAULT_BRANCH"]

    kept = [rule for rule in payload["rules"] if rule["type"] not in drop_rules]
    checks = next((rule for rule in kept if rule["type"] == "required_status_checks"), None)
    if checks is None:
        checks = {"type": "required_status_checks", "parameters": {}}
        kept.append(checks)
    parameters = checks.setdefault("parameters", {}) or {}
    checks["parameters"] = parameters
    existing = [
        item for item in parameters.get("required_status_checks") or [] if isinstance(item, dict)
    ]
    contexts = {item.get("context") for item in existing}
    parameters["required_status_checks"] = existing + [
        {"context": name} for name in REQUIRED_CHECKS if name not in contexts
    ]
    parameters["strict_required_status_checks_policy"] = True
    parameters.setdefault("do_not_enforce_on_create", False)
    payload["rules"] = kept

    bypass = [item for item in payload.get("bypass_actors") or [] if isinstance(item, dict)]
    if bypass_owner and ADMIN_BYPASS not in bypass:
        bypass.append(dict(ADMIN_BYPASS))
        warnings.append(
            "bypass: repository admins may merge PRs without meeting the rules, including "
            "the required checks; keep it only while there is a single maintainer"
        )
    payload["bypass_actors"] = bypass

    types = {rule["type"] for rule in kept}
    for rule_type, message in RULE_WARNINGS.items():
        if rule_type in types and not (rule_type == "update" and bypass_owner):
            warnings.append(f"{rule_type}: {message}")
    body = json.dumps(payload, sort_keys=True, indent=2)
    return {
        "schema": "apiforge/github-ruleset-plan/v1",
        "ruleset_id": ruleset["id"],
        "payload": payload,
        "warnings": warnings,
        "command": (
            f"gh api -X PUT repos/{repository}/rulesets/{ruleset['id']} --input plan-payload.json"
        ),
        "plan_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "applies": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", required=True, help="Ruleset JSON file, or - for stdin.")
    parser.add_argument("--repository", default="EdgarSocrates98/api-forge")
    parser.add_argument("--bypass-owner", action="store_true")
    parser.add_argument("--drop-rule", action="append", default=[])
    parser.add_argument("--payload-out", help="Write the PUT payload here (plan-payload.json).")
    args = parser.parse_args(argv)
    try:
        raw = (
            sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        )
        result = plan(
            json.loads(raw),
            repository=args.repository,
            bypass_owner=args.bypass_owner,
            drop_rules=tuple(args.drop_rule),
        )
    except (OSError, json.JSONDecodeError, RulesetError) as exc:
        print(
            str(exc) if isinstance(exc, RulesetError) else f"AF-GITHUB-RULESET-INVALID: {exc}",
            file=sys.stderr,
        )
        return 2
    if args.payload_out:
        Path(args.payload_out).write_text(
            json.dumps(result["payload"], sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
