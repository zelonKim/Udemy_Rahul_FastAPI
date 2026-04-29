from contextlib import asynccontextmanager
from fastapi import FastAPI
from rich import print, panel


@asynccontextmanager
async def lifespan_handler(app: FastAPI):
    print(panel.Panel("Server is started...", border_style="green"))
    yield
    print(panel.Panel("Server is stopped...", border_style="red"))


app = FastAPI(lifespan=lifespan_handler)


@app.get("/")
def read_root():
    return {"detail": "Server is running"}
