from pydantic import BaseModel

class RecommendationRequest(BaseModel):
    data: int

class RecommendationResponse(BaseModel):
    result: str