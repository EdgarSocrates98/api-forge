"""Adversarial review helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


def critic_findings(artifacts: Iterable[Mapping[str, object]]) -> tuple[str, ...]:
    findings: list[str] = []
    for artifact in artifacts:
        evidence = artifact.get("evidence")
        confidence = artifact.get("confidence")
        if not evidence:
            findings.append("artifact has no evidence")
        if isinstance(confidence, (int, float)) and confidence < 0.70:
            findings.append("artifact confidence is below 0.70")
        unresolved = artifact.get("unresolved")
        if isinstance(unresolved, list | tuple) and unresolved:
            findings.extend(str(item) for item in unresolved)
    return tuple(sorted(set(findings)))
