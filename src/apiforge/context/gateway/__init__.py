"""Context Gateway: minimal sufficient evidence as ContextCapsule/v1 + ctx:// refs."""

from apiforge.context.gateway.capsule import build_capsule, emit, expand_ref
from apiforge.context.gateway.refs import CtxStore

__all__ = ["CtxStore", "build_capsule", "emit", "expand_ref"]
