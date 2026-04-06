from pydantic import BaseModel, Field


class DeliverySubmissionRequest(BaseModel):
    message: str
    attachments: list[str] = []


class ApprovalRequest(BaseModel):
    release_amount: float = Field(gt=0)
    note: str | None = None


class MilestoneResponse(BaseModel):
    milestone_id: str
    status: str
    funded_amount: float
    released_amount: float
