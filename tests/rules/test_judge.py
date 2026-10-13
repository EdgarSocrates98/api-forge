from apiforge.api_ir.models import ApiModel
from apiforge.core.models import FindingStatus, Severity
from apiforge.rules.judge import judge_api_model, load_catalog


def test_missing_implementation_is_confirmed(api_model: ApiModel) -> None:
    findings = judge_api_model(api_model)
    finding = next(f for f in findings if f.rule_id == "AF-CONTRACT-001")
    assert finding.status == FindingStatus.CONFIRMED
    assert finding.evidence == ("fact:c-post",)


def test_duplicate_implementation_is_reported(
    api_model_with_duplicate_post: ApiModel,
) -> None:
    findings = judge_api_model(api_model_with_duplicate_post)
    finding = next(f for f in findings if f.rule_id == "AF-CODE-001")
    assert len(finding.evidence) == 2
    assert finding.status == FindingStatus.CONFIRMED


def test_dynamic_route_yields_unresolved_finding(
    api_model_with_dynamic_route: ApiModel,
) -> None:
    findings = judge_api_model(api_model_with_dynamic_route)
    assert any(
        f.rule_id == "AF-CODE-003" and f.status == FindingStatus.UNRESOLVED for f in findings
    )


def test_uncertainty_makes_absence_unresolved_not_confirmed(
    api_model_with_dynamic_route: ApiModel,
) -> None:
    findings = judge_api_model(api_model_with_dynamic_route)
    finding = next(f for f in findings if f.rule_id == "AF-CONTRACT-001")
    assert finding.status == FindingStatus.UNRESOLVED
    assert "AF-FASTAPI-DYNAMIC-ROUTE" in finding.detail


def test_code_only_route_is_reported(api_model_with_code_only_route: ApiModel) -> None:
    findings = judge_api_model(api_model_with_code_only_route)
    finding = next(f for f in findings if f.rule_id == "AF-CODE-002")
    assert finding.status == FindingStatus.CONFIRMED
    assert finding.evidence == ("fact:k-del",)


def test_matched_get_produces_nothing(api_model: ApiModel) -> None:
    findings = judge_api_model(api_model)
    get_related = [f for f in findings if "c-get" in str(f.evidence) or "k-get" in str(f.evidence)]
    assert get_related == []


def test_catalog_loads_from_package_data() -> None:
    catalog = load_catalog()
    assert set(catalog) >= {
        "AF-CONTRACT-001",
        "AF-CODE-001",
        "AF-CODE-002",
        "AF-CODE-003",
    }
    for meta in catalog.values():
        assert meta.title and meta.remediation
        assert meta.severity in set(Severity)


def test_finding_ids_are_stable_and_sorted(api_model: ApiModel) -> None:
    first = judge_api_model(api_model)
    second = judge_api_model(api_model)
    assert [f.finding_id for f in first] == [f.finding_id for f in second]
    ranks = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    keys = [(ranks[f.severity], f.rule_id, f.finding_id) for f in first]
    assert keys == sorted(keys)
