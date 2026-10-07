from fastapi import APIRouter

router = APIRouter(prefix="/orders")


@router.get("")
def list_orders():
    return []


@router.post("")
def create_order():
    return {}


@router.delete("/{order_id}")
def delete_order(order_id: str):
    return {}
