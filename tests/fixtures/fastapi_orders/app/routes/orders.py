from fastapi import APIRouter

router = APIRouter(prefix="/orders")


@router.get("/{order_id}")
def get_order(order_id: str):
    return {"id": order_id}


@router.get("/")
def list_orders():
    return []


@router.post("")
def create_order():
    return {}


@router.post("")
def create_order_again():
    return {}


@router.get(build_path())  # noqa: F821 — intentionally dynamic for extractor tests
def dynamic_route():
    return {}
