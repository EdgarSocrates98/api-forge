"""Normalize gRPC source inputs without requiring protobuf runtime packages."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import cast

from apiforge.adapters.protobuf.descriptor import load_descriptor_set
from apiforge.contracts.grpc import GrpcIR
from apiforge.grpc.ir import build_ir


def load_source(path: Path) -> GrpcIR:
    if path.suffix == ".proto":
        return build_ir(path)
    if path.suffix in {".json", ".fds"}:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        loaded = load_descriptor_set(path)
        descriptor = loaded.get("descriptor")
        if isinstance(descriptor, dict):
            return _ir_from_descriptor(path, digest, descriptor)
        return GrpcIR(source_path=str(path), source_sha256=digest, descriptor_sha256=digest, provenance=(f"descriptor:{path}:{digest}",), unresolved=(str(loaded.get("reason", "descriptor-unresolved")),))
    raise ValueError(f"AF-GRPC-SOURCE: unsupported source {path}")


def _ir_from_descriptor(path: Path, digest: str, descriptor: dict[str, object]) -> GrpcIR:
    from apiforge.contracts.grpc import GrpcMessage, GrpcRpc, GrpcService, GrpcStreamMode

    package = str(descriptor.get("package", ""))
    raw_messages = cast(list[object], descriptor.get("messages", []))
    messages = tuple(GrpcMessage(name=str(item.get("name", "")), full_name=f"{package}.{item.get('name', '')}".strip(".")) for item in raw_messages if isinstance(item, dict))
    services: list[GrpcService] = []
    raw_services = cast(list[object], descriptor.get("services", []))
    for item in raw_services:
        if not isinstance(item, dict):
            continue
        service_name = str(item.get("name", ""))
        full_service = f"{package}.{service_name}".strip(".")
        rpcs: list[GrpcRpc] = []
        raw_rpcs = cast(list[object], item.get("rpcs", []))
        for rpc_item in raw_rpcs:
            if not isinstance(rpc_item, dict):
                continue
            client = bool(rpc_item.get("client_streaming", False))
            server = bool(rpc_item.get("server_streaming", False))
            mode = GrpcStreamMode.BIDI if client and server else GrpcStreamMode.CLIENT if client else GrpcStreamMode.SERVER if server else GrpcStreamMode.UNARY
            rpc_name = str(rpc_item.get("name", ""))
            rpcs.append(GrpcRpc(name=rpc_name, full_name=f"{full_service}/{rpc_name}", request_type=str(rpc_item.get("request", "")), response_type=str(rpc_item.get("response", "")), stream_mode=mode, http_method=str(rpc_item["http_method"]) if rpc_item.get("http_method") else None, http_path=str(rpc_item["http_path"]) if rpc_item.get("http_path") else None, source_path=str(path)))
        services.append(GrpcService(name=service_name, full_name=full_service, rpcs=tuple(rpcs)))
    return GrpcIR(package=package, source_path=str(path), source_sha256=digest, messages=messages, services=tuple(services), descriptor_sha256=digest, provenance=(f"descriptor:{path}:{digest}",))
