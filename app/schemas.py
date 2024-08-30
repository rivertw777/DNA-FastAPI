from typing import List

from pydantic import BaseModel

class RecommendLocationRequest(BaseModel):
    activities: int
    visitTypes: int
    incomeRanges: int
    preferenceTypes: int
    tripCount: int
    accommodationPreference: int
    workationGoals: int
    relaxationExperience: int
    photoImportance: int

class RecommendLocationResponse(BaseModel):
    locationNames: List[str]