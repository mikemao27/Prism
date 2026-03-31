from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime
from app.db.session import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    task_type = Column(String(50), nullable=False)
    model_used = Column(String(100), nullable=False)
    latency_ms = Column(Float, nullable=False)
    estimated_cost = Column(Float, nullable=False)