from pydantic import BaseModel

class RecommendLocationRequest(BaseModel):
    input: int

class RecommendLocationResponse(BaseModel):
    output: str