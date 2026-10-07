"""Bounded contract diff between two OpenAPI 3.1 documents.

Supported classifications: operation addition/removal, response status
addition/removal, request required-property changes, response/request
property-set changes, and request body presence. Local component refs of the
exact form ``#/components/schemas/<name>`` are resolved with a bounded cycle
guard; anything else that differs becomes a named unresolved change instead
of a guessed verdict.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

from apiforge.core.ids import stable_id
from apiforge.core.models import FindingStatus
from apiforge.openapi.models import OpenApiDocument, OpenApiOperation


class ChangeKind(StrEnum):
    OPERATION_REMOVED = "AF-BREAKING-OPERATION-REMOVED"
    OPERATION_ADDED = "AF-COMPAT-OPERATION-ADDED"
    RESPONSE_STATUS_REMOVED = "AF-BREAKING-RESPONSE-REMOVED"
    RESPONSE_STATUS_ADDED = "AF-COMPAT-RESPONSE-ADDED"
    REQUEST_BODY_ADDED = "AF-BREAKING-REQUEST-BODY-ADDED"
    REQUEST_BODY_REMOVED = "AF-BREAKING-REQUEST-BODY-REMOVED"
    REQUEST_REQUIRED_ADDED = "AF-BREAKING-REQUEST-REQUIRED-ADDED"
    REQUEST_REQUIRED_REMOVED = "AF-COMPAT-REQUEST-REQUIRED-REMOVED"
    REQUEST_OPTIONAL_ADDED = "AF-COMPAT-REQUEST-OPTIONAL-ADDED"
    REQUEST_PROPERTY_REMOVED = "AF-BREAKING-REQUEST-PROPERTY-REMOVED"
    RESPONSE_OPTIONAL_ADDED = "AF-COMPAT-RESPONSE-OPTIONAL-ADDED"
    RESPONSE_REQUIRED_ADDED = "AF-BREAKING-RESPONSE-REQUIRED-ADDED"
    RESPONSE_REQUIRED_REMOVED = "AF-BREAKING-RESPONSE-REQUIRED-REMOVED"
    RESPONSE_PROPERTY_REMOVED = "AF-BREAKING-RESPONSE-PROPERTY-REMOVED"
    REF_UNRESOLVED = "AF-OPENAPI-REF-UNRESOLVED"
    UNCLASSIFIED = "AF-OPENAPI-UNCLASSIFIED"


_BREAKING = frozenset(kind for kind in ChangeKind if kind.value.startswith("AF-BREAKING-"))

_LOCAL_REF = re.compile(r"^#/components/schemas/([^/]+)$")
_MAX_REF_DEPTH = 8


class ContractChange(BaseModel):
    """One classified delta between two contract versions."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    change_id: str
    code: ChangeKind
    breaking: bool
    status: FindingStatus
    path: str
    method: str | None = None
    pointer: str
    detail: str = ""
    evidence: tuple[str, ...] = ()


def _escape(segment: str) -> str:
    return segment.replace("~", "~0").replace("/", "~1")


def _pointer(*segments: str) -> str:
    return "/" + "/".join(_escape(s) for s in segments)


def _add(
    changes: list[ContractChange],
    kind: ChangeKind,
    *,
    path: str,
    method: str | None,
    pointer: str,
    detail: str,
    evidence: tuple[str, ...] = (),
) -> None:
    unresolved = kind in (ChangeKind.REF_UNRESOLVED, ChangeKind.UNCLASSIFIED)
    changes.append(
        ContractChange(
            change_id=stable_id(
                "change",
                {"code": kind.value, "path": path, "method": method, "pointer": pointer},
            ),
            code=kind,
            breaking=kind in _BREAKING,
            status=FindingStatus.UNRESOLVED if unresolved else FindingStatus.CONFIRMED,
            path=path,
            method=method,
            pointer=pointer,
            detail=detail,
            evidence=evidence,
        )
    )


def _resolve_schema(
    schema: object, components: Mapping[str, Any]
) -> tuple[Mapping[str, Any] | None, str | None]:
    """Resolve local ``#/components/schemas/*`` refs; None + ref on failure."""
    seen: set[str] = set()
    current = schema
    for _ in range(_MAX_REF_DEPTH):
        if not isinstance(current, Mapping):
            return None, "non-mapping"
        ref = current.get("$ref")
        if ref is None:
            return current, None
        if not isinstance(ref, str) or not _LOCAL_REF.match(ref) or ref in seen:
            return None, str(ref)
        seen.add(ref)
        current = components.get("schemas", {}).get(_LOCAL_REF.match(ref).group(1))  # type: ignore[union-attr]
    return None, "depth-exceeded"


