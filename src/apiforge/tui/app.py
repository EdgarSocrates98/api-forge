"""Textual presentation layer; business state stays in application services."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from apiforge.application import runtime_experience
from apiforge.application.experience_projection import (
    project_doctor,
    project_review,
    project_status,
)

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical
    from textual.widgets import Footer, Header, Static, TabbedContent, TabPane
except ImportError as exc:  # pragma: no cover - exercised by fallback tests
    raise ImportError("Textual is required for the visual TUI") from exc


class ForgeApp(App[None]):
    """Execution-first screen with a governance panel and safe refresh action."""

    TITLE = "API Forge — execution control plane"
    CSS_PATH = "styles.tcss"
    BINDINGS: ClassVar[list[tuple[str, str, str]]] = [
        ("d", "doctor", "Doctor"),
        ("s", "status", "Status"),
        ("v", "review", "Review"),
        ("e", "evolve", "Evolve"),
        ("n", "resume", "Resume"),
        ("c", "cancel", "Cancel"),
        ("g", "governance", "Governance"),
        ("b", "debate", "Debate"),
        ("r", "refresh", "Refresh"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, *, root: Path, task_id: str) -> None:
        super().__init__()
        self.root = root
        self.task_id = task_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="execution"):
            with TabPane("Execution", id="execution"), Horizontal():
                with Vertical(id="execution-card"):
                    yield Static("Execution", classes="heading")
                    yield Static(id="status")
                with Vertical(id="governance-card"):
                    yield Static("Governance", classes="heading")
                    yield Static(id="governance-body")
            with TabPane("Evidence", id="evidence"):
                yield Static("Evidence navigation", classes="heading")
                yield Static(id="evidence-body")
            with TabPane("Capabilities", id="capabilities"):
                yield Static("Capability negotiation", classes="heading")
                yield Static("Use the expert capability commands to inspect host declarations.")
            with TabPane("Debate", id="debate"):
                yield Static("Adaptive debate", classes="heading")
                yield Static(id="debate-body")
        yield Footer()

    def on_mount(self) -> None:
        self.action_refresh()

    def _show_snapshot(self, loader: object) -> None:
        try:
            snapshot = loader(self.root, self.task_id, surface="textual")  # type: ignore[operator]
            view = snapshot.view
            routing = view.payload.get("routing")
            plan = view.payload.get("routing_plan")
            assessment = routing.get("risk_complexity") if isinstance(routing, dict) else None
            routing_lines = []
            if isinstance(assessment, dict):
                routing_lines.extend(
                    (
                        f"Complexity: {assessment.get('complexity', 'unknown')}",
                        f"Verification: {assessment.get('verification_depth', 'unknown')}",
                        f"Policy: {assessment.get('policy_version', 'unknown')}",
                    )
                )
            if isinstance(plan, dict):
                roles = [
                    str(plan.get("primary")) if plan.get("primary") is not None else "",
                    *(str(item) for item in plan.get("reviewers", ())),
                    str(plan.get("critic")) if plan.get("critic") is not None else "",
                    str(plan.get("referee")) if plan.get("referee") is not None else "",
                ]
                routing_lines.append(f"Roles: {', '.join(item for item in roles if item) or 'none'}")
            routing_summary = "\n".join(routing_lines)
            self.query_one("#status", Static).update(
                f"Task: {view.task_id}\nStatus: {view.status}\n"
                f"{view.summary or 'No summary'}\n"
                f"{routing_summary}"
            )
            self.query_one("#governance-body", Static).update(
                f"Evidence: {view.evidence.level}\n"
                f"Gaps: {', '.join(view.gaps) or 'none'}\n"
                f"Actions: {', '.join(view.actions)}"
            )
        except Exception as exc:  # noqa: BLE001 - surface a review state
            self.query_one("#status", Static).update(f"Status: REVIEW\nError: {exc}")

    def action_refresh(self) -> None:
        self._show_snapshot(project_status)

    def action_doctor(self) -> None:
        self._show_snapshot(project_doctor)

    def action_status(self) -> None:
        self._show_snapshot(project_status)

    def action_review(self) -> None:
        self._show_snapshot(project_review)

    def action_evolve(self) -> None:
        try:
            runtime_experience.evolve(self.root, self.task_id, requested_debate=False)
            self.action_refresh()
        except Exception as exc:  # noqa: BLE001 - surface review state
            self.query_one("#status", Static).update(f"Status: REVIEW\nError: {exc}")

    def action_resume(self) -> None:
        try:
            runtime_experience.resume(self.root, self.task_id)
            self.action_refresh()
        except Exception as exc:  # noqa: BLE001 - surface review state
            self.query_one("#status", Static).update(f"Status: REVIEW\nError: {exc}")

    def action_cancel(self) -> None:
        try:
            runtime_experience.cancel(self.root, self.task_id)
            self.action_refresh()
        except Exception as exc:  # noqa: BLE001 - surface review state
            self.query_one("#status", Static).update(f"Status: REVIEW\nError: {exc}")

    def action_governance(self) -> None:
        self.query_one(TabbedContent).active = "evidence"

    def action_debate(self) -> None:
        self.query_one(TabbedContent).active = "debate"
        self.query_one("#debate-body", Static).update(
            "Debate remains bounded by policy; use `apiforge debate` for submissions."
        )
