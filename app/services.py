from app.schemas import RecommendLocationResponse

def get_recommendations(input: int):
    return RecommendLocationResponse(output="Test Success!")
