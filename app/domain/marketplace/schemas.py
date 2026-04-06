from pydantic import BaseModel, Field


class MilestoneCreateRequest(BaseModel):
    title: str
    amount: float = Field(gt=0)
    description: str | None = None


class ContractCreateRequest(BaseModel):
    freelancer_id: str
    title: str
    currency: str = "USD"
    milestones: list[MilestoneCreateRequest]


class MilestoneSummary(BaseModel):
    id: str
    title: str
    amount: float
    status: str
    funded_amount: float = 0
    released_amount: float = 0


class ContractResponse(BaseModel):
    id: str
    title: str
    status: str
    currency: str
    milestones: list[MilestoneSummary]
