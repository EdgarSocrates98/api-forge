"""Capability discovery for optional gRPC toolchains."""

from __future__ import annotations

import shutil

from apiforge.contracts.grpc import GrpcCapability


def discover() -> tuple[GrpcCapability, ...]:
    tools = ("protoc", "buf", "envoy", "grpcurl")
    values = [
        GrpcCapability(name="fake", available=True, tool_version="builtin", mode="local_reversible")
    ]
    values.extend(
        GrpcCapability(
            name=tool,
            available=shutil.which(tool) is not None,
            mode="local_reversible",
            reason=None if shutil.which(tool) else "executable not found",
        )
        for tool in tools
    )
    return tuple(values)


def available(name: str) -> bool:
    return any(item.name == name and item.available for item in discover())
