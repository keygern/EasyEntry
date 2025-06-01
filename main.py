# easyentry/main.py
from dotenv import load_dotenv
load_dotenv(override=True)                      # load .env first

from fastapi import FastAPI
from routers import all_routers
from db import create_db_and_tables             # import after .env loaded

def create_app() -> FastAPI:
    app = FastAPI(title="EasyEntry API", version="0.1.0")

    @app.get("/")
    async def root() -> dict:
        return {"status": "ok"}

    # include feature routers
    for r in all_routers:
        app.include_router(r)

    @app.on_event("startup")
    def _init_db() -> None:
        create_db_and_tables()                  # run once on startup

    return app

app = create_app()
