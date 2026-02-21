from fastapi import FastAPI

from src.api.v1 import routes

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(routes.router)
