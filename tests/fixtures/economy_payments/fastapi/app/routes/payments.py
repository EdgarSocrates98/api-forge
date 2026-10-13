from app.models import Payment, PaymentPage, PaymentRequest, Refund, RefundRequest
from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/payments")

_STORE: dict[str, Payment] = {}
_SEEN_KEYS: dict[str, str] = {}


def _authorize(request: PaymentRequest) -> str:
    if request.amount.amount <= 0:
        raise HTTPException(status_code=422, detail="amount must be positive")
    if request.method not in {"card", "pix", "boleto"}:
        raise HTTPException(status_code=422, detail="unsupported method")
    return "authorized" if request.method == "card" else "pending"


@router.get("")
def list_payments(cursor: str | None = None, limit: int = 20) -> PaymentPage:
    items = sorted(_STORE.values(), key=lambda item: item.payment_id)
    start = int(cursor or 0)
    page = items[start : start + min(limit, 100)]
    next_cursor = str(start + len(page)) if start + len(page) < len(items) else None
    return PaymentPage(items=page, next_cursor=next_cursor)


@router.post("", status_code=201)
def create_payment(
    request: PaymentRequest, idempotency_key: str = Header(alias="Idempotency-Key")
) -> Payment:
    if idempotency_key in _SEEN_KEYS:
        raise HTTPException(status_code=409, detail="idempotency conflict")
    payment_id = f"pay_{len(_STORE) + 1:06d}"
    payment = Payment(payment_id=payment_id, status=_authorize(request), amount=request.amount)
    _STORE[payment_id] = payment
    _SEEN_KEYS[idempotency_key] = payment_id
    return payment


@router.get("/{payment_id}")
def get_payment(payment_id: str) -> Payment:
    payment = _STORE.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="payment not found")
    return payment


@router.post("/{payment_id}/refunds", status_code=201)
def refund_payment(
    payment_id: str,
    request: RefundRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
) -> Refund:
    payment = _STORE.get(payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="payment not found")
    if request.amount.amount > payment.amount.amount:
        raise HTTPException(status_code=422, detail="refund exceeds payment")
    return Refund(
        refund_id=f"ref_{idempotency_key[:8]}",
        payment_id=payment_id,
        status="pending",
        amount=request.amount,
    )
