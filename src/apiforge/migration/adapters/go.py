"""Go runtime migration adapter."""

from __future__ import annotations

from pathlib import Path

from apiforge.migration.adapters.base import AdapterObservation
from apiforge.migration.contracts import MigrationFinding, RuntimeCapability


class GoAdapter:
    ecosystem = "go"
    versions = frozenset({f"1.{minor}" for minor in range(18, 28)})

    def can_handle(self, source: str, target: str) -> bool:
        return source in self.versions and target in self.versions

    def discover(self, root: Path, source: str, target: str) -> AdapterObservation:
        files = tuple(
            str(path.relative_to(root))
            for path in sorted(root.rglob("go.mod"))
            if path.is_file()
        )
        findings: list[MigrationFinding] = []
        if not files:
            findings.append(
                MigrationFinding(
                    rule_id="AF-MIG-GO-001",
                    severity="high",
                    message="No go.mod detected",
                    source="go-adapter",
                    unresolved=("module path",),
                    blocking=True,
                )
            )
        capabilities = (
            RuntimeCapability(name="go-modules", available=bool(files), evidence=files),
            RuntimeCapability(
                name="race-and-fuzz",
                available=True,
                evidence=("go test -race", "go test -fuzz"),
                limitation="requires installed Go toolchain",
            ),
        )
        return AdapterObservation(
            files=files,
            capabilities=capabilities,
            findings=tuple(findings),
        )

    def commands(self, root: Path) -> tuple[tuple[str, ...], ...]:
        return (
            ("go", "version"),
            ("go", "mod", "tidy"),
            ("go", "test", "./..."),
            ("go", "test", "-race", "./..."),
        )
