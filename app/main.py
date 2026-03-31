from fastapi import FastAPI
from app.api.routes.query import router
from app.db.session import engine, Base
from app.models import query_log
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
app.include_router(router)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
