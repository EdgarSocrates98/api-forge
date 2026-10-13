"""Python runtime migration adapter."""

from __future__ import annotations

from pathlib import Path

from apiforge.migration.adapters.base import AdapterObservation
from apiforge.migration.contracts import MigrationFinding, RuntimeCapability


class PythonAdapter:
    ecosystem = "python"
    versions = frozenset({"2", "3", "3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "3.14"})

    def can_handle(self, source: str, target: str) -> bool:
        return source in self.versions and target in self.versions

    def discover(self, root: Path, source: str, target: str) -> AdapterObservation:
        names = {
            "pyproject.toml",
            "setup.py",
            "setup.cfg",
            "requirements.txt",
            "Pipfile",
            "poetry.lock",
            "uv.lock",
        }
        files = tuple(
            str(path.relative_to(root))
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.name in names
        )
        findings: list[MigrationFinding] = []
        if source == "2" and target != "2":
            findings.append(
                MigrationFinding(
                    rule_id="AF-MIG-PY-001",
                    severity="high",
                    message="Python 2 to 3 requires syntax, dependency and runtime review",
                    source="python-adapter",
                    unresolved=("legacy syntax", "dependency support", "native extensions"),
                    blocking=True,
                )
            )
        if not files:
            findings.append(
                MigrationFinding(
                    rule_id="AF-MIG-PY-002",
                    severity="high",
                    message="No Python packaging manifest detected",
                    source="python-adapter",
                    unresolved=("package manager",),
                    blocking=True,
                )
            )
        capabilities = (
            RuntimeCapability(
                name="python-toolchain",
                available=True,
                evidence=("python --version adapter",),
                limitation="target interpreter availability must be verified",
            ),
            RuntimeCapability(name="packaging", available=bool(files), evidence=files),
        )
        return AdapterObservation(
            files=files,
            capabilities=capabilities,
            findings=tuple(findings),
        )

    def commands(self, root: Path) -> tuple[tuple[str, ...], ...]:
        return (
            ("python", "--version"),
            ("python", "-m", "pip", "check"),
            ("python", "-m", "compileall", "."),
        )
