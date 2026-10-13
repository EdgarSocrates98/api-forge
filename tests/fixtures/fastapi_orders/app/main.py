from fastapi import FastAPI

from app.routes.orders import router

app = FastAPI()

app.include_router(router, prefix="/v1")
