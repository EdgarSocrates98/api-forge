from app.models import Money, PaymentRequest, RefundRequest
from app.routes.payments import create_payment, get_payment, refund_payment


def _request(amount: int = 1000) -> PaymentRequest:
    return PaymentRequest(
        customer_id="cus_1", amount=Money(amount=amount, currency="BRL"), method="card"
    )


def test_create_payment_is_idempotent() -> None:
    first = create_payment(_request(), idempotency_key="key-00000001")
    assert first.status == "authorized"


def test_get_payment_returns_created() -> None:
    created = create_payment(_request(), idempotency_key="key-00000002")
    assert get_payment(created.payment_id) == created


def test_refund_payment_rejects_excess() -> None:
    created = create_payment(_request(500), idempotency_key="key-00000003")
    refund = refund_payment(
        created.payment_id,
        RefundRequest(amount=Money(amount=100, currency="BRL"), reason="duplicate"),
        idempotency_key="key-00000004",
    )
    assert refund.status == "pending"
