from pathlib import Path

import pytest

from apiforge.context.gateway.canonical import dumps
from apiforge.context.gateway.capsule import build_capsule, emit, expand_ref
from apiforge.context.gateway.errors import GatewayError
from apiforge.context.gateway.refs import CtxStore
from tests.context.gateway_support import analyzed_root


@pytest.fixture(scope="module")
def fastapi_root(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return analyzed_root(tmp_path_factory.mktemp("capsule"), "fastapi")


def _labels(capsule) -> set[str]:
    return {ref.label for ref in capsule.refs}


def test_capsule_selects_operation_schemas_handler_and_tests(fastapi_root: Path) -> None:
    capsule = build_capsule(fastapi_root, "POST /payments")
    assert capsule.status == "ready"
    assert capsule.budget.reached_level == "L3"
    labels = _labels(capsule)
    assert {"operation:POST /payments", "schema:PaymentRequest", "schema:Money"} <= labels
    assert "handler:create_payment" in labels
    assert "test:test_payments.py" in labels
    assert "handler:get_customer" not in labels
    assert capsule.unresolved == ()
    assert all(ref.uri.startswith("ctx://sha256/") for ref in capsule.refs)


def test_capsule_is_byte_identical_across_builds(fastapi_root: Path) -> None:
    first = build_capsule(fastapi_root, "POST /payments")
    second = build_capsule(fastapi_root, "post:/payments")
    assert dumps(emit(first)) == dumps(emit(second))
    assert first.capsule_id == second.capsule_id


def test_schema_is_carried_once_and_code_model_as_delta(fastapi_root: Path) -> None:
    capsule = build_capsule(fastapi_root, "POST /payments")
    schemas = [ref for ref in capsule.refs if ref.label == "schema:PaymentRequest"]
    model = next(ref for ref in capsule.refs if ref.label == "model:PaymentRequest")
    assert len(schemas) == 1
    assert model.parity is False
    assert model.delta == {"missing": ("idempotency_key",)}
    money = next(ref for ref in capsule.refs if ref.label == "model:Money")
    assert money.parity is True


def test_expand_returns_verified_content(fastapi_root: Path) -> None:
    capsule = build_capsule(fastapi_root, "POST /payments")
    handler = next(ref for ref in capsule.refs if ref.label == "handler:create_payment")
    expansion = expand_ref(fastapi_root, handler.uri, run_id=capsule.run_id)
    assert expansion["verified"] is True
    assert "def create_payment" in expansion["content"]
    assert "def get_payment" not in expansion["content"]
    assert expansion["label"] == "handler:create_payment"


def test_budget_exhaustion_returns_whole_refs_and_refusal(fastapi_root: Path) -> None:
    capsule = build_capsule(fastapi_root, "POST /payments", budget_bytes=1600)
    assert capsule.status == "unresolved"
    assert capsule.budget.reached_level == "L2"
    assert capsule.refusals[0].code == "AF-CONTEXT-BUDGET-EXHAUSTED"
    assert capsule.refusals[0].field == "budget_bytes"
    assert capsule.budget.serialized_bytes <= 1600
    store = CtxStore(fastapi_root)
    assert all(store.exists(ref.uri) for ref in capsule.refs)


def test_level_l4_inlines_focused_handler_code(fastapi_root: Path) -> None:
    capsule = build_capsule(fastapi_root, "POST /payments", max_level="L4")
    handler = next(ref for ref in capsule.refs if ref.label == "handler:create_payment")
    assert capsule.budget.reached_level == "L4"
    assert handler.level == "L4"
    assert handler.excerpt is not None and "idempotency conflict" in handler.excerpt


def test_missing_case_degrades_explicitly(tmp_path: Path) -> None:
    capsule = build_capsule(tmp_path, "POST /payments")
    assert capsule.status == "degraded"
    assert capsule.refs == ()
    assert capsule.refusals[0].code == "AF-CTX-GRAPH-UNAVAILABLE"
    assert capsule.budget.reached_level in {"L0", "L1"}
    assert "graph-unavailable" in capsule.unresolved


def test_unknown_operation_is_refused(fastapi_root: Path) -> None:
    with pytest.raises(GatewayError) as error:
        build_capsule(fastapi_root, "DELETE /payments")
    assert error.value.code == "AF-CONTEXT-TARGET-NOT-FOUND"


def test_malformed_target_is_refused(fastapi_root: Path) -> None:
    with pytest.raises(GatewayError) as error:
        build_capsule(fastapi_root, "payments")
    assert error.value.code == "AF-CONTEXT-TARGET-INVALID"


def test_spring_handler_span_ignores_braces_inside_annotations(tmp_path: Path) -> None:
    root = analyzed_root(tmp_path, "spring")
    capsule = build_capsule(root, "POST /payments/{payment_id}/refunds")
    handler = next(ref for ref in capsule.refs if ref.label == "handler:refund")
    content = CtxStore(root).get(handler.uri)
    assert "refund exceeds payment" in content
    assert "private String authorize" not in content
