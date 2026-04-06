from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.collaboration.service import record_contract_activity
from app.domain.disputes.models import Dispute
from app.domain.disputes.schemas import DisputeCreateRequest, DisputeResponse
from app.domain.identity.schemas import TokenPayload
from app.domain.marketplace.models import Contract, Milestone


class DisputeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def open_dispute(
        self, milestone_id: str, payload: DisputeCreateRequest, token: TokenPayload
    ) -> DisputeResponse:
        milestone = self.db.scalar(select(Milestone).where(Milestone.id == milestone_id))
        if not milestone:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Milestone not found")

        contract = self.db.scalar(select(Contract).where(Contract.id == milestone.contract_id))
        if not contract or token.sub not in {contract.client_id, contract.freelancer_id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to open dispute")

        dispute = Dispute(
            milestone_id=milestone.id,
            opened_by=token.sub,
            reason_code=payload.reason_code,
            description=payload.description,
            status="open",
        )
        milestone.status = "disputed"
        self.db.add(dispute)
        record_contract_activity(
            self.db,
            contract.id,
            "dispute_opened",
            f"A dispute was opened for milestone '{milestone.title}'.",
            token.sub,
        )
        self.db.commit()
        self.db.refresh(dispute)
        return DisputeResponse(dispute_id=dispute.id, milestone_id=milestone.id, status=dispute.status)
