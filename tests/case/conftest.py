import pytest

from apiforge.api_ir.models import ApiModel, ApiOperation, Projection
from apiforge.case.models import CasePayload
from apiforge.core.models import (
    Diagnostic,
    Fact,
    Finding,
    FindingStatus,
    Severity,
    SourceRef,
)


def _source(path: str = "app/routes/orders.py", line: int = 1) -> SourceRef:
    return SourceRef(path=path, sha256="a" * 64, line=line, extractor="test")


@pytest.fixture
def case_payload(tmp_path_factory) -> CasePayload:
    contract_source = _source("contracts/orders.yaml", None)
    projection = Projection(source_kind="contract", fact_id="fact:c1", source=contract_source)
    model = ApiModel(
        generator="apiforge 0.1.0",
        input_hashes={"contract:contracts/orders.yaml": "a" * 64},
        operations=(
            ApiOperation(
                method="get",
                path="/orders",
                contract_projections=(projection,),
            ),
        ),
    )
    fact = Fact(
        fact_id="fact:k1",
        kind="code.route",
        source=_source(),
        measures={"method": "get", "path": "/orders"},
    )
    finding = Finding(
        finding_id="finding:x",
        rule_id="AF-CONTRACT-001",
        status=FindingStatus.CONFIRMED,
        severity=Severity.HIGH,
        title="missing",
        evidence=("fact:c1",),
    )
    diagnostic = Diagnostic(
        code="AF-FASTAPI-DYNAMIC-ROUTE",
        status=FindingStatus.UNRESOLVED,
        message="dynamic",
        source=_source(line=9),
    )
    project = tmp_path_factory.mktemp("project")
    return CasePayload(
        contract_path="contracts/orders.yaml",
        project_path=str(project),
        model=model,
        facts=(fact,),
        findings=(finding,),
        diagnostics=(diagnostic,),
    )
