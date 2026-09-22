"""Provider-neutral application facade shared by CLI and MCP projections."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apiforge.adapters.fastapi.extractor import extract_fastapi
from apiforge.adapters.go.extractor import extract_go
from apiforge.adapters.spring.extractor import extract_spring
from apiforge.application.analyze import AnalysisResult, analyze_project

_EXTRACTORS = {"fastapi": extract_fastapi, "spring": extract_spring, "go": extract_go}


class ApiForgePlatform:
    """Stable use-case facade; transports only project its results."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root or Path.cwd()).resolve()

    def discover(self, project: Path, *, framework: str = "fastapi") -> dict[str, Any]:
        from apiforge.index.cache import extract_cached

        extractor = _EXTRACTORS.get(framework)
        if extractor is None:
            raise ValueError(f"AF-INPUT-FRAMEWORK-UNKNOWN: {framework}")
        inventory, cache = extract_cached(
            Path(project), framework, extractor, self.root / ".apiforge" / "cache", ledger_root=self.root
        )
        return {
            "cache": cache,
            "framework": inventory.framework,
            "routes": [fact.model_dump(mode="json") for fact in inventory.facts],
            "diagnostics": [diagnostic.model_dump(mode="json") for diagnostic in inventory.diagnostics],
            "input_hashes": dict(inventory.input_hashes),
            "execution": inventory.execution.model_dump(mode="json") if inventory.execution else None,
        }

    def analyze(
        self,
        contract: Path,
        project: Path,
        out_dir: Path,
        *,
        baseline: Path | None = None,
        framework: str = "auto",
    ) -> AnalysisResult:
        return analyze_project(
            contract, project, baseline, out_dir, framework=framework,
            cache_dir=self.root / ".apiforge" / "cache", ledger_root=self.root,
        )
