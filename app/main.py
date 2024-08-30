import uvicorn
from fastapi import FastAPI
from app.schemas import RecommendLocationRequest, RecommendLocationResponse
from app.services import get_recommendations

# 서버 실행: uvicorn app.main:app --reload
# API 확인: http://127.0.0.1:8000/docs

app = FastAPI()

@app.post("/recommend", response_model=RecommendLocationResponse)
def recommend(request: RecommendLocationRequest):
    return get_recommendations(request)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)