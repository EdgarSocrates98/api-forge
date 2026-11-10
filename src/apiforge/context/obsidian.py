"""Read-only API contract review projection for federated Obsidian notes."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from typing import Any

import yaml

_SENSITIVE = ("secret", "token", "password", "credential", "access_key", "session_key")
_SENSITIVE_TEXT = re.compile(
    r"(?i)(\b(?:secret|token|password|credential|access[_-]?key|session[_-]?key)\s*[:=]\s*)([^\s,;]+)"
)


def _safe(value: Any, key: str = "") -> Any:
    if any(marker in key.lower() for marker in _SENSITIVE):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): _safe(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [_safe(item, key) for item in value]
    if isinstance(value, str):
        return _SENSITIVE_TEXT.sub(r"\1[REDACTED]", value)
    return value


def _section(title: str, values: Any) -> list[str]:
    safe = _safe(values)
    if safe in (None, "", [], {}):
        return [f"## {title}", "- None reported", ""]
    return [
        f"## {title}",
        "```yaml",
        yaml.safe_dump(safe, sort_keys=True, allow_unicode=True).rstrip(),
        "```",
        "",
    ]


def build_obsidian_contract_review(
    *,
    title: str,
    summary: str,
    workspace: str,
    vault_id: str,
    endpoints: list[Any] | None = None,
    breaking_changes: list[Any] | None = None,
    adrs: list[Any] | None = None,
    security_review: list[Any] | None = None,
    e2e_notes: list[Any] | None = None,
    related_refs: list[str] | None = None,
    note_path: str = "api-reviews/contract-review.md",
    confidence: str = "unknown",
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    safe_title = str(_safe(title.strip() or "API contract review"))
    safe_summary = str(_safe(summary.strip()))
    metadata = _safe(
        {
            "type": "api-contract-review",
            "source": "api-forge",
            "classification": "internal",
            "confidence": confidence,
            "provenance": provenance or {},
        }
    )
    lines = [
        "---",
        yaml.safe_dump(metadata, sort_keys=True, allow_unicode=True).rstrip(),
        "---",
        f"# {safe_title}",
        "",
        safe_summary,
        "",
    ]
    lines += _section("Endpoints", endpoints)
    lines += _section("Breaking changes", breaking_changes)
    lines += _section("ADRs", adrs)
    lines += _section("Security review", security_review)
    lines += _section("E2E notes", {"notes": e2e_notes or [], "related_refs": related_refs or []})
    content = "\n".join(lines).rstrip() + "\n"
    return {
        "schema": "theforge/ObsidianNoteDraft/v1",
        "version": "v1",
        "workspace": workspace,
        "vault_id": vault_id,
        "path": note_path,
        "source": "api-forge",
        "classification": "internal",
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "updated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "outcome": "projected",
        "provenance": {"adapter": "api-forge", **_safe(provenance or {})},
        "content": content,
        "warnings": [],
        "unresolved": [],
    }


def to_obsidian_note_ref(draft: dict[str, Any]) -> dict[str, Any]:
    """Project a body-bearing draft to the canonical body-free ref."""
    if draft.get("schema") != "theforge/ObsidianNoteDraft/v1" or not isinstance(
        draft.get("content"), str
    ):
        raise ValueError("expected theforge/ObsidianNoteDraft/v1 with Markdown content")
    return {key: value for key, value in draft.items() if key != "content"} | {
        "schema": "theforge/ObsidianNoteRef/v1"
    }


__all__ = ["build_obsidian_contract_review", "to_obsidian_note_ref"]
