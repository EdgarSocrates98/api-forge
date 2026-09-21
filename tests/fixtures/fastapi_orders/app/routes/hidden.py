from fastapi import APIRouter

hidden = APIRouter()


@hidden.get("/secret")
def secret():
    return {}
