"""Rich renderer for ``apiforge install`` forge/* documents.

Mirrors the shared ui-kit ``format_status_doc`` layout — same sections,
same state vocabulary, same honesty (only real data is emitted) — but
drawn with Rich panels/tables for terminals that support it. Falls back
to the vendored stdlib renderer when Rich is unavailable.
"""

from __future__ import annotations

from typing import Any

_GOOD = {
    "ok",
    "pass",
    "healthy",
    "completed",
    "installed",
    "detected",
    "ready",
    "done",
    "supported",
}
_BAD = {"fail", "failed", "broken", "missing", "unsupported", "refused", "blocked"}
_WARN = {
    "degraded",
    "unverified",
    "planned",
    "skipped",
    "vendored",
    "not_installed",
    "pending",
    "modified",
    "declined",
}


def _style(state: str) -> str:
    s = state.lower()
    if s in _GOOD:
        return "green"
    if s in _BAD:
        return "red"
    if s in _WARN:
        return "yellow"
    return "dim"


def _fmt(value: Any) -> str:
    if isinstance(value, bool) or value is None:
        return "yes" if value else ""
    return str(value)


def render_doc_rich(doc: dict[str, Any]) -> bool:
    """Render ``doc`` via Rich. Returns False when Rich is unavailable."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text
    except ImportError:
        return False

    console = Console()
    op = doc.get("operation") or doc.get("command") or "status"
    status = str(doc.get("status", "?"))
    console.print()
    console.rule(
        Text(f" {doc.get('forge_id', 'forge')} · {op} ", style="bold")
        + Text(status.upper(), style=f"bold {_style(status)}")
    )

    for key, label in (
        ("target_root", "target"),
        ("scope", "scope"),
        ("version", "version"),
        ("state_dir", "state dir"),
    ):
        if doc.get(key):
            console.print(f"  [dim]{label:<10}[/] {doc[key]}")
    profile = (doc.get("context") or {}).get("profile") or doc.get("profile")
    if profile:
        console.print(f"  [dim]{'profile':<10}[/] {profile}")
    if doc.get("ledger_entries") is not None:
        console.print(f"  [dim]{'managed':<10}[/] {doc['ledger_entries']} entries")

    checks = doc.get("checks") or []
    if checks:
        table = Table(box=None, pad_edge=False, show_edge=False)
        table.add_column("", width=2, no_wrap=True)
        table.add_column("check", style="bold", no_wrap=True)
        table.add_column("status", no_wrap=True)
        table.add_column("detail")
        for c in checks:
            st = str(c.get("status", "?"))
            mark = {
                "PASS": "[green]✓[/]",
                "OK": "[green]✓[/]",
                "FAIL": "[red]✗[/]",
                "NOT_APPLICABLE": "[dim]—[/]",
            }.get(st.upper(), "[yellow]◇[/]")
            detail = str(c.get("detail") or "")
            if c.get("repairable"):
                detail += " [cyan](repairable)[/]"
            table.add_row(mark, str(c.get("id", "?")), f"[{_style(st)}]{st}[/]", detail)
        console.print(table)

    drift = doc.get("drift")
    if isinstance(drift, dict) and drift.get("ok") is not None:
        modified, missing = drift.get("modified") or [], drift.get("missing") or []
        console.print(
            f"  [green]ok {drift.get('ok', 0)}[/]  "
            f"[yellow]modified {len(modified)}[/]  [red]missing {len(missing)}[/]"
        )
        for entry in (modified + missing)[:6]:
            path = entry.get("path") if isinstance(entry, dict) else str(entry)
            kind = entry.get("status") if isinstance(entry, dict) else "?"
            console.print(f"    [dim]·[/] [{_style(str(kind))}]{kind}[/] {path}")

    files = doc.get("managed_files") or doc.get("planned_files")
    if files:
        label = "managed files" if doc.get("managed_files") is not None else "planned files"
        console.print(f"  [dim]{label}[/] {len(files)}")
        for f in files[:5]:
            path = f.get("path") if isinstance(f, dict) else str(f)
            console.print(f"    [dim]·[/] {path}")
        if len(files) > 5:
            console.print(f"    [dim]… {len(files) - 5} more[/]")

    portal = doc.get("forge_portal")
    if isinstance(portal, dict):
        state = str(portal.get("state", "?"))
        where = portal.get("install_root") or portal.get("manifest") or ""
        suffix = (
            f"  {where}"
            if where
            else ("  [dim]vendored assets — no local install[/]" if state == "vendored" else "")
        )
        console.print(f"  [dim]forge portal[/] [{_style(state)}]{state}[/]{suffix}")

    verification = doc.get("verification")
    if isinstance(verification, dict) and verification.get("status"):
        st = str(verification["status"])
        console.print(f"  [dim]verification[/] [{_style(st)}]{st.upper()}[/]")

    error = doc.get("error")
    if isinstance(error, dict) and (error.get("kind") or error.get("detail")):
        console.print(f"  [red]refused:[/] {error.get('kind', '')}")
        if error.get("detail"):
            console.print(f"    {error['detail']}")
        if error.get("unlock"):
            console.print(f"    [cyan]unlock:[/] {error['unlock']}")

    if doc.get("repair_hint"):
        console.print(f"  [cyan]repair:[/] {doc['repair_hint']}")
    console.print()
    return True


def render_doc(doc: dict[str, Any]) -> None:
    """Rich when available, vendored kit renderer otherwise."""
    if render_doc_rich(doc):
        return
    from apiforge.ui.kit import UIContext, format_status_doc

    print(format_status_doc(doc, ctx=UIContext.detect()))
