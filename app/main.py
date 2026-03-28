from fastapi import FastAPI
from app.api.routes.query import router

app = FastAPI()
app.include_router(router)