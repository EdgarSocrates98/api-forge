"""Agent-operations compatibility layer for API Forge hosts."""

from apiforge.agentops.compact import (
    CavemanMode,
    CompactedOutput,
    compact_file,
    compact_text,
)

__all__ = ["CavemanMode", "CompactedOutput", "compact_file", "compact_text"]
