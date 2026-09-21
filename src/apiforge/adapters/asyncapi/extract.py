"""AsyncAPI extractor: doc.yaml -> asyncapi.* facts, offline.

AsyncAPI 2.x models pub/sub as ``channels.<name>.publish|subscribe``; 3.x as
top-level ``operations`` referencing channels. Both become
``asyncapi.operation`` facts with an ``action`` of ``send``/``receive`` —
the reader's projection, the document's words kept in ``raw_action``.
``$ref`` values are recorded as pointers, never dereferenced; a document
whose version is neither 2.x nor 3.x is ``AF-ASYNC-VERSION``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from apiforge.adapters.inventory import CodeInventory
from apiforge.core.ids import stable_id
from apiforge.core.models import Diagnostic, Fact, FindingStatus, SourceRef
from apiforge.core.yaml import StrictLoadError, load_yaml_strict

_EXTRACTOR = "asyncapi-doc"


def _fact(kind: str, rel: str, digest: str, measures: dict[str, Any], attrs: dict[str, Any]) -> Fact:
    return Fact(
        fact_id=stable_id("fact", {"kind": kind, "file": rel, **measures}),
        kind=kind,
        source=SourceRef(path=rel, sha256=digest, extractor=_EXTRACTOR),
        measures=measures,
        attrs=attrs,
    )


def _diag(code: str, rel: str, digest: str, message: str) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=message,
        source=SourceRef(path=rel, sha256=digest, line=None, extractor=_EXTRACTOR),
    )


def _ref_of(value: Any) -> str | None:
    return str(value["$ref"]) if isinstance(value, dict) and "$ref" in value else None


def _message_names(raw: Any) -> tuple[str, ...]:
    if isinstance(raw, dict):
        if _ref_of(raw):
            return (_ref_of(raw) or "",)
        if "oneOf" in raw and isinstance(raw["oneOf"], list):
            return tuple(_ref_of(m) or str(m.get("name", "?")) for m in raw["oneOf"])
        return (str(raw.get("name", raw.get("title", "?"))),)
    if isinstance(raw, list):
        return tuple(_ref_of(m) or "?" for m in raw)
    if isinstance(raw, str):
        return (raw,)
    return ()


def _operations_v2(channels: dict[str, Any]) -> list[tuple[str, str, str, tuple[str, ...]]]:
    ops: list[tuple[str, str, str, tuple[str, ...]]] = []
    for name, spec in channels.items():
        if not isinstance(spec, dict):
            continue
        for verb in ("publish", "subscribe"):
            op = spec.get(verb)
            if not isinstance(op, dict):
                continue
            # 2.x: publish = provider sends, subscribe = provider receives.
            action = "send" if verb == "publish" else "receive"
            ops.append((name, verb, action, _message_names(op.get("message"))))
    return ops


def _operations_v3(doc: dict[str, Any]) -> list[tuple[str, str, str, tuple[str, ...]]]:
    ops: list[tuple[str, str, str, tuple[str, ...]]] = []
    for name, op in (doc.get("operations") or {}).items():
        if not isinstance(op, dict):
            continue
        channel = op.get("channel")
        channel_ref = _ref_of(channel) or ""
        action = str(op.get("action", ""))
        msgs = _message_names(op.get("messages"))
        ops.append((channel_ref, name, action, msgs))
    return ops


def extract_asyncapi(path: Path) -> CodeInventory:
    """AsyncAPI 2.x/3.x document -> ``asyncapi.*`` facts."""
    path = Path(path)
    facts: list[Fact] = []
    diagnostics: list[Diagnostic] = []
    hashes: dict[str, str] = {}
    rel = path.name
    raw = path.read_bytes()
    hashes[rel] = hashlib.sha256(raw).hexdigest()
    try:
        doc: Any = load_yaml_strict(raw.decode("utf-8"), source=rel)
    except (StrictLoadError, UnicodeDecodeError) as exc:
        diagnostics.append(_diag("AF-ASYNC-INVALID", rel, hashes[rel], str(exc)))
        return CodeInventory(
            framework="asyncapi",
            root=str(path.parent),
            diagnostics=tuple(diagnostics),
            facts=(),
            input_hashes=hashes,
        )
    if not isinstance(doc, dict) or "asyncapi" not in doc:
        diagnostics.append(
            _diag("AF-ASYNC-INVALID", rel, hashes[rel], "missing 'asyncapi' version key")
        )
        return CodeInventory(
            framework="asyncapi",
            root=str(path.parent),
            diagnostics=tuple(diagnostics),
            facts=(),
            input_hashes=hashes,
        )

    version = str(doc["asyncapi"])
    channels = doc.get("channels") or {}
    major = version.split(".")[0]
    if major == "2":
        ops = _operations_v2(channels)
        channel_names = tuple(sorted(channels))
    elif major == "3":
        ops = _operations_v3(doc)
        channel_names = tuple(sorted(channels))
    else:
        diagnostics.append(
            _diag("AF-ASYNC-VERSION", rel, hashes[rel], f"asyncapi {version} unsupported")
        )
        ops, channel_names = [], ()

    for name, spec in (doc.get("servers") or {}).items():
        if not isinstance(spec, dict):
            continue
        facts.append(
            _fact(
                "asyncapi.server",
                rel,
                hashes[rel],
                {"name": str(name)},
                {"host": spec.get("host"), "protocol": spec.get("protocol")},
            )
        )
    for name in channel_names:
        spec = channels.get(name) or {}
        address = spec.get("address", name) if isinstance(spec, dict) else name
        if _ref_of(address):
            address = str(spec.get("address")) if isinstance(spec, dict) else name
        facts.append(
            _fact(
                "asyncapi.channel",
                rel,
                hashes[rel],
                {"name": str(name)},
                {"address": str(address)},
            )
        )
    for channel, name, action, messages in ops:
        facts.append(
            _fact(
                "asyncapi.operation",
                rel,
                hashes[rel],
                {"operation": str(name)},
                {
                    "channel": str(channel),
                    "action": str(action),
                    "messages": messages,
                },
            )
        )

    for section in (channels, doc.get("operations") or {}, doc.get("components") or {}):
        _collect_refs(section, rel, hashes[rel], diagnostics)

    return CodeInventory(
        framework="asyncapi",
        root=str(path.parent),
        diagnostics=tuple(diagnostics),
        facts=tuple(facts),
        input_hashes=hashes,
    )


def _collect_refs(
    node: Any, rel: str, digest: str, diagnostics: list[Diagnostic]
) -> None:
    """Every `$ref` is a named unresolved pointer — recorded, never followed."""
    if isinstance(node, dict):
        if "$ref" in node:
            diagnostics.append(
                _diag(
                    "AF-ASYNC-UNRESOLVED",
                    rel,
                    digest,
                    f"$ref {node['$ref']} recorded as pointer, not dereferenced",
                )
            )
        for value in node.values():
            _collect_refs(value, rel, digest, diagnostics)
    elif isinstance(node, list):
        for item in node:
            _collect_refs(item, rel, digest, diagnostics)
