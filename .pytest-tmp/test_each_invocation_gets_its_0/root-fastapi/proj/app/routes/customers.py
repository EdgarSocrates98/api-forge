from app.models import Customer
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/customers")

_CUSTOMERS = {"cus_1": Customer(customer_id="cus_1", email="a@example.com", segment="retail")}


@router.get("/{customer_id}")
def get_customer(customer_id: str) -> Customer:
    customer = _CUSTOMERS.get(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="customer not found")
    return customer
