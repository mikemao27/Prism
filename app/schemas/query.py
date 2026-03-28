from pydantic import BaseModel, Field
from typing import Optional

# Given that we are defining a user query schema, we should instantiate this as a class.
class QueryRequest(BaseModel):
    query: str = Field(..., description="User's Query.")
    constraints: Optional[dict] = Field(default=None, description="Optional Constraints for the Query.")

class QueryResponse(BaseModel):
    response: str = Field(..., description="Response to User Query.")
    model_used: str = Field(..., description="LLM Used to Generate Response.")
    latency: float = Field(..., description="Latency for Response Generation in Milliseconds.")
    estimated_cost: float = Field(..., description="Estimated Cost for Query.")