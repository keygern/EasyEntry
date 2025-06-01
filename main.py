from dotenv import load_dotenv
import os
from db import create_db_and_tables

load_dotenv(override=True)                             

from fastapi import FastAPI                 
from routers import all_routers             


def create_app() -> FastAPI:
    app = FastAPI(title="EasyEntry API", version="0.1.0")

    # Health-check routes
    @app.get("/")
    def read_root():
        return {"status": "ok"}

    @app.head("/", include_in_schema=False)
    def root_head():
        return {"status": "ok"}             # body ignored for HEAD

    # Plug in every router (billing, entry, etc.)
    for r in all_routers:
        app.include_router(r)

    return app

app = create_app()
create_db_and_tables()