def _media_schema(container: Mapping[str, Any]) -> object:
    content = container.get("content")
    if not isinstance(content, Mapping) or not content:
        return None
    key = "application/json" if "application/json" in content else min(content)
    media = content[key]
    return media.get("schema") if isinstance(media, Mapping) else None


def _object_view(
    schema: object, components: Mapping[str, Any]
) -> tuple[Mapping[str, Any] | None, str | None]:
    resolved, bad_ref = _resolve_schema(schema, components)
    if bad_ref is not None:
        return None, bad_ref
    if resolved is None or resolved.get("type") not in (None, "object"):
        return resolved, None
    return resolved, None


def _properties(schema: Mapping[str, Any]) -> Mapping[str, Any]:
    props = schema.get("properties")
    return props if isinstance(props, Mapping) else {}


def _required(schema: Mapping[str, Any]) -> set[str]:
    required = schema.get("required")
    if not isinstance(required, (list, tuple)):
        return set()
    return {item for item in required if isinstance(item, str)}


def _diff_schema(
    base_schema: object,
    cand_schema: object,
    base_doc: OpenApiDocument,
    cand_doc: OpenApiDocument,
    *,
    side: str,
    path: str,
    method: str,
    base_pointer: str,
    evidence: tuple[str, ...],
    changes: list[ContractChange],
) -> None:
    if base_schema is None and cand_schema is None:
        return
    if base_schema is None or cand_schema is None:
        _add(
            changes,
            ChangeKind.UNCLASSIFIED,
            path=path,
            method=method,
            pointer=base_pointer,
            detail=f"{side} schema present on only one side",
            evidence=evidence,
        )
        return
    base_obj, base_bad = _object_view(base_schema, base_doc.components)
    cand_obj, cand_bad = _object_view(cand_schema, cand_doc.components)
    for bad_ref in (base_bad, cand_bad):
        if bad_ref is not None:
            _add(
                changes,
                ChangeKind.REF_UNRESOLVED,
                path=path,
                method=method,
                pointer=base_pointer,
                detail=f"unresolvable $ref {bad_ref!r} in {side} schema",
                evidence=evidence,
            )
    if base_obj is None or cand_obj is None:
        return
    if base_obj.get("type") not in (None, "object") or cand_obj.get("type") not in (
        None,
        "object",
    ):
        if dict(base_obj) != dict(cand_obj):
            _add(
                changes,
                ChangeKind.UNCLASSIFIED,
                path=path,
                method=method,
                pointer=base_pointer,
                detail=f"{side} schema is not an object; delta not classified",
                evidence=evidence,
            )
        return

    base_props, cand_props = _properties(base_obj), _properties(cand_obj)
    base_req, cand_req = _required(base_obj), _required(cand_obj)

    if side == "request":
        for name in sorted(cand_req - base_req):
            _add(
                changes,
                ChangeKind.REQUEST_REQUIRED_ADDED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/required/{_escape(name)}",
                detail=f"request property {name!r} became required",
                evidence=evidence,
            )
        for name in sorted(base_req - cand_req):
            _add(
                changes,
                ChangeKind.REQUEST_REQUIRED_REMOVED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/required/{_escape(name)}",
                detail=f"request property {name!r} is no longer required",
                evidence=evidence,
            )
        for name in sorted(set(base_props) - set(cand_props)):
            _add(
                changes,
                ChangeKind.REQUEST_PROPERTY_REMOVED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/properties/{_escape(name)}",
                detail=f"request property {name!r} removed",
                evidence=evidence,
            )
        for name in sorted(set(cand_props) - set(base_props)):
            if name in cand_req:
                continue  # already reported as required-added
            _add(
                changes,
                ChangeKind.REQUEST_OPTIONAL_ADDED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/properties/{_escape(name)}",
                detail=f"optional request property {name!r} added",
                evidence=evidence,
            )
    else:
        for name in sorted(set(cand_props) - set(base_props)):
            kind = (
                ChangeKind.RESPONSE_REQUIRED_ADDED
                if name in cand_req
                else ChangeKind.RESPONSE_OPTIONAL_ADDED
            )
            _add(
                changes,
                kind,
                path=path,
                method=method,
                pointer=f"{base_pointer}/properties/{_escape(name)}",
                detail=f"response property {name!r} added ({'required' if name in cand_req else 'optional'})",
                evidence=evidence,
            )
        for name in sorted(set(base_props) - set(cand_props)):
            _add(
                changes,
                ChangeKind.RESPONSE_PROPERTY_REMOVED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/properties/{_escape(name)}",
                detail=f"response property {name!r} removed",
                evidence=evidence,
            )
        for name in sorted(base_req - cand_req):
            _add(
                changes,
                ChangeKind.RESPONSE_REQUIRED_REMOVED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/required/{_escape(name)}",
                detail=f"response property {name!r} no longer required",
                evidence=evidence,
            )
    for name in sorted(set(base_props) & set(cand_props)):
        if base_props[name] != cand_props[name]:
            _add(
                changes,
                ChangeKind.UNCLASSIFIED,
                path=path,
                method=method,
                pointer=f"{base_pointer}/properties/{_escape(name)}",
                detail=f"{side} property {name!r} schema changed; not classified",
                evidence=evidence,
            )


