"""Emit new-file unified-diff patches from synthesized sources."""

from __future__ import annotations


def sources_to_diff(sources: dict[str, str]) -> str:
    """One ``new file`` patch per source, sorted by path."""
    chunks: list[str] = []
    for path in sorted(sources):
        lines = sources[path].splitlines()
        chunks.append(f"diff --git a/{path} b/{path}")
        chunks.append("new file mode 100644")
        chunks.append("--- /dev/null")
        chunks.append(f"+++ b/{path}")
        chunks.append(f"@@ -0,0 +1,{len(lines)} @@")
        chunks.extend(f"+{line}" for line in lines)
    return "\n".join(chunks) + "\n"
