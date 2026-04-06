from datetime import datetime

from pydantic import BaseModel, Field


class RoomCreateRequest(BaseModel):
    title: str
    currency: str = "USD"


class RoomJoinRequest(BaseModel):
    room_code: str


class RoomMoneyRequest(BaseModel):
    amount: float = Field(gt=0)
    note: str | None = None


class RoomRefundDecisionRequest(BaseModel):
    approve: bool
    note: str | None = None


class RoomMessageRequest(BaseModel):
    body: str


class StripeCheckoutRequest(BaseModel):
    amount: float = Field(gt=0)


class StripeCheckoutResponse(BaseModel):
    checkout_url: str
    provider_session_id: str


class RoomListItem(BaseModel):
    room_code: str
    title: str
    status: str
    current_user_role: str
    counterparty_connected: bool
    hold_amount: float
    released_amount: float


class RoomMessageResponse(BaseModel):
    id: str
    sender_id: str
    body: str
    created_at: datetime


class RoomActivityResponse(BaseModel):
    id: str
    event_type: str
    summary: str
    created_at: datetime


class RoomResponse(BaseModel):
    room_code: str
    title: str
    status: str
    currency: str
    client_id: str | None
    freelancer_id: str | None
    current_user_role: str
    hold_amount: float
    released_amount: float
    remaining_hold_amount: float
    refund_status: str
    refund_note: str | None
    messages: list[RoomMessageResponse]
    activities: list[RoomActivityResponse]
