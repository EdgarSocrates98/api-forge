from fastapi import APIRouter, FastAPI

app = FastAPI()
router = APIRouter(prefix="/orders")


@router.get("")
def list_orders() -> list[dict[str, str]]:
    return []


app.include_router(router)
