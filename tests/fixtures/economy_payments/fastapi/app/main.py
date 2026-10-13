from app.routes import customers, payments
from fastapi import FastAPI

app = FastAPI(title="Payments API")
app.include_router(payments.router)
app.include_router(customers.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
