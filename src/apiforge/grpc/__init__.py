"""Offline-first gRPC contract control plane."""

from apiforge.grpc.compatibility import compare
from apiforge.grpc.ir import build_ir
from apiforge.grpc.source import load_source

__all__ = ["build_ir", "compare", "load_source"]
