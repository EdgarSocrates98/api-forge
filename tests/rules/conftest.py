import pytest

from apiforge.api_ir.models import ApiModel, ApiOperation, Projection
from apiforge.core.models import Diagnostic, FindingStatus, SourceRef


def _proj(kind: str, fact_id: str, path: str = "app/routes/orders.py", line: int = 1) -> Projection:
    return Projection(
        source_kind=kind,
        fact_id=fact_id,
        source=SourceRef(path=path, sha256="a" * 64, line=line, extractor="test"),
    )


def _op(method: str, path: str, contract=(), code=()) -> ApiOperation:
    return ApiOperation(
        method=method,
        path=path,
        contract_projections=contract,
        code_projections=code,
    )


def _diag(code: str, line: int = 10) -> Diagnostic:
    return Diagnostic(
        code=code,
        status=FindingStatus.UNRESOLVED,
        message=f"{code} occurred",
        source=SourceRef(
            path="app/routes/orders.py", sha256="b" * 64, line=line, extractor="fastapi"
        ),
    )


@pytest.fixture
def api_model() -> ApiModel:
    return ApiModel(
        generator="apiforge 0.1.0",
        operations=(
            _op(
                "get",
                "/orders",
                contract=(_proj("contract", "fact:c-get", path="orders-v1.yaml"),),
                code=(_proj("code", "fact:k-get"),),
            ),
            _op(
                "post",
                "/orders",
                contract=(_proj("contract", "fact:c-post", path="orders-v1.yaml"),),
            ),
        ),
    )


@pytest.fixture
def api_model_with_duplicate_post() -> ApiModel:
    return ApiModel(
        generator="apiforge 0.1.0",
        operations=(
            _op(
                "post",
                "/orders",
                contract=(_proj("contract", "fact:c-post", path="orders-v1.yaml"),),
                code=(
                    _proj("code", "fact:k-dup-1", line=12),
                    _proj("code", "fact:k-dup-2", line=18),
                ),
            ),
        ),
    )


@pytest.fixture
def api_model_with_dynamic_route() -> ApiModel:
    return ApiModel(
        generator="apiforge 0.1.0",
        operations=(
            _op(
                "post",
                "/orders",
                contract=(_proj("contract", "fact:c-post", path="orders-v1.yaml"),),
            ),
        ),
        diagnostics=(_diag("AF-FASTAPI-DYNAMIC-ROUTE"),),
    )


@pytest.fixture
def api_model_with_code_only_route() -> ApiModel:
    return ApiModel(
        generator="apiforge 0.1.0",
        operations=(_op("delete", "/orders/{order_id}", code=(_proj("code", "fact:k-del"),)),),
    )
