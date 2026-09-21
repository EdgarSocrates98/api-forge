"""Load the autonomy policy: versioned, closed-schema YAML data.

Lookup order for ``load_policy(None)``: ``apiforge.policy.yaml`` then
``.apiforge/policy.yaml`` under the current directory, then the built-in
``DEFAULT_POLICY`` — the engine never runs without a policy.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from apiforge.core.yaml import StrictLoadError, load_yaml_mapping
from apiforge.policy.models import (
    KNOWN_REQUIREMENTS,
    AutonomyClass,
    Policy,
    PolicyRule,
)

_CANDIDATES = (Path("apiforge.policy.yaml"), Path(".apiforge") / "policy.yaml")

_DEFAULT_DOC = """\
version: 1
defaults:
  read_only: allow
  local_reversible: allow
  sensitive: gate
  external_mutation: gate
  destructive: gate
  irreversible: deny
gates:
  destructive: [exact_target, impact, dry_run_or_reason, rollback, confirmation]
  sensitive: [evidence, approval]
  external_mutation: [identity_resolved, impact, rollback]
rules:
  - name: no-force-push
    match: {verb: "git.push", arg_glob: "--force*"}
    decision: deny
    reason: "rewrites shared history"
"""


class PolicyLoadError(ValueError):
    """A refused policy document; ``str()`` begins with the code."""

    def __init__(self, code: str, field: str) -> None:
        self.code = code
        self.field = field
        super().__init__(f"{code}: {field}")


def _schema(field: str) -> PolicyLoadError:
    return PolicyLoadError("AF-POLICY-SCHEMA", field)


def _parse(data: object, source: str) -> Policy:
    if not isinstance(data, Mapping):
        raise _schema("root")
    if data.get("version") != 1:
        raise _schema("version")
    unknown = set(data) - {"version", "defaults", "gates", "rules"}
    if unknown:
        raise _schema(min(str(k) for k in unknown))

    defaults_raw = data.get("defaults")
    if not isinstance(defaults_raw, Mapping):
        raise _schema("defaults")
    defaults: dict[AutonomyClass, Any] = {}
    for key, value in defaults_raw.items():
        try:
            klass = AutonomyClass(str(key))
        except ValueError:
            raise _schema(f"defaults.{key}") from None
        if value not in ("allow", "gate", "deny"):
            raise _schema(f"defaults.{key}")
        defaults[klass] = value
    missing = set(AutonomyClass) - set(defaults)
    if missing:
        raise _schema(f"defaults.{min(c.value for c in missing)}")

    gates: dict[AutonomyClass, tuple[str, ...]] = {}
    gates_raw = data.get("gates", {})
    if not isinstance(gates_raw, Mapping):
        raise _schema("gates")
    for key, requirements in gates_raw.items():
        try:
            klass = AutonomyClass(str(key))
        except ValueError:
            raise _schema(f"gates.{key}") from None
        if not isinstance(requirements, list) or not all(isinstance(r, str) for r in requirements):
            raise _schema(f"gates.{key}")
        unknown_req = [r for r in requirements if r not in KNOWN_REQUIREMENTS]
        if unknown_req:
            raise _schema(f"gates.{key}.{unknown_req[0]}")
        gates[klass] = tuple(requirements)

    rules: list[PolicyRule] = []
    rules_raw = data.get("rules", [])
    if not isinstance(rules_raw, list):
        raise _schema("rules")
    names: set[str] = set()
    for index, item in enumerate(rules_raw):
        try:
            rule = PolicyRule.model_validate(item)
        except ValidationError as exc:
            raise _schema(f"rules[{index}]") from exc
        if not isinstance(rule.match.verb, str) or not rule.match.verb:
            raise _schema(f"rules[{index}].match.verb")
        if rule.name in names:
            raise _schema(f"rules[{index}].name")
        names.add(rule.name)
        rules.append(rule)

    return Policy(version=1, defaults=defaults, gates=gates, rules=tuple(rules))


def load_policy(path: Path | None = None) -> Policy:
    """Load a policy file, or the first candidate, or the built-in default."""
    if path is None:
        for candidate in _CANDIDATES:
            if candidate.is_file():
                return load_policy(candidate)
        return load_policy_from_text(_DEFAULT_DOC, source="<default>")
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyLoadError("AF-POLICY-NOT-FOUND", str(path)) from exc
    return load_policy_from_text(text, source=str(path))


def load_policy_from_text(text: str, *, source: str = "<policy>") -> Policy:
    """Parse policy YAML text under the strict loader and closed schema."""
    try:
        data = load_yaml_mapping(text, source=source)
    except StrictLoadError as exc:
        raise PolicyLoadError("AF-POLICY-SCHEMA", f"{source}: {exc}") from exc
    return _parse(data, source)


DEFAULT_POLICY = load_policy_from_text(_DEFAULT_DOC, source="<default>")