def _diff_operation(
    base: OpenApiOperation,
    cand: OpenApiOperation,
    base_doc: OpenApiDocument,
    cand_doc: OpenApiDocument,
    changes: list[ContractChange],
) -> None:
    path, method = base.path, base.method
    op_pointer = _pointer("paths", path, method)
    evidence = (base.fact_id, cand.fact_id)

    base_res = base.raw.get("responses")
    cand_res = cand.raw.get("responses")
    base_res = base_res if isinstance(base_res, Mapping) else {}
    cand_res = cand_res if isinstance(cand_res, Mapping) else {}
    base_statuses = {str(s) for s in base_res}
    cand_statuses = {str(s) for s in cand_res}
    for status in sorted(base_statuses - cand_statuses):
        _add(
            changes,
            ChangeKind.RESPONSE_STATUS_REMOVED,
            path=path,
            method=method,
            pointer=f"{op_pointer}/responses/{status}",
            detail=f"response status {status} removed",
            evidence=evidence,
        )
    for status in sorted(cand_statuses - base_statuses):
        _add(
            changes,
            ChangeKind.RESPONSE_STATUS_ADDED,
            path=path,
            method=method,
            pointer=f"{op_pointer}/responses/{status}",
            detail=f"response status {status} added",
            evidence=evidence,
        )
    for status in sorted(base_statuses & cand_statuses):
        base_item = base_res[status]
        cand_item = cand_res[status]
        _diff_schema(
            _media_schema(base_item) if isinstance(base_item, Mapping) else None,
            _media_schema(cand_item) if isinstance(cand_item, Mapping) else None,
            base_doc,
            cand_doc,
            side="response",
            path=path,
            method=method,
            base_pointer=f"{op_pointer}/responses/{status}",
            evidence=evidence,
            changes=changes,
        )

    base_body = base.raw.get("requestBody")
    cand_body = cand.raw.get("requestBody")
    if isinstance(base_body, Mapping) and not isinstance(cand_body, Mapping):
        _add(
            changes,
            ChangeKind.REQUEST_BODY_REMOVED,
            path=path,
            method=method,
            pointer=f"{op_pointer}/requestBody",
            detail="request body removed",
            evidence=evidence,
        )
        return
    if isinstance(cand_body, Mapping) and not isinstance(base_body, Mapping):
        required = cand_body.get("required") is True
        _add(
            changes,
            ChangeKind.REQUEST_BODY_ADDED if required else ChangeKind.UNCLASSIFIED,
            path=path,
            method=method,
            pointer=f"{op_pointer}/requestBody",
            detail="request body added" + ("" if required else " (optional)"),
            evidence=evidence,
        )
        return
    if isinstance(base_body, Mapping) and isinstance(cand_body, Mapping):
        _diff_schema(
            _media_schema(base_body),
            _media_schema(cand_body),
            base_doc,
            cand_doc,
            side="request",
            path=path,
            method=method,
            base_pointer=f"{op_pointer}/requestBody",
            evidence=evidence,
            changes=changes,
        )


def diff_contracts(
    baseline: OpenApiDocument, candidate: OpenApiDocument
) -> tuple[ContractChange, ...]:
    """Classify bounded changes between two contract versions."""
    changes: list[ContractChange] = []
    base_ops = {(op.method, op.path): op for op in baseline.operations}
    cand_ops = {(op.method, op.path): op for op in candidate.operations}

    for method, path in sorted(base_ops.keys() - cand_ops.keys(), key=lambda k: (k[1], k[0])):
        op = base_ops[(method, path)]
        _add(
            changes,
            ChangeKind.OPERATION_REMOVED,
            path=path,
            method=method,
            pointer=_pointer("paths", path, method),
            detail=f"operation {method.upper()} {path} removed",
            evidence=(op.fact_id,),
        )
    for method, path in sorted(cand_ops.keys() - base_ops.keys(), key=lambda k: (k[1], k[0])):
        op = cand_ops[(method, path)]
        _add(
            changes,
            ChangeKind.OPERATION_ADDED,
            path=path,
            method=method,
            pointer=_pointer("paths", path, method),
            detail=f"operation {method.upper()} {path} added",
            evidence=(op.fact_id,),
        )
    for key in sorted(base_ops.keys() & cand_ops.keys()):
        _diff_operation(base_ops[key], cand_ops[key], baseline, candidate, changes)

    changes.sort(key=lambda c: (c.code.value, c.path, c.method or "", c.pointer))
    return tuple(changes)
