from typing import List

from pydantic import BaseModel

class RecommendLocationRequest(BaseModel):
    activities: int
    visit_types: int
    income_ranges: int
    preference_types: int
    trip_count: int
    accommodation_preference: int
    workation_goals: int
    relaxation_experience: int
    photo_importance: int

class RecommendLocationResponse(BaseModel):
    output: List[str]