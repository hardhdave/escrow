from datetime import datetime

from pydantic import BaseModel

from app.domain.marketplace.schemas import MilestoneSummary


class ContractListItem(BaseModel):
    id: str
    title: str
    status: str
    currency: str
    current_user_role: str
    counterparty_id: str
    counterparty_role: str
    message_count: int


class MessageCreateRequest(BaseModel):
    body: str


class ContractStateRequest(BaseModel):
    reason: str | None = None


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    message_type: str
    body: str
    created_at: datetime
    seen_by_other_party: bool


class ActivityResponse(BaseModel):
    id: str
    actor_id: str | None
    event_type: str
    summary: str
    created_at: datetime


class ContractRoomResponse(BaseModel):
    id: str
    title: str
    status: str
    currency: str
    client_id: str
    freelancer_id: str
    current_user_role: str
    milestones: list[MilestoneSummary]
    messages: list[MessageResponse]
    activities: list[ActivityResponse]
