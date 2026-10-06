from fastapi import FastAPI

app = FastAPI()


@app.post("/authorize")
def authorize() -> dict:
    return {}
