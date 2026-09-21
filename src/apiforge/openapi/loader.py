"""Safe, deterministic loading of OpenAPI 3.1 documents.

The document is parsed under the strict YAML/JSON rules of
:mod:`apiforge.core.yaml` — aliases, merge keys, custom tags, duplicate keys
and non-finite JSON numbers are all refused by name. Paths are preserved
verbatim: ``/orders`` and ``/orders/`` are distinct operations, exactly as
FastAPI treats them.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from apiforge.core.ids import stable_id
from apiforge.core.io import sha256_file
from apiforge.core.models import Diagnostic, FindingStatus, SourceRef
from apiforge.core.yaml import StrictLoadError, load_data_file
from apiforge.openapi.models import OpenApiDocument, OpenApiOperation

HTTP_METHODS = frozenset({"get", "put", "post", "delete", "options", "head", "patch", "trace"})
_PATH_ITEM_FIELDS = frozenset({"$ref", "summary", "description", "parameters", "servers"})
_VERSION_31 = re.compile(r"^3\.1(\.\d+)?$")


class OpenApiLoadError(ValueError):
    """A named contract loading failure; ``str()`` begins with the code."""

    def __init__(self, code: str, message: str, path: Path | None = None) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code}: {message}")


def _expect_mapping(value: object, field: str, path: Path) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise OpenApiLoadError("AF-OPENAPI-SCHEMA", f"{path.name}: {field} must be a mapping", path)
    return value


def _operations(
    paths: Mapping[str, Any], source_path: str, digest: str, path: Path
) -> tuple[tuple[OpenApiOperation, ...], tuple[Diagnostic, ...]]:
    operations: list[OpenApiOperation] = []
    diagnostics: list[Diagnostic] = []
    seen: set[tuple[str, str]] = set()
    for path_key, item in paths.items():
        if not isinstance(path_key, str):
            raise OpenApiLoadError(
                "AF-OPENAPI-SCHEMA", f"{path.name}: path keys must be strings", path
            )
        item_map = _expect_mapping(item, f"paths[{path_key!r}]", path)
        if "$ref" in item_map:
            diagnostics.append(
                Diagnostic(
                    code="AF-OPENAPI-UNSUPPORTED",
                    status=FindingStatus.UNRESOLVED,
                    message=f"path item {path_key!r} uses $ref; not resolved",
                    source=SourceRef(path=source_path, sha256=digest, extractor="openapi"),
                )
            )
            continue
        for key, raw in item_map.items():
            method = key.lower() if isinstance(key, str) else ""
            if method not in HTTP_METHODS:
                if key not in _PATH_ITEM_FIELDS:
                    diagnostics.append(
                        Diagnostic(
                            code="AF-OPENAPI-UNSUPPORTED",
                            status=FindingStatus.UNRESOLVED,
                            message=f"{path_key!r}: unsupported path item key {key!r}",
                            source=SourceRef(path=source_path, sha256=digest, extractor="openapi"),
                        )
                    )
                continue
            operation_map = _expect_mapping(raw, f"paths[{path_key!r}].{key}", path)
            pair = (method, path_key)
            if pair in seen:
                raise OpenApiLoadError(
                    "AF-OPENAPI-DUPLICATE-OPERATION",
                    f"{path.name}: duplicate operation {method.upper()} {path_key}",
                    path,
                )
            seen.add(pair)
            operation_id = operation_map.get("operationId")
            operations.append(
                OpenApiOperation(
                    method=method,
                    path=path_key,
                    operation_id=operation_id if isinstance(operation_id, str) else None,
                    source=SourceRef(path=source_path, sha256=digest, extractor="openapi"),
                    raw=dict(operation_map),
                    fact_id=stable_id(
                        "fact",
                        {
                            "kind": "contract.operation",
                            "document": digest,
                            "method": method,
                            "path": path_key,
                        },
                    ),
                )
            )
    operations.sort(key=lambda op: (op.path, op.method))
    return tuple(operations), tuple(diagnostics)


def load_openapi(path: Path) -> OpenApiDocument:
    """Load an OpenAPI 3.1 document into a normalized, hashed document."""
    target = Path(path)
    digest = sha256_file(target)
    try:
        data = load_data_file(target)
    except StrictLoadError as exc:
        code = (
            "AF-OPENAPI-INVALID-JSON"
            if target.suffix.lower() == ".json"
            else "AF-OPENAPI-INVALID-YAML"
        )
        raise OpenApiLoadError(code, f"{target.name}: {exc}", path) from exc
    if not isinstance(data, Mapping):
        raise OpenApiLoadError(
            "AF-OPENAPI-NOT-MAPPING", f"{target.name}: document root must be a mapping", path
        )
    version = data.get("openapi")
    if not isinstance(version, str) or not _VERSION_31.match(version):
        raise OpenApiLoadError(
            "AF-OPENAPI-UNSUPPORTED-VERSION",
            f"{target.name}: openapi must be 3.1.x, got {version!r}",
            path,
        )
    paths = _expect_mapping(data.get("paths"), "paths", target)
    components = _expect_mapping(data.get("components"), "components", target)
    source_path = target.as_posix()
    operations, diagnostics = _operations(paths, source_path, digest, target)
    return OpenApiDocument(
        version=version,
        source_path=source_path,
        sha256=digest,
        operations=operations,
        components=dict(components),
        diagnostics=diagnostics,
    )
