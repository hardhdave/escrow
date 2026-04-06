from pydantic import BaseModel


class FundMilestoneRequest(BaseModel):
    provider: str = "manual"
    payment_method_id: str | None = None
    idempotency_key: str


class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    status: str
    provider: str
