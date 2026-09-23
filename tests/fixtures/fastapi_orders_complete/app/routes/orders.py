from fastapi import APIRouter

router = APIRouter(prefix="/orders")


@router.get("")
def list_orders() -> list[dict[str, str]]:
    return []


@router.post("")
def create_order() -> dict[str, str]:
    return {"status": "created"}


@router.get("/{order_id}")
def get_order(order_id: str) -> dict[str, str]:
    return {"id": order_id}
