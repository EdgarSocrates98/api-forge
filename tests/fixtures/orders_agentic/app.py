"""Static Commerce Orders fixture used by the verifier and holdout tests."""

AUTH_REQUIRED = True
IDEMPOTENCY_REQUIRED = True
CURSOR_VALIDATION = True


def create_order(payload: dict[str, object], idempotency_key: str) -> dict[str, object]:
    """Describe the protected create operation without external I/O."""
    if AUTH_REQUIRED and not payload.get("tenant_id"):
        raise ValueError("tenant is required")
    if IDEMPOTENCY_REQUIRED and not idempotency_key:
        raise ValueError("Idempotency-Key is required")
    return {"status": "pending", "idempotency_key": idempotency_key}


def list_orders(cursor: str | None = None) -> list[dict[str, object]]:
    """Describe cursor-based order listing without external I/O."""
    if CURSOR_VALIDATION and cursor is not None and not cursor.startswith("c_"):
        raise ValueError("invalid cursor")
    return []


def cancel_order(order_id: str, idempotency_key: str) -> dict[str, str]:
    """Describe an idempotent cancellation operation."""
    return {"order_id": order_id, "status": "cancelled", "Idempotency-Key": idempotency_key}
