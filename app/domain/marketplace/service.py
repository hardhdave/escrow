from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain.collaboration.service import record_contract_activity
from app.domain.identity.models import User
from app.domain.identity.schemas import TokenPayload
from app.domain.marketplace.models import Contract, Milestone
from app.domain.marketplace.schemas import ContractCreateRequest, ContractResponse, MilestoneSummary


class ContractService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_contract(self, payload: ContractCreateRequest, token: TokenPayload) -> ContractResponse:
        freelancer = self.db.scalar(select(User).where(User.id == payload.freelancer_id))
        if not freelancer or freelancer.role != "freelancer":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Freelancer account not found")

        contract = Contract(
            client_id=token.sub,
            freelancer_id=payload.freelancer_id,
            title=payload.title,
            currency=payload.currency,
            status="active",
        )
        self.db.add(contract)
        self.db.flush()

        milestones: list[Milestone] = []
        for index, item in enumerate(payload.milestones, start=1):
            milestone = Milestone(
                contract_id=contract.id,
                title=item.title,
                description=item.description,
                amount=item.amount,
                sequence_no=index,
            )
            self.db.add(milestone)
            milestones.append(milestone)

        record_contract_activity(self.db, contract.id, "contract_created", "Contract room created and shared with both parties.", token.sub)
        self.db.commit()
        return ContractResponse(
            id=contract.id,
            title=contract.title,
            status=contract.status,
            currency=contract.currency,
            milestones=[
                MilestoneSummary(
                    id=m.id,
                    title=m.title,
                    amount=float(m.amount),
                    status=m.status,
                    funded_amount=float(m.funded_amount),
                    released_amount=float(m.released_amount),
                )
                for m in milestones
            ],
        )

    def list_visible_contracts(self, token: TokenPayload) -> list[Contract]:
        return self.db.scalars(
            select(Contract).where(or_(Contract.client_id == token.sub, Contract.freelancer_id == token.sub))
        ).all()
