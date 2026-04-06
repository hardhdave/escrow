from pydantic import BaseModel


class DisputeCreateRequest(BaseModel):
    reason_code: str
    description: str | None = None


class DisputeResponse(BaseModel):
    dispute_id: str
    milestone_id: str
    status: str
