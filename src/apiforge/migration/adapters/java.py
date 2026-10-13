"""Java runtime migration adapter."""

from __future__ import annotations

from pathlib import Path

from apiforge.migration.adapters.base import AdapterObservation
from apiforge.migration.contracts import MigrationFinding, RuntimeCapability


class JavaAdapter:
    ecosystem = "java"
    versions = frozenset({"11", "17", "21", "25"})

    def can_handle(self, source: str, target: str) -> bool:
        return source in self.versions and target in self.versions

    def discover(self, root: Path, source: str, target: str) -> AdapterObservation:
        names = {"pom.xml", "build.gradle", "build.gradle.kts", "gradle.properties"}
        files = tuple(
            str(path.relative_to(root))
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.name in names
        )
        findings: list[MigrationFinding] = []
        if not files:
            findings.append(
                MigrationFinding(
                    rule_id="AF-MIG-JAVA-001",
                    severity="high",
                    message="No Maven or Gradle manifest detected",
                    source="java-adapter",
                    unresolved=("build tool",),
                    blocking=True,
                )
            )
        if source == target:
            findings.append(
                MigrationFinding(
                    rule_id="AF-MIG-RUNTIME-001",
                    severity="info",
                    message="Source and target Java versions are equal",
                    source="java-adapter",
                )
            )
        capabilities = (
            RuntimeCapability(
                name="jdeps-jdeprscan",
                available=True,
                evidence=("optional command adapter",),
                limitation="availability must be verified in execution environment",
            ),
            RuntimeCapability(name="maven-gradle", available=bool(files), evidence=files),
        )
        return AdapterObservation(
            files=files,
            capabilities=capabilities,
            findings=tuple(findings),
        )

    def commands(self, root: Path) -> tuple[tuple[str, ...], ...]:
        return (
            ("java", "-version"),
            ("jdeps", "--version"),
            ("jdeprscan", "--release", "21", "--help"),
        )
