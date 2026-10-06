"""Canonical gRPC intermediate representation builders."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Literal, cast

from apiforge.contracts.grpc import (
    GrpcField,
    GrpcIR,
    GrpcMessage,
    GrpcRpc,
    GrpcService,
    GrpcStreamMode,
)

_MESSAGE = re.compile(r"\bmessage\s+(\w+)\s*\{")
_SERVICE = re.compile(r"\bservice\s+(\w+)\s*\{")
_RPC = re.compile(
    r"\brpc\s+(\w+)\s*\(\s*(stream\s+)?([\w.]+)\s*\)\s*returns\s*\(\s*(stream\s+)?([\w.]+)"
)
_FIELD = re.compile(r"^\s*(optional|required|repeated)?\s*([\w.]+)\s+(\w+)\s*=\s*(\d+)")
_ENUM = re.compile(r"\benum\s+(\w+)\s*\{")
_ENUM_VALUE = re.compile(r"^\s*(\w+)\s*=\s*-?\d+")
_HTTP = re.compile(r"(?i)(get|post|put|patch|delete):\s*\"([^\"]+)\"")


def _clean(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", "", text)


def build_ir(path: Path, descriptor_sha256: str | None = None) -> GrpcIR:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    text = _clean(raw.decode("utf-8"))
    package_match = re.search(r"\bpackage\s+([\w.]+)\s*;", text)
    package = package_match.group(1) if package_match else ""
    messages: list[GrpcMessage] = []
    lines = text.splitlines()
    for match in _MESSAGE.finditer(text):
        start = text[: match.start()].count("\n")
        depth = 0
        body: list[str] = []
        for line in lines[start:]:
            depth += line.count("{") - line.count("}")
            if body or "{" in line:
                body.append(line)
            if body and depth <= 0:
                break
        fields: list[GrpcField] = []
        for line in body:
            field = _FIELD.match(line)
            if field:
                label, type_name, name, number = field.groups()
                field_label = cast(Literal["optional", "required", "repeated"], label or "optional")
                fields.append(
                    GrpcField(
                        name=name,
                        number=int(number),
                        type_name=type_name,
                        label=field_label,
                    )
                )
        full_name = f"{package}.{match.group(1)}" if package else match.group(1)
        messages.append(GrpcMessage(name=match.group(1), full_name=full_name, fields=tuple(fields)))
    services: list[GrpcService] = []
    for service_match in _SERVICE.finditer(text):
        start = text[: service_match.start()].count("\n")
        depth = 0
        service_body: list[str] = []
        for line in lines[start:]:
            depth += line.count("{") - line.count("}")
            if service_body or "{" in line:
                service_body.append(line)
            if service_body and depth <= 0:
                break
        rpcs: list[GrpcRpc] = []
        service_text = "\n".join(service_body)
        for line in service_body:
            rpc = _RPC.search(line)
            if rpc:
                name, client, request, server, response = rpc.groups()
                mode = (
                    GrpcStreamMode.BIDI
                    if client and server
                    else GrpcStreamMode.CLIENT
                    if client
                    else GrpcStreamMode.SERVER
                    if server
                    else GrpcStreamMode.UNARY
                )
                full_service = (
                    f"{package}.{service_match.group(1)}" if package else service_match.group(1)
                )
                http_method: str | None = None
                http_path: str | None = None
                line_offset = service_text.find(line)
                annotation = (
                    _HTTP.search(service_text[line_offset : line_offset + 400])
                    if line_offset >= 0
                    else None
                )
                if annotation:
                    http_method, http_path = annotation.group(1).upper(), annotation.group(2)
                rpcs.append(
                    GrpcRpc(
                        name=name,
                        full_name=f"{full_service}/{name}",
                        request_type=request,
                        response_type=response,
                        stream_mode=mode,
                        source_path=str(path),
                        source_line=start + 1,
                        http_method=http_method,
                        http_path=http_path,
                    )
                )
        full_service = f"{package}.{service_match.group(1)}" if package else service_match.group(1)
        services.append(
            GrpcService(name=service_match.group(1), full_name=full_service, rpcs=tuple(rpcs))
        )
    imports = tuple(sorted(re.findall(r'\bimport\s+(?:public\s+|weak\s+)?"([^"]+)"\s*;', text)))
    enum_values: dict[str, tuple[str, ...]] = {}
    for enum_match in _ENUM.finditer(text):
        enum_name = enum_match.group(1)
        enum_start = text[: enum_match.start()].count("\n")
        enum_depth = 0
        values: list[str] = []
        for enum_line in lines[enum_start:]:
            enum_depth += enum_line.count("{") - enum_line.count("}")
            value_match = _ENUM_VALUE.match(enum_line)
            if value_match:
                values.append(value_match.group(1))
            if enum_depth <= 0 and values:
                break
        enum_values[enum_name] = tuple(values)
    enums = tuple(sorted(enum_values))
    unresolved = tuple(f"import:{item}" for item in imports if not (path.parent / item).is_file())
    return GrpcIR(
        package=package,
        source_path=str(path),
        source_sha256=digest,
        imports=imports,
        messages=tuple(messages),
        services=tuple(services),
        enums=enums,
        enum_values=enum_values,
        descriptor_sha256=descriptor_sha256,
        unresolved=unresolved,
        provenance=(f"file:{path}:{digest}",),
    )
