from pathlib import Path

from apiforge.adapters.dbaccess import extract_dynamo_access
from apiforge.adapters.redis_.extract import extract_redis
from apiforge.data_governance import build_data_performance_profile

ROOT = Path(__file__).parent / "fixtures"


def test_redis_profile_surfaces_ttl_risk() -> None:
    profile = build_data_performance_profile(extract_redis(ROOT / "redis_app"), database="redis")
    assert profile.latency_class == "low_latency"
    assert "write-without-declared-ttl" in profile.risk_findings


def test_dynamo_profile_surfaces_scan_and_key_risks() -> None:
    profile = build_data_performance_profile(
        extract_dynamo_access(ROOT / "dbaccess_app"), database="dynamo"
    )
    assert profile.latency_class == "partitioned_scale"
    assert "full-scan" in profile.risk_findings
