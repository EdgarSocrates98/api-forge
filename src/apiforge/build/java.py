"""Synthesize Spring Boot endpoint skeletons from an OpenAPI operation.

Bounded and deterministic: new files only, under
``src/main/java/com/apiforge/generated/`` — a build never edits an
existing file, never infers a type it cannot map.
"""

from __future__ import annotations

import re
from typing import Any

from apiforge.openapi.models import OpenApiDocument, OpenApiOperation

_BASE = "src/main/java/com/apiforge/generated"
_METHOD_ANNOTATIONS = {
    "get": "GetMapping",
    "post": "PostMapping",
    "put": "PutMapping",
    "delete": "DeleteMapping",
    "patch": "PatchMapping",
}


class BuildError(Exception):
    """Named refusal from the builder."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _pascal(name: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", name)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _camel(name: str) -> str:
    pascal = _pascal(name)
    return pascal[:1].lower() + pascal[1:]


def _ref_name(schema: Any) -> str | None:
    if isinstance(schema, dict):
        ref = schema.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            return ref.rsplit("/", 1)[-1]
    return None


def _java_type(schema: Any, imports: set[str], ctx: str) -> str:
    """Map a JSON schema node to a Java type; refuse what we cannot map."""
    if not isinstance(schema, dict):
        raise BuildError("AF-BUILD-SCHEMA-MISSING", f"{ctx}: schema node is not an object")
    ref = _ref_name(schema)
    if ref is not None:
        return ref
    stype = schema.get("type")
    if stype == "string":
        return "String"
    if stype == "integer":
        return "Long"
    if stype == "number":
        imports.add("import java.math.BigDecimal;")
        return "BigDecimal"
    if stype == "boolean":
        return "Boolean"
    if stype == "array":
        imports.add("import java.util.List;")
        return f"List<{_java_type(schema.get('items'), imports, ctx + '.items')}>"
    if stype == "object":
        imports.add("import java.util.Map;")
        return "Map<String, Object>"
    raise BuildError("AF-BUILD-SCHEMA-MISSING", f"{ctx}: cannot map type {stype!r}")


def _content_schema(node: Any) -> Any | None:
    if not isinstance(node, dict):
        return None
    content = node.get("content")
    if not isinstance(content, dict):
        return None
    for media in ("application/json",):
        media_obj = content.get(media)
        if isinstance(media_obj, dict):
            return media_obj.get("schema")
    for media_obj in content.values():
        if isinstance(media_obj, dict) and "schema" in media_obj:
            return media_obj["schema"]
    return None


def _response_type(raw: dict[str, Any], imports: set[str]) -> str:
    responses = raw.get("responses")
    if not isinstance(responses, dict):
        return "Void"
    for code, response in sorted(responses.items()):
        if not str(code).startswith("2"):
            continue
        schema = _content_schema(response)
        if schema is None:
            continue
        return _java_type(schema, imports, f"responses.{code}")
    return "Void"


def _request_body_type(raw: dict[str, Any], imports: set[str]) -> str | None:
    body = raw.get("requestBody")
    if not isinstance(body, dict) or not body.get("required"):
        return None
    schema = _content_schema(body)
    if schema is None:
        return None
    return _java_type(schema, imports, "requestBody")


def _dto_schemas(document: OpenApiDocument, needed: set[str]) -> dict[str, str]:
    """Render each needed component schema as a Java record."""
    schemas = document.components.get("schemas")
    out: dict[str, str] = {}
    for name in sorted(needed):
        node = schemas.get(name) if isinstance(schemas, dict) else None
        if not isinstance(node, dict):
            raise BuildError(
                "AF-BUILD-SCHEMA-MISSING", f"components.schemas.{name} is not an object"
            )
        imports: set[str] = set()
        props = node.get("properties")
        components: list[str] = []
        if isinstance(props, dict):
            for prop, pschema in props.items():
                jtype = _java_type(pschema, imports, f"{name}.{prop}")
                components.append(f"{jtype} {_camel(prop)}")
        header = "package com.apiforge.generated.dto;\n\n"
        body = f"public record {name}({', '.join(components)}) {{}}\n"
        out[name] = (
            header + ("".join(f"{i}\n" for i in sorted(imports)) + "\n" if imports else "") + body
        )
    return out


def _find_operation(document: OpenApiDocument, operation_id: str) -> OpenApiOperation:
    for op in document.operations:
        if op.operation_id == operation_id:
            return op
    raise BuildError(
        "AF-BUILD-OP-MISSING", f"no operationId {operation_id!r} in {document.source_path}"
    )


def operation_to_sources(document: OpenApiDocument, operation_id: str) -> dict[str, str]:
    """Map one contract operation to new-file Java sources."""
    operation = _find_operation(document, operation_id)
    raw = dict(operation.raw)
    annotation = _METHOD_ANNOTATIONS.get(operation.method)
    if annotation is None:
        raise BuildError("AF-BUILD-OP-MISSING", f"unsupported method {operation.method!r}")

    imports: set[str] = set()
    response = _response_type(raw, imports)
    body_type = _request_body_type(raw, imports)
    path_vars = re.findall(r"\{([^}/]+)\}", operation.path)

    params = [f'@PathVariable("{v}") String {_camel(v)}' for v in path_vars]
    if body_type is not None:
        params.append(f"@RequestBody {body_type} body")
    dto_needed = _collect_refs(raw.get("requestBody")) | _collect_refs(raw.get("responses"))
    dtos = _dto_schemas(document, dto_needed)

    class_name = _pascal(operation_id) + "Controller"
    method_name = _camel(operation_id)
    lines = [
        "package com.apiforge.generated;",
        "",
        *sorted(imports),
        "",
        "import com.apiforge.generated.dto.*;",
        "import org.springframework.http.ResponseEntity;",
        "import org.springframework.web.bind.annotation.*;",
        "",
        "@RestController",
        f"public class {class_name} {{",
        "",
        f'    @{annotation}("{operation.path}")',
        f"    public ResponseEntity<{response}> {method_name}({', '.join(params)}) {{",
        "        return ResponseEntity.ok(null);",
        "    }",
        "}",
        "",
    ]
    controller = "\n".join(lines)

    sources: dict[str, str] = {f"{_BASE}/{class_name}.java": controller}
    for name, content in dtos.items():
        sources[f"{_BASE}/dto/{name}.java"] = content
    return dict(sorted(sources.items()))


def _collect_refs(node: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(node, dict):
        ref = _ref_name(node)
        if ref is not None:
            refs.add(ref)
        for value in node.values():
            refs |= _collect_refs(value)
    elif isinstance(node, (list, tuple)):
        for item in node:
            refs |= _collect_refs(item)
    return refs
