"""Bounded context resolution over repository and virtual workspace scopes."""

from apiforge.context.resolver import resolve_scope, resolve_targets
from apiforge.context.scopes import validate_scope
from apiforge.context.service import ContextService

__all__ = ["ContextService", "resolve_scope", "resolve_targets", "validate_scope"]
