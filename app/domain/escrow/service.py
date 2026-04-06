from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.collaboration.service import record_contract_activity
from app.domain.escrow.schemas import ApprovalRequest, DeliverySubmissionRequest, MilestoneResponse
from app.domain.identity.schemas import TokenPayload
from app.domain.marketplace.models import Contract, Milestone


class EscrowService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def submit_delivery(
        self, milestone_id: str, payload: DeliverySubmissionRequest, token: TokenPayload
    ) -> MilestoneResponse:
        milestone = self.db.scalar(select(Milestone).where(Milestone.id == milestone_id))
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        contract = self.db.scalar(select(Contract).where(Contract.id == milestone.contract_id))
        if not contract or contract.freelancer_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to submit delivery")

        milestone.status = "submitted"
        record_contract_activity(
            self.db,
            contract.id,
            "delivery_submitted",
            f"Freelancer submitted delivery for milestone '{milestone.title}'.",
            token.sub,
        )
        self.db.commit()
        return MilestoneResponse(
            milestone_id=milestone.id,
            status=milestone.status,
            funded_amount=float(milestone.funded_amount),
            released_amount=float(milestone.released_amount),
        )

    def approve_milestone(self, milestone_id: str, payload: ApprovalRequest, token: TokenPayload) -> MilestoneResponse:
        milestone = self.db.scalar(select(Milestone).where(Milestone.id == milestone_id))
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        contract = self.db.scalar(select(Contract).where(Contract.id == milestone.contract_id))
        if not contract or contract.client_id != token.sub:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to approve milestone")

        remaining = float(milestone.funded_amount) - float(milestone.released_amount)
        if payload.release_amount > remaining:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Release amount exceeds escrow")

        milestone.released_amount = float(milestone.released_amount) + payload.release_amount
        milestone.status = "released" if float(milestone.released_amount) >= float(milestone.funded_amount) else "partially_released"
        record_contract_activity(
            self.db,
            contract.id,
            "milestone_released",
            f"Client released {payload.release_amount:.2f} for milestone '{milestone.title}'.",
            token.sub,
        )
        self.db.commit()
        return MilestoneResponse(
            milestone_id=milestone.id,
            status=milestone.status,
            funded_amount=float(milestone.funded_amount),
            released_amount=float(milestone.released_amount),
        )
