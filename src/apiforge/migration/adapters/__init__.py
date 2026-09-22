"""Static runtime adapters."""

from apiforge.migration.adapters.go import GoAdapter
from apiforge.migration.adapters.java import JavaAdapter
from apiforge.migration.adapters.python import PythonAdapter

ADAPTERS = (JavaAdapter(), PythonAdapter(), GoAdapter())

__all__ = ["ADAPTERS", "GoAdapter", "JavaAdapter", "PythonAdapter"]
