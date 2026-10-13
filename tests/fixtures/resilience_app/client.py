import requests
from tenacity import retry, wait_fixed


@retry(wait=wait_fixed(1))
def fetch_orders():
    return requests.get("https://api.internal/orders")
