from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.collaboration.models import ActivityEvent, ContractMessage, ContractReadState
from app.domain.collaboration.schemas import (
    ActivityResponse,
    ContractListItem,
    ContractRoomResponse,
    ContractStateRequest,
    MessageCreateRequest,
    MessageResponse,
)
from app.domain.identity.schemas import TokenPayload
from app.domain.marketplace.models import Contract, Milestone
from app.domain.marketplace.schemas import MilestoneSummary


class CollaborationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_contracts(self, token: TokenPayload) -> list[ContractListItem]:
        contracts = self.db.scalars(
            select(Contract)
            .where(or_(Contract.client_id == token.sub, Contract.freelancer_id == token.sub))
            .order_by(Contract.created_at.desc())
        ).all()

        items: list[ContractListItem] = []
        for contract in contracts:
            current_user_role = "client" if contract.client_id == token.sub else "freelancer"
            counterparty_id = contract.freelancer_id if current_user_role == "client" else contract.client_id
            counterparty_role = "freelancer" if current_user_role == "client" else "client"
            message_count = self.db.scalar(
                select(func.count()).select_from(ContractMessage).where(ContractMessage.contract_id == contract.id)
            ) or 0
            items.append(
                ContractListItem(
                    id=contract.id,
                    title=contract.title,
                    status=contract.status,
                    currency=contract.currency,
                    current_user_role=current_user_role,
                    counterparty_id=counterparty_id,
                    counterparty_role=counterparty_role,
                    message_count=int(message_count),
                )
            )
        return items

    def get_contract_room(self, contract_id: str, token: TokenPayload) -> ContractRoomResponse:
        contract = self._get_contract_for_participant(contract_id, token.sub)
        self._mark_seen(contract.id, token.sub)
        return self._build_room(contract, token.sub)

    def post_message(self, contract_id: str, payload: MessageCreateRequest, token: TokenPayload) -> MessageResponse:
        contract = self._get_contract_for_participant(contract_id, token.sub)
        message = ContractMessage(contract_id=contract.id, sender_id=token.sub, body=payload.body.strip(), message_type="user")
        if not message.body:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message body is required")

        self.db.add(message)
        self.db.flush()
        record_contract_activity(self.db, contract.id, "message_posted", "A new message was posted in the contract room.", token.sub)
        self.db.commit()
        self.db.refresh(message)
        return self._message_to_response(message, contract, token.sub)

    def pause_contract(self, contract_id: str, payload: ContractStateRequest, token: TokenPayload) -> ContractRoomResponse:
        contract = self._get_contract_for_participant(contract_id, token.sub)
        contract.status = "paused"
        reason = payload.reason or "Work was paused for coordination."
        record_contract_activity(self.db, contract.id, "contract_paused", reason, token.sub)
        self.db.commit()
        return self._build_room(contract, token.sub)

    def resume_contract(self, contract_id: str, payload: ContractStateRequest, token: TokenPayload) -> ContractRoomResponse:
        contract = self._get_contract_for_participant(contract_id, token.sub)
        contract.status = "active"
        reason = payload.reason or "Work resumed."
        record_contract_activity(self.db, contract.id, "contract_resumed", reason, token.sub)
        self.db.commit()
        return self._build_room(contract, token.sub)

    def _get_contract_for_participant(self, contract_id: str, user_id: str) -> Contract:
        contract = self.db.scalar(select(Contract).where(Contract.id == contract_id))
        if not contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
        if user_id not in {contract.client_id, contract.freelancer_id}:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access contract")
        return contract

    def _build_room(self, contract: Contract, user_id: str) -> ContractRoomResponse:
        messages = self.db.scalars(
            select(ContractMessage).where(ContractMessage.contract_id == contract.id).order_by(ContractMessage.created_at.asc())
        ).all()
        activities = self.db.scalars(
            select(ActivityEvent).where(ActivityEvent.contract_id == contract.id).order_by(ActivityEvent.created_at.desc())
        ).all()
        milestones = self.db.scalars(
            select(Milestone).where(Milestone.contract_id == contract.id).order_by(Milestone.sequence_no.asc())
        ).all()
        current_user_role = "client" if contract.client_id == user_id else "freelancer"
        return ContractRoomResponse(
            id=contract.id,
            title=contract.title,
            status=contract.status,
            currency=contract.currency,
            client_id=contract.client_id,
            freelancer_id=contract.freelancer_id,
            current_user_role=current_user_role,
            milestones=[
                MilestoneSummary(
                    id=item.id,
                    title=item.title,
                    amount=float(item.amount),
                    status=item.status,
                    funded_amount=float(item.funded_amount),
                    released_amount=float(item.released_amount),
                )
                for item in milestones
            ],
            messages=[self._message_to_response(item, contract, user_id) for item in messages],
            activities=[
                ActivityResponse(
                    id=item.id,
                    actor_id=item.actor_id,
                    event_type=item.event_type,
                    summary=item.summary,
                    created_at=item.created_at,
                )
                for item in activities
            ],
        )

    def _message_to_response(self, message: ContractMessage, contract: Contract, user_id: str) -> MessageResponse:
        other_party_id = contract.freelancer_id if message.sender_id == contract.client_id else contract.client_id
        other_read_state = self.db.scalar(
            select(ContractReadState).where(
                ContractReadState.contract_id == contract.id,
                ContractReadState.user_id == other_party_id,
            )
        )
        seen_by_other_party = bool(other_read_state and other_read_state.last_seen_at >= message.created_at)
        return MessageResponse(
            id=message.id,
            sender_id=message.sender_id,
            message_type=message.message_type,
            body=message.body,
            created_at=message.created_at,
            seen_by_other_party=seen_by_other_party,
        )

    def _mark_seen(self, contract_id: str, user_id: str) -> None:
        read_state = self.db.scalar(
            select(ContractReadState).where(
                ContractReadState.contract_id == contract_id,
                ContractReadState.user_id == user_id,
            )
        )
        if not read_state:
            read_state = ContractReadState(contract_id=contract_id, user_id=user_id)
            self.db.add(read_state)
        read_state.last_seen_at = datetime.now(timezone.utc)
        self.db.commit()


def record_contract_activity(db: Session, contract_id: str, event_type: str, summary: str, actor_id: str | None = None) -> None:
    db.add(ActivityEvent(contract_id=contract_id, actor_id=actor_id, event_type=event_type, summary=summary))
