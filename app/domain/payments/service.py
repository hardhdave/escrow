from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.collaboration.service import record_contract_activity
from app.domain.identity.schemas import TokenPayload
from app.domain.marketplace.models import Contract, Milestone
from app.domain.payments.models import PaymentIntent
from app.domain.payments.schemas import FundMilestoneRequest, PaymentIntentResponse


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def fund_milestone(
        self, milestone_id: str, payload: FundMilestoneRequest, token: TokenPayload
    ) -> PaymentIntentResponse:
        milestone = self.db.scalar(select(Milestone).where(Milestone.id == milestone_id))
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        contract = self.db.scalar(select(Contract).where(Contract.id == milestone.contract_id))
        if not contract or contract.client_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to fund milestone")

        existing = self.db.scalar(
            select(PaymentIntent).where(PaymentIntent.idempotency_key == payload.idempotency_key)
        )
        if existing:
            return PaymentIntentResponse(
                payment_intent_id=existing.id,
                status=existing.status,
                provider=existing.provider,
            )

        final_status = "succeeded" if payload.provider == "manual" else "processing"
        payment_intent = PaymentIntent(
            milestone_id=milestone.id,
            user_id=token.sub,
            provider=payload.provider,
            amount=float(milestone.amount),
            currency=contract.currency,
            idempotency_key=payload.idempotency_key,
            status=final_status,
        )
        milestone.status = "funded" if final_status == "succeeded" else "funding"
        if final_status == "succeeded":
            milestone.funded_amount = float(milestone.amount)
            record_contract_activity(
                self.db,
                contract.id,
                "milestone_funded",
                f"Milestone '{milestone.title}' was funded in escrow.",
                token.sub,
            )
        self.db.add(payment_intent)
        self.db.commit()
        self.db.refresh(payment_intent)

        return PaymentIntentResponse(
            payment_intent_id=payment_intent.id,
            status=payment_intent.status,
            provider=payment_intent.provider,
        )
