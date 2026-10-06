from fastapi import FastAPI
from app.init_db import init_db_and_seed
from app.routers import documents

app = FastAPI(title="Document Search API", version="1.0.0")

init_db_and_seed()

app.include_router(documents.router)