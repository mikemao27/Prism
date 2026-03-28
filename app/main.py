from fastapi import FastAPI
from app.api.routes.query import router
from app.db.session import engine, Base
from app.models import query_log

app = FastAPI()
app.include_router(router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)