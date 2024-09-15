from typing import List

from pydantic import BaseModel

class RecommendLocationRequest(BaseModel):
    gender: int
    age: int
    income: int
    travelCompanions: int
    travelPreference: int
    newOrFamiliar: int
    comfortVsCost: int
    relaxationVsActivities: int
    knownVsUnknown: int
    photographyImportance: int

class RecommendLocationResponse(BaseModel):
    locationNames: List[str]

