"""Streaming semantics and bounded runtime analysis."""

from __future__ import annotations

from apiforge.contracts.grpc import GrpcIR, GrpcRuntimePolicy, GrpcStreamMode


def analyze_streams(ir: GrpcIR, policy: GrpcRuntimePolicy) -> dict[str, object]:
    modes = {mode.value: 0 for mode in GrpcStreamMode}
    for service in ir.services:
        for rpc in service.rpcs:
            modes[rpc.stream_mode.value] += 1
    return {
        "modes": modes,
        "max_message_bytes": policy.max_message_bytes,
        "max_stream_duration_s": policy.max_stream_duration_s,
        "bounded": True,
    }
