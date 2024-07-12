from fastapi import FastAPI
from app.schemas import RecommendationRequest, RecommendationResponse
from app.services import get_recommendations

# 서버 실행: uvicorn app.main:app --reload
# API 확인: http://127.0.0.1:8000/docs

app = FastAPI()

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(request: RecommendationRequest):
    result = get_recommendations(request.data)
    return RecommendationResponse(result="Test Success!")

