from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class CompanyProfile(BaseModel):
    industry: Optional[str] = Field(None, description="Industry of the company")
    customer_touchpoints: Optional[List[str]] = Field(None, description="Channels used (e.g., email, Zalo, POS)")
    team_size: Optional[Literal["small", "medium", "large"]] = Field(None, description="Size of support team")
    region: Optional[str] = Field(None, description="Region or country of operation")


class AgentInput(BaseModel):
    pain_point: str = Field(..., description="Description of the business problem")
    company_profile: Optional[CompanyProfile] = None
    priority: Optional[Literal["low", "medium", "high"]] = "medium"


class SuggestedSolution(BaseModel):
    feature_name: str
    categories: List[str]
    description: str
    how_it_helps: str
    relevance_score: float
    link: Optional[str] = None


class AgentOutput(BaseModel):
    suggested_solutions: List[SuggestedSolution]