from fastapi import FastAPI
from routers import all_routers
from dotenv import load_dotenv
load_dotenv()

def create_app() -> FastAPI:
    app = FastAPI(title="EasyEntry API", version="0.1.0")
    
    @app.get("/") # Health-check
    def read_root():
        return {"status": "ok"}
    
    for r in all_routers:
        app.include_router(r)
    return app

app = create_app()
