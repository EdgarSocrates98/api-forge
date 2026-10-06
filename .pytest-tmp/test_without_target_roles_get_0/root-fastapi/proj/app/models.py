from pydantic import BaseModel, Field


class Money(BaseModel):
    amount: int = Field(ge=0)
    currency: str = Field(pattern="^[A-Z]{3}$")


class PaymentRequest(BaseModel):
    customer_id: str
    amount: Money
    method: str
    description: str | None = None


class Payment(BaseModel):
    payment_id: str
    status: str
    amount: Money
    created_at: str | None = None


class PaymentPage(BaseModel):
    items: list[Payment]
    next_cursor: str | None = None


class RefundRequest(BaseModel):
    amount: Money
    reason: str


class Refund(BaseModel):
    refund_id: str
    payment_id: str
    status: str
    amount: Money | None = None


class Customer(BaseModel):
    customer_id: str
    email: str
    segment: str | None = None
