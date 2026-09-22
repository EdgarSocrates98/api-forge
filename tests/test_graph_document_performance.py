from pathlib import Path

from apiforge.adapters.dbaccess import extract_mongo, extract_neptune_access
from apiforge.data_governance import build_data_performance_profile

ROOT = Path(__file__).parent / "fixtures" / "dbaccess_app"


def test_mongo_profile_surfaces_document_write_risk() -> None:
    profile = build_data_performance_profile(extract_mongo(ROOT), database="mongo")
    assert profile.latency_class == "document"
    assert "unfiltered-write" in profile.risk_findings


def test_neptune_profile_surfaces_unbounded_traversal() -> None:
    profile = build_data_performance_profile(
        extract_neptune_access(ROOT), database="neptune"
    )
    assert profile.latency_class == "graph"
    assert "unbounded-graph-traversal" in profile.risk_findings
