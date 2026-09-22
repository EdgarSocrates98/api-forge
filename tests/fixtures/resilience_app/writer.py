import httpx
from tenacity import retry


@retry
def create_order(payload):
    httpx.post("https://api.internal/orders", json=payload, timeout=2.0)
