"""Agent-operations compatibility layer for API Forge hosts."""

from apiforge.agentops.compact import (
    CavemanMode,
    CompactedOutput,
    compact_file,
    compact_text,
)
from apiforge.agentops.evals import evaluate_compaction
from apiforge.agentops.filters import CommandFilter, get_filter, list_filters
from apiforge.agentops.hosts import list_hosts
from apiforge.agentops.tools import ToolAdapter, get_tool_adapter, list_tool_adapters
from apiforge.agentops.workflows import Workflow, list_workflows, plan_workflow

__all__ = [
    "CavemanMode",
    "CommandFilter",
    "CompactedOutput",
    "ToolAdapter",
    "Workflow",
    "compact_file",
    "compact_text",
    "evaluate_compaction",
    "get_filter",
    "get_tool_adapter",
    "list_filters",
    "list_hosts",
    "list_tool_adapters",
    "list_workflows",
    "plan_workflow",
]
